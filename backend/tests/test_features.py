import numpy as np
import pandas as pd
import pytest

from app.services.features import (
    APPROVED_MODEL_FEATURES,
    FeatureLeakageError,
    create_binary_target,
    create_model_feature_table,
    validate_no_leakage_features,
)
from app.services.preprocessing import build_preprocessing_pipeline, create_train_test_split, prepare_model_data


def make_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "campaign_id": [916, 916, 936, 936, 1178, 1178, 1178, 916],
            "age": ["30-34", "30-34", "35-39", "35-39", "40-44", "40-44", "45-49", "45-49"],
            "gender": ["M", "F", "M", "F", "M", "F", "M", "F"],
            "interest": [15, 16, 20, 21, 22, 23, 24, 25],
            "impressions": [1000, 1200, 900, 1500, 2500, 3000, 800, 1100],
            "clicks": [10, 0, 12, 15, 20, 21, 1, 2],
            "spend": [25.0, 0.0, 30.0, 45.0, 80.0, 90.0, 5.0, 7.0],
            "leads": [2, 0, 3, 1, 4, 2, 0, 1],
            "purchases": [1, 0, 1, 0, 1, 0, 0, 1],
        }
    )


def test_target_is_created_from_purchases() -> None:
    target = create_binary_target(make_dataframe())

    assert target.name == "converted"
    assert target.tolist() == [1, 0, 1, 0, 1, 0, 0, 1]


def test_purchase_greater_than_zero_has_target_one() -> None:
    target = create_binary_target(pd.DataFrame({"purchases": [2]}))

    assert target.iloc[0] == 1


def test_zero_purchases_has_target_zero() -> None:
    target = create_binary_target(pd.DataFrame({"purchases": [0]}))

    assert target.iloc[0] == 0


def test_prohibited_leakage_columns_are_rejected() -> None:
    with pytest.raises(FeatureLeakageError, match="Target leakage risk"):
        validate_no_leakage_features(["campaign_id", "age", "purchases", "estimated_ROAS", "CAC"])


def test_approved_features_are_accepted() -> None:
    validate_no_leakage_features(APPROVED_MODEL_FEATURES)

    table = create_model_feature_table(make_dataframe())

    assert list(table.features.columns) == APPROVED_MODEL_FEATURES


def test_missing_values_are_processed_by_preprocessing_pipeline() -> None:
    dataframe = make_dataframe()
    dataframe.loc[0, "age"] = np.nan
    dataframe.loc[1, "impressions"] = np.nan
    table = create_model_feature_table(dataframe)
    pipeline = build_preprocessing_pipeline()

    transformed = pipeline.fit_transform(table.features)

    assert transformed.shape[0] == len(dataframe)
    assert not np.isnan(transformed).any()


def test_unknown_categorical_values_are_handled() -> None:
    table = create_model_feature_table(make_dataframe())
    pipeline = build_preprocessing_pipeline()
    pipeline.fit(table.features)
    unknown = table.features.head(1).copy()
    unknown.loc[unknown.index[0], "age"] = "65+"
    unknown.loc[unknown.index[0], "gender"] = "X"

    transformed = pipeline.transform(unknown)

    assert transformed.shape[0] == 1


def test_split_preserves_both_classes_where_possible() -> None:
    table = create_model_feature_table(make_dataframe())
    split = create_train_test_split(table.features, table.target)

    assert split.used_stratification is True
    assert split.class_distribution.total == {0: 4, 1: 4}
    assert split.class_distribution.train == {0: 3, 1: 3}
    assert split.class_distribution.test == {0: 1, 1: 1}


def test_original_validated_dataframe_is_not_mutated() -> None:
    dataframe = make_dataframe()
    original = dataframe.copy(deep=True)

    create_model_feature_table(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)


def test_prepare_model_data_reports_mvp_mid_campaign_context() -> None:
    prepared = prepare_model_data(make_dataframe())

    assert prepared.metadata.model_type == "Mid-campaign optimisation model"
    assert prepared.metadata.train_fraction == 0.75
    assert prepared.metadata.test_fraction == 0.25
    assert any("not a pre-launch prediction model" in note for note in prepared.metadata.notes)
    assert any("time-based split is not possible" in note for note in prepared.metadata.notes)

