from dataclasses import dataclass
from typing import Iterable

import pandas as pd


TARGET_COLUMN = "converted"

APPROVED_MODEL_FEATURES = [
    "campaign_id",
    "age",
    "gender",
    "interest",
    "impressions",
    "clicks",
    "spend",
]

CATEGORICAL_MODEL_FEATURES = [
    "campaign_id",
    "age",
    "gender",
    "interest",
]

NUMERICAL_MODEL_FEATURES = [
    "impressions",
    "clicks",
    "spend",
]

PROHIBITED_LEAKAGE_FEATURES = [
    "purchases",
    "leads",
    "approved_conversion",
    "total_conversion",
    "purchase_conversion_rate",
    "cost_per_lead",
    "cac",
    "estimated_revenue",
    "estimated_profit",
    "estimated_roas",
    "estimated_romi",
]

PREDICTION_QUESTION = "Will an active advertising segment generate at least one approved conversion?"
MODEL_POSITIONING = "Mid-campaign optimisation model"
MODEL_SCOPE_NOTE = (
    "This is a mid-campaign optimisation model because impressions, clicks, and spend become "
    "available while the campaign is active. It is not a pre-launch prediction model."
)
SPLIT_LIMITATION_NOTE = (
    "The dataset contains no campaign dates, so a time-based split is not possible. "
    "The current stratified split is for MVP evaluation only."
)


class FeatureLeakageError(ValueError):
    pass


class FeatureTableError(ValueError):
    pass


@dataclass(frozen=True)
class ModelFeatureTable:
    features: pd.DataFrame
    target: pd.Series


def create_binary_target(dataframe: pd.DataFrame) -> pd.Series:
    if "purchases" not in dataframe.columns:
        raise FeatureTableError("Cannot create target because required column 'purchases' is missing.")

    purchases = pd.to_numeric(dataframe["purchases"], errors="coerce").fillna(0)
    return (purchases > 0).astype(int).rename(TARGET_COLUMN)


def validate_no_leakage_features(columns: Iterable[str]) -> None:
    normalized_columns = {_normalize_feature_name(column): column for column in columns}
    normalized_prohibited = {_normalize_feature_name(column): column for column in PROHIBITED_LEAKAGE_FEATURES}
    leaked = [
        normalized_columns[column]
        for column in normalized_columns
        if column in normalized_prohibited
    ]

    if leaked:
        leaked_list = ", ".join(sorted(leaked))
        raise FeatureLeakageError(
            "Target leakage risk detected. Remove prohibited model input column(s): "
            f"{leaked_list}."
        )


def create_model_feature_table(dataframe: pd.DataFrame) -> ModelFeatureTable:
    missing_features = [column for column in APPROVED_MODEL_FEATURES if column not in dataframe.columns]
    if missing_features:
        raise FeatureTableError(f"Missing approved model feature column(s): {', '.join(missing_features)}.")

    validate_no_leakage_features(APPROVED_MODEL_FEATURES)

    target = create_binary_target(dataframe)
    features = dataframe.loc[:, APPROVED_MODEL_FEATURES].copy(deep=True)

    for column in NUMERICAL_MODEL_FEATURES:
        features[column] = pd.to_numeric(features[column], errors="coerce")

    for column in CATEGORICAL_MODEL_FEATURES:
        features[column] = features[column].astype("object")

    return ModelFeatureTable(features=features, target=target)


def _normalize_feature_name(value: str) -> str:
    return value.strip().lower().replace(" ", "_")

