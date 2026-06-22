"""Report download endpoints for CSV and PDF exports."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.config import Settings, get_settings
from app.schemas.analytics import FinancialAssumptions
from app.services.report_service import (
    generate_campaign_summary_csv,
    generate_executive_summary_pdf,
    generate_model_metrics_csv,
    generate_recommendations_csv,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/campaign-summary-csv",
    summary="Download campaign summary as CSV.",
    response_class=Response,
)
def download_campaign_summary_csv(
    assumptions: FinancialAssumptions,
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        content = generate_campaign_summary_csv(assumptions, settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=campaigniq_campaign_summary.csv"},
    )


@router.post(
    "/recommendations-csv",
    summary="Download segment recommendations as CSV.",
    response_class=Response,
)
def download_recommendations_csv(
    assumptions: FinancialAssumptions,
    probability_threshold: Optional[float] = Query(None, ge=0, le=1),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        content = generate_recommendations_csv(assumptions, settings, probability_threshold)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=campaigniq_recommendations.csv"},
    )


@router.get(
    "/model-metrics-csv",
    summary="Download model evaluation metrics as CSV.",
    response_class=Response,
)
def download_model_metrics_csv(
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        content = generate_model_metrics_csv(settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=campaigniq_model_metrics.csv"},
    )


@router.post(
    "/executive-summary-pdf",
    summary="Download executive summary report as PDF.",
    response_class=Response,
)
def download_executive_summary_pdf(
    assumptions: FinancialAssumptions,
    probability_threshold: Optional[float] = Query(None, ge=0, le=1),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        content = generate_executive_summary_pdf(assumptions, settings, probability_threshold)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=campaigniq_executive_summary.pdf"},
    )
