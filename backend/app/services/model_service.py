"""
Model training and comparison service for CampaignIQ.

Model type: Mid-campaign optimisation model.
Prediction: Will an active advertising segment generate at least one approved conversion?

Selection priority: average_precision > f1_score > roc_auc.
Average precision is preferred because it summarises the precision-recall tradeoff across
all thresholds. When classes are imbalanced the positive class is rare, and ROC-AUC can
appear optimistic because it credits true-negative performance. Average precision focuses
only on how well the model ranks positive examples, making it a more honest metric for
imbalanced conversion prediction.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from app.config import get_settings
from app.schemas.model import (
    ClassDistribution,
    ConfusionMatrixValues,
    CurvePoint,
    EvaluationMetrics,
    FeatureImportance,
    ModelMetadata,
    ModelResult,
    TrainingResult,
)
from app.services.features import (
    APPROVED_MODEL_FEATURES,
    MODEL_SCOPE_NOTE,
    PROHIBITED_LEAKAGE_FEATURES,
    SPLIT_LIMITATION_NOTE,
)

# Lazy imports for sklearn/joblib to allow the app to boot on serverless without them
_sklearn_available = None


def _check_sklearn():
    global _sklearn_available
    if _sklearn_available is None:
        try:
            import sklearn  # noqa: F401
            import joblib  # noqa: F401
            _sklearn_available = True
        except ImportError:
            _sklearn_available = False
    return _sklearn_available


def _require_sklearn():
    if not _check_sklearn():
        raise RuntimeError(
            "Model training and prediction require scikit-learn and joblib. "
            "These are not available in the serverless deployment. "
            "Use the local or Docker deployment to train models."
        )


def _get_model_definitions() -> dict:
    _require_sklearn()
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from app.services.preprocessing import RANDOM_STATE
    return {
        "LogisticRegression": lambda: LogisticRegression(
            class_weight="balanced", random_state=RANDOM_STATE, max_iter=1000,
        ),
        "RandomForest": lambda: RandomForestClassifier(
            class_weight="balanced", random_state=RANDOM_STATE, n_estimators=100,
        ),
    }


# Backwards-compatible access for tests
class _LazyModelDefinitions:
    def items(self):
        return _get_model_definitions().items()

    def __getitem__(self, key):
        return _get_model_definitions()[key]

    def __contains__(self, key):
        return key in _get_model_definitions()


_MODEL_DEFINITIONS = _LazyModelDefinitions()


def train_and_compare(dataframe: pd.DataFrame, *, settings=None) -> TrainingResult:
    """Train all models, evaluate, select best, persist artifacts."""
    _require_sklearn()

    from app.services.preprocessing import (
        RANDOM_STATE,
        build_preprocessing_pipeline,
        prepare_model_data,
    )

    if settings is None:
        settings = get_settings()

    model_definitions = _get_model_definitions()

    prepared = prepare_model_data(dataframe)
    split = prepared.split

    results: List[ModelResult] = []
    trained_pipelines: dict = {}

    for name, make_estimator in model_definitions.items():
        pipeline = build_preprocessing_pipeline()
        pipeline.steps.append(("classifier", make_estimator()))
        pipeline.fit(split.x_train, split.y_train)

        y_pred = pipeline.predict(split.x_test)
        y_proba = pipeline.predict_proba(split.x_test)[:, 1]

        metrics = _compute_metrics(split.y_test, y_pred, y_proba)
        importances = _extract_feature_importances(pipeline, name)
        roc_points = _compute_roc_curve(split.y_test, y_proba)
        pr_points = _compute_pr_curve(split.y_test, y_proba)

        results.append(ModelResult(
            model_name=name, metrics=metrics, feature_importances=importances,
            roc_curve=roc_points, precision_recall_curve=pr_points,
        ))
        trained_pipelines[name] = pipeline

    results.sort(key=lambda r: (
        r.metrics.average_precision, r.metrics.f1_score, r.metrics.roc_auc,
    ), reverse=True)

    selected = results[0]
    selected_pipeline = trained_pipelines[selected.model_name]

    metadata = ModelMetadata(
        selected_model_name=selected.model_name,
        training_timestamp=datetime.now(timezone.utc).isoformat(),
        dataset_row_count=len(dataframe),
        training_row_count=len(split.x_train),
        testing_row_count=len(split.x_test),
        target_definition="converted = 1 if purchases > 0 else 0",
        approved_features=APPROVED_MODEL_FEATURES,
        excluded_leakage_features=PROHIBITED_LEAKAGE_FEATURES,
        class_distribution=split.class_distribution,
        evaluation_metrics=selected.metrics,
        random_state=RANDOM_STATE,
        dataset_limitations=[MODEL_SCOPE_NOTE, SPLIT_LIMITATION_NOTE],
    )

    save_model(selected_pipeline, settings.model_artifact_path)
    save_metadata(metadata, settings.model_metadata_path)

    return TrainingResult(
        selected_model=selected.model_name, leaderboard=results, metadata=metadata,
    )


def save_model(pipeline, path: Path) -> None:
    _require_sklearn()
    import joblib
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)


def save_metadata(metadata: ModelMetadata, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata.model_dump(), indent=2), encoding="utf-8")


def load_model(path: Path):
    _require_sklearn()
    import joblib
    return joblib.load(path)


def _compute_metrics(y_true: pd.Series, y_pred: np.ndarray, y_proba: np.ndarray) -> EvaluationMetrics:
    from sklearn.metrics import (
        accuracy_score, average_precision_score, confusion_matrix,
        f1_score, precision_score, recall_score, roc_auc_score,
    )
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return EvaluationMetrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, zero_division=0)),
        f1_score=float(f1_score(y_true, y_pred, zero_division=0)),
        roc_auc=float(roc_auc_score(y_true, y_proba)),
        average_precision=float(average_precision_score(y_true, y_proba)),
        confusion_matrix=ConfusionMatrixValues(
            true_negatives=int(tn), false_positives=int(fp),
            false_negatives=int(fn), true_positives=int(tp),
        ),
    )


def _compute_roc_curve(y_true: pd.Series, y_proba: np.ndarray) -> List[CurvePoint]:
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    return [CurvePoint(x=float(x), y=float(y)) for x, y in zip(fpr, tpr)]


def _compute_pr_curve(y_true: pd.Series, y_proba: np.ndarray) -> List[CurvePoint]:
    from sklearn.metrics import precision_recall_curve
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    return [CurvePoint(x=float(r), y=float(p)) for r, p in zip(recall, precision)]


def _extract_feature_importances(pipeline, model_name: str) -> List[FeatureImportance]:
    feature_names = _get_transformed_feature_names(pipeline)
    classifier = pipeline.named_steps["classifier"]

    if model_name == "LogisticRegression":
        coefficients = classifier.coef_[0]
        importances = []
        for name, coef in zip(feature_names, coefficients):
            importances.append(FeatureImportance(
                feature=_simplify_feature_name(name),
                importance=float(abs(coef)),
                direction="positive" if coef > 0 else "negative",
            ))
        importances.sort(key=lambda x: x.importance, reverse=True)
        return importances

    raw_importances = classifier.feature_importances_
    importances = []
    for name, imp in zip(feature_names, raw_importances):
        importances.append(FeatureImportance(
            feature=_simplify_feature_name(name), importance=float(imp),
        ))
    importances.sort(key=lambda x: x.importance, reverse=True)
    return importances


def _get_transformed_feature_names(pipeline) -> List[str]:
    preprocessor = pipeline.named_steps["preprocessor"]
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        return [f"feature_{i}" for i in range(preprocessor.n_features_in_)]


def _simplify_feature_name(name: str) -> str:
    for prefix in ("numeric__", "categorical__"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name
