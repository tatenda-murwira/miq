from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.dependencies import get_app_settings
from app.schemas.analytics import (
    AudienceAnalyticsResponse,
    CampaignAnalyticsResponse,
    FinancialAssumptions,
    OverviewAnalyticsResponse,
    SensitivityAnalyticsResponse,
)
from app.services.analytics_service import (
    build_audiences,
    build_campaigns,
    build_overview,
    build_sensitivity,
)
from app.services.data_service import DataValidationError

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/overview", response_model=OverviewAnalyticsResponse)
def analytics_overview(
    assumptions: FinancialAssumptions,
    settings: Settings = Depends(get_app_settings),
) -> OverviewAnalyticsResponse:
    try:
        return build_overview(assumptions, settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


@router.post("/campaigns", response_model=CampaignAnalyticsResponse)
def analytics_campaigns(
    assumptions: FinancialAssumptions,
    settings: Settings = Depends(get_app_settings),
) -> CampaignAnalyticsResponse:
    try:
        return build_campaigns(assumptions, settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


@router.post("/audiences", response_model=AudienceAnalyticsResponse)
def analytics_audiences(
    assumptions: FinancialAssumptions,
    settings: Settings = Depends(get_app_settings),
) -> AudienceAnalyticsResponse:
    try:
        return build_audiences(assumptions, settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


@router.post("/sensitivity", response_model=SensitivityAnalyticsResponse)
def analytics_sensitivity(
    assumptions: FinancialAssumptions,
    settings: Settings = Depends(get_app_settings),
) -> SensitivityAnalyticsResponse:
    try:
        return build_sensitivity(assumptions, settings)
    except DataValidationError as exc:
        _raise_http_validation_error(exc)


def _raise_http_validation_error(exc: DataValidationError) -> None:
    detail = {"message": exc.message}
    if exc.report:
        detail["report"] = exc.report.model_dump(mode="json")
    raise HTTPException(status_code=exc.status_code, detail=detail)

