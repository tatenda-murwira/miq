"""Recommendation generation endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import generate_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post(
    "/generate",
    response_model=RecommendationResponse,
    summary="Generate segment-level budget recommendations using model predictions and financial assumptions.",
)
def generate(
    request: RecommendationRequest,
    settings: Settings = Depends(get_settings),
) -> RecommendationResponse:
    try:
        return generate_recommendations(request, settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {exc}")
