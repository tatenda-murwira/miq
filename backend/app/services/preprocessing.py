from dataclasses import dataclass
from math import ceil

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.schemas.model import ClassDistribution, FeatureEngineeringMetadata
from app.services.features import (
    APPROVED_MODEL_FEATURES,
    CATEGORICAL_MODEL_FEATURES,
    MODEL_POSITIONING,
    MODEL_SCOPE_NOTE,
    NUMERICAL_MODEL_FEATURES,
    PREDICTION_QUESTION,
    PROHIBITED_LEAKAGE_FEATURES,
    SPLIT_LIMITATION_NOTE,
    TARGET_COLUMN,
    ModelFeatureTable,
    create_model_feature_table,
)


RANDOM_STATE = 42
TEST_SIZE = 0.25
TRAIN_SIZE = 0.75


@dataclass(frozen=True)
class ModelSplit:
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    class_distribution: ClassDistribution
    used_stratification: bool


@dataclass(frozen=True)
class PreparedModelData:
    feature_table: ModelFeatureTable
    split: ModelSplit
    preprocessing_pipeline: Pipeline
    metadata: FeatureEngineeringMetadata


def build_column_transformer() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERICAL_MODEL_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_MODEL_FEATURES),
        ],
        remainder="drop",
    )


def build_preprocessing_pipeline() -> Pipeline:
    return Pipeline(steps=[("preprocessor", build_column_transformer())])


def create_train_test_split(
    features: pd.DataFrame,
    target: pd.Series,
    *,
    random_state: int = RANDOM_STATE,
    test_size: float = TEST_SIZE,
) -> ModelSplit:
    stratify = target if _can_stratify(target, test_size=test_size) else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    return ModelSplit(
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        class_distribution=ClassDistribution(
            total=_class_counts(target),
            train=_class_counts(y_train),
            test=_class_counts(y_test),
        ),
        used_stratification=stratify is not None,
    )


def prepare_model_data(dataframe: pd.DataFrame) -> PreparedModelData:
    feature_table = create_model_feature_table(dataframe)
    split = create_train_test_split(feature_table.features, feature_table.target)
    preprocessing_pipeline = build_preprocessing_pipeline()
    metadata = FeatureEngineeringMetadata(
        model_type=MODEL_POSITIONING,
        prediction_question=PREDICTION_QUESTION,
        target_column=TARGET_COLUMN,
        approved_features=APPROVED_MODEL_FEATURES,
        prohibited_leakage_features=PROHIBITED_LEAKAGE_FEATURES,
        train_fraction=TRAIN_SIZE,
        test_fraction=TEST_SIZE,
        random_state=RANDOM_STATE,
        class_distribution=split.class_distribution,
        notes=[
            MODEL_SCOPE_NOTE,
            SPLIT_LIMITATION_NOTE,
            "No final model is trained by this feature-engineering preparation step.",
        ],
    )

    return PreparedModelData(
        feature_table=feature_table,
        split=split,
        preprocessing_pipeline=preprocessing_pipeline,
        metadata=metadata,
    )


def _can_stratify(target: pd.Series, *, test_size: float) -> bool:
    counts = target.value_counts()
    if len(counts) < 2 or counts.min() < 2:
        return False

    test_count = ceil(len(target) * test_size)
    train_count = len(target) - test_count
    class_count = len(counts)

    return test_count >= class_count and train_count >= class_count


def _class_counts(target: pd.Series) -> dict[int, int]:
    counts = target.value_counts().sort_index()
    return {int(label): int(count) for label, count in counts.items()}

