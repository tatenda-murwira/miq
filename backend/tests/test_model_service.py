import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.services.features import FeatureLeakageError, APPROVED_MODEL_FEATURES, PROHIBITED_LEAKAGE_FEATURES
from app.services.model_service import (
    _MODEL_DEFINITIONS,
    load_model,
    save_model,
    save_metadata,
    train_and_compare,
)
from app.services.preprocessing import build_preprocessing_pipeline, RANDOM_STATE, create_train_test_split
from app.services.features import create_model_feature_table


def _make_dataframe(n: int = 80) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "campaign_id": rng.choice([916, 936, 1178], size=n),
        "age": rng.choice(["30-34", "35-39", "40-44", "45-49"], size=n),
        "gender": rng.choice(["M", "F"], size=n),
        "interest": rng.integers(10, 30, size=n),
        "impressions": rng.integers(100, 5000, size=n),
        "clicks": rng.integers(0, 50, size=n),
        "spend": rng.uniform(0, 100, size=n).round(2),
        "purchases": rng.choice([0, 0, 0, 1, 1], size=n),  # imbalanced
    })


def _make_dataframe_with_leakage() -> pd.DataFrame:
    df = _make_dataframe()
    df["leads"] = 5
    return df


class TestBothModelsTrain:
    def test_both_models_train_successfully(self) -> None:
        result = train_and_compare(_make_dataframe())
        model_names = [r.model_name for r in result.leaderboard]
        assert "LogisticRegression" in model_names
        assert "RandomForest" in model_names

    def test_both_models_return_probabilities(self) -> None:
        df = _make_dataframe()
        table = create_model_feature_table(df)
        split = create_train_test_split(table.features, table.target)

        for name, make_est in _MODEL_DEFINITIONS.items():
            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", make_est()))
            pipeline.fit(split.x_train, split.y_train)
            proba = pipeline.predict_proba(split.x_test)
            assert proba.shape[1] == 2, f"{name} should return 2-class probabilities"

    def test_probabilities_between_zero_and_one(self) -> None:
        df = _make_dataframe()
        table = create_model_feature_table(df)
        split = create_train_test_split(table.features, table.target)

        for name, make_est in _MODEL_DEFINITIONS.items():
            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", make_est()))
            pipeline.fit(split.x_train, split.y_train)
            proba = pipeline.predict_proba(split.x_test)[:, 1]
            assert (proba >= 0.0).all() and (proba <= 1.0).all(), f"{name} probabilities out of range"


class TestUnknownCategoricals:
    def test_unknown_categorical_values_do_not_crash(self) -> None:
        df = _make_dataframe()
        table = create_model_feature_table(df)
        split = create_train_test_split(table.features, table.target)

        for name, make_est in _MODEL_DEFINITIONS.items():
            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", make_est()))
            pipeline.fit(split.x_train, split.y_train)

            unknown_row = pd.DataFrame({
                "campaign_id": [99999],
                "age": ["65+"],
                "gender": ["X"],
                "interest": [999],
                "impressions": [1],
                "clicks": [0],
                "spend": [0.01],
            })
            pred = pipeline.predict(unknown_row)
            assert len(pred) == 1


class TestLeakagePrevention:
    def test_leakage_features_cannot_enter_model_features(self) -> None:
        """Verify that validate_no_leakage_features raises if leakage columns
        are passed as model input features (tested at the features layer)."""
        from app.services.features import validate_no_leakage_features
        with pytest.raises(FeatureLeakageError, match="Target leakage risk"):
            validate_no_leakage_features(["campaign_id", "leads", "spend"])

    def test_dataframe_with_extra_columns_trains_without_error(self) -> None:
        """The raw dataframe may contain non-feature columns (e.g. leads).
        Only APPROVED_MODEL_FEATURES are used as model inputs."""
        result = train_and_compare(_make_dataframe_with_leakage())
        assert result.selected_model in ("LogisticRegression", "RandomForest")


class TestModelPersistence:
    def _make_temp_dir(self) -> Path:
        return Path(tempfile.mkdtemp())

    def test_model_can_be_saved(self) -> None:
        tmp = self._make_temp_dir()
        try:
            df = _make_dataframe()
            table = create_model_feature_table(df)
            split = create_train_test_split(table.features, table.target)

            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", _MODEL_DEFINITIONS["LogisticRegression"]()))
            pipeline.fit(split.x_train, split.y_train)

            model_path = tmp / "model.joblib"
            save_model(pipeline, model_path)
            assert model_path.exists()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_saved_model_can_be_loaded(self) -> None:
        tmp = self._make_temp_dir()
        try:
            df = _make_dataframe()
            table = create_model_feature_table(df)
            split = create_train_test_split(table.features, table.target)

            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", _MODEL_DEFINITIONS["RandomForest"]()))
            pipeline.fit(split.x_train, split.y_train)

            model_path = tmp / "model.joblib"
            save_model(pipeline, model_path)
            loaded = load_model(model_path)
            assert loaded is not None
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_loaded_model_generates_predictions(self) -> None:
        tmp = self._make_temp_dir()
        try:
            df = _make_dataframe()
            table = create_model_feature_table(df)
            split = create_train_test_split(table.features, table.target)

            pipeline = build_preprocessing_pipeline()
            pipeline.steps.append(("classifier", _MODEL_DEFINITIONS["LogisticRegression"]()))
            pipeline.fit(split.x_train, split.y_train)

            model_path = tmp / "model.joblib"
            save_model(pipeline, model_path)
            loaded = load_model(model_path)

            predictions = loaded.predict(split.x_test)
            assert len(predictions) == len(split.x_test)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestEvaluationMetrics:
    def test_metrics_have_valid_ranges(self) -> None:
        result = train_and_compare(_make_dataframe())
        for model_result in result.leaderboard:
            m = model_result.metrics
            assert 0.0 <= m.accuracy <= 1.0
            assert 0.0 <= m.precision <= 1.0
            assert 0.0 <= m.recall <= 1.0
            assert 0.0 <= m.f1_score <= 1.0
            assert 0.0 <= m.roc_auc <= 1.0
            assert 0.0 <= m.average_precision <= 1.0
            cm = m.confusion_matrix
            assert cm.true_negatives >= 0
            assert cm.false_positives >= 0
            assert cm.false_negatives >= 0
            assert cm.true_positives >= 0

    def test_feature_importances_present(self) -> None:
        result = train_and_compare(_make_dataframe())
        for model_result in result.leaderboard:
            assert len(model_result.feature_importances) > 0

    def test_leaderboard_ordered_by_average_precision(self) -> None:
        result = train_and_compare(_make_dataframe())
        ap_scores = [r.metrics.average_precision for r in result.leaderboard]
        assert ap_scores == sorted(ap_scores, reverse=True)
