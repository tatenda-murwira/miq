from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import Settings
from app.dependencies import get_app_settings
from app.schemas.data import DataPreviewResponse, DataQualityReport, DataStatusResponse, DataUploadResponse
from app.services.data_service import (
    DataValidationError,
    get_data_status,
    get_dataset_preview,
    get_latest_quality_report,
    load_default_dataset,
    store_uploaded_dataset,
)

router = APIRouter(prefix="/data", tags=["Data"])


@router.get("/status", response_model=DataStatusResponse)
def data_status(settings: Settings = Depends(get_app_settings)) -> DataStatusResponse:
    return get_data_status(settings)


@router.post("/upload", response_model=DataUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_app_settings),
) -> DataUploadResponse:
    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail={"message": "Only CSV uploads are supported."})

    content = await file.read()
    try:
        result = store_uploaded_dataset(content, settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)

    return DataUploadResponse(
        message="Dataset uploaded, validated, and stored.",
        stored=True,
        report=result.report,
    )


@router.post("/use-default", response_model=DataUploadResponse)
def use_default_dataset(settings: Settings = Depends(get_app_settings)) -> DataUploadResponse:
    try:
        result = load_default_dataset(settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)

    return DataUploadResponse(
        message="Default dataset validated and stored for analysis.",
        stored=True,
        report=result.report,
    )


@router.get("/quality", response_model=DataQualityReport)
def data_quality(settings: Settings = Depends(get_app_settings)) -> DataQualityReport:
    try:
        return get_latest_quality_report(settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


@router.get("/preview", response_model=DataPreviewResponse)
def data_preview(settings: Settings = Depends(get_app_settings)) -> DataPreviewResponse:
    try:
        return get_dataset_preview(settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


def _raise_http_validation_error(exc: DataValidationError) -> None:
    detail = {"message": exc.message}
    if exc.report:
        detail["report"] = exc.report.model_dump(mode="json")
    raise HTTPException(status_code=exc.status_code, detail=detail)

