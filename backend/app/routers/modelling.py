"""Model training, evaluation, and prediction endpoints."""

import json

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

import numpy as np

from app.config import Settings, get_settings
from app.schemas.model import (
    FeatureImportance,
    ModelMetadata,
    ModelStatusResponse,
    PredictionRow,
    PredictResponse,
    TrainingResult,
)
from app.schemas.threshold import ThresholdAnalysisResponse, ThresholdAssumptions
from app.services.features import (
    APPROVED_MODEL_FEATURES,
    FeatureLeakageError,
    FeatureTableError,
    create_binary_target,
    create_model_feature_table,
)
from app.services.model_service import load_model, train_and_compare

router = APIRouter(prefix="/model", tags=["model"])

MODEL_VERSION = "1.0.0"


def _load_metadata(settings: Settings) -> ModelMetadata:
    if not settings.model_metadata_path.exists():
        raise HTTPException(status_code=404, detail="No model has been trained yet.")
    raw = json.loads(settings.model_metadata_path.read_text(encoding="utf-8"))
    return ModelMetadata(**raw)


def _load_current_dataset(settings: Settings) -> pd.DataFrame:
    if not settings.current_dataset_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No validated dataset is available. Upload a CSV or use the default dataset first.",
        )
    return pd.read_csv(settings.current_dataset_path)


@router.get(
    "/status",
    response_model=ModelStatusResponse,
    summary="Check whether a trained model exists and its metadata.",
)
def get_model_status(settings: Settings = Depends(get_settings)) -> ModelStatusResponse:
    if not settings.model_metadata_path.exists():
        return ModelStatusResponse(
            model_exists=False,
            selected_model_name=None,
            training_timestamp=None,
            dataset_row_count=None,
            target_definition=None,
            model_version=MODEL_VERSION,
        )
    metadata = _load_metadata(settings)
    return ModelStatusResponse(
        model_exists=True,
        selected_model_name=metadata.selected_model_name,
        training_timestamp=metadata.training_timestamp,
        dataset_row_count=metadata.dataset_row_count,
        target_definition=metadata.target_definition,
        model_version=MODEL_VERSION,
    )


@router.post(
    "/train",
    response_model=TrainingResult,
    summary="Train Logistic Regression and Random Forest, select the best model.",
)
def train_model(settings: Settings = Depends(get_settings)) -> TrainingResult:
    dataframe = _load_current_dataset(settings)
    try:
        return train_and_compare(dataframe, settings=settings)
    except FeatureLeakageError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FeatureTableError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Training failed: {exc}")


@router.get(
    "/results",
    response_model=ModelMetadata,
    summary="Return latest saved model evaluation results without retraining.",
)
def get_model_results(settings: Settings = Depends(get_settings)) -> ModelMetadata:
    return _load_metadata(settings)


@router.get(
    "/feature-importance",
    response_model=list[FeatureImportance],
    summary="Return readable feature importance from the selected trained model.",
)
def get_feature_importance(settings: Settings = Depends(get_settings)) -> list[FeatureImportance]:
    if not settings.model_artifact_path.exists():
        raise HTTPException(status_code=404, detail="No model has been trained yet.")

    pipeline = load_model(settings.model_artifact_path)
    from app.services.model_service import _extract_feature_importances

    metadata = _load_metadata(settings)
    return _extract_feature_importances(pipeline, metadata.selected_model_name)


@router.post(
    "/threshold-analysis",
    response_model=ThresholdAnalysisResponse,
    summary="Evaluate probability thresholds using profit-oriented back-testing on the held-out test set.",
)
def threshold_analysis(
    assumptions: ThresholdAssumptions,
    settings: Settings = Depends(get_settings),
) -> ThresholdAnalysisResponse:
    if not settings.model_artifact_path.exists():
        raise HTTPException(status_code=404, detail="No model has been trained yet.")

    from app.services.preprocessing import create_train_test_split
    from app.services.threshold_service import run_threshold_analysis

    dataframe = _load_current_dataset(settings)
    pipeline = load_model(settings.model_artifact_path)

    table = create_model_feature_table(dataframe)
    split = create_train_test_split(table.features, table.target)

    y_proba = pipeline.predict_proba(split.x_test)[:, 1]
    y_true = split.y_test.values

    # Get actual purchases and spend from the original dataframe for test rows
    test_indices = split.x_test.index
    purchases = dataframe.loc[test_indices, "purchases"].values.astype(float)
    spend = dataframe.loc[test_indices, "spend"].values.astype(float)
    clicks = dataframe.loc[test_indices, "clicks"].values.astype(float)

    return run_threshold_analysis(
        y_true=np.asarray(y_true),
        y_proba=np.asarray(y_proba),
        spend=np.asarray(spend),
        purchases=np.asarray(purchases),
        clicks=np.asarray(clicks),
        assumptions=assumptions,
    )


@router.post(
    "/predict-current",
    response_model=PredictResponse,
    summary="Predict conversion probabilities for every row in the current validated dataset.",
)
def predict_current_dataset(settings: Settings = Depends(get_settings)) -> PredictResponse:
    if not settings.model_artifact_path.exists():
        raise HTTPException(status_code=404, detail="No model has been trained yet.")

    dataframe = _load_current_dataset(settings)
    pipeline = load_model(settings.model_artifact_path)

    features = dataframe[APPROVED_MODEL_FEATURES]
    probabilities = pipeline.predict_proba(features)[:, 1]
    predictions = pipeline.predict(features)
    target = create_binary_target(dataframe)

    rows = []
    for i in range(len(dataframe)):
        rows.append(PredictionRow(
            ad_id=int(dataframe.iloc[i].get("ad_id", 0)),
            campaign_id=int(dataframe.iloc[i]["campaign_id"]),
            age=str(dataframe.iloc[i]["age"]),
            gender=str(dataframe.iloc[i]["gender"]),
            interest=int(dataframe.iloc[i]["interest"]),
            impressions=int(dataframe.iloc[i]["impressions"]),
            clicks=int(dataframe.iloc[i]["clicks"]),
            spend=float(dataframe.iloc[i]["spend"]),
            actual_converted=int(target.iloc[i]),
            conversion_probability=float(probabilities[i]),
            predicted_class=int(predictions[i]),
        ))

    return PredictResponse(row_count=len(rows), predictions=rows)
