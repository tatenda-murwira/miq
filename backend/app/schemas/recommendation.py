from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    average_order_value: float = Field(75, ge=0)
    fulfilment_cost_per_purchase: float = Field(35, ge=0)
    transaction_cost_per_purchase: float = Field(2, ge=0)
    fixed_campaign_operating_cost: float = Field(0, ge=0)
    probability_threshold: Optional[float] = Field(None, ge=0, le=1)
    filter_campaign: Optional[str] = None
    filter_age: Optional[str] = None
    filter_gender: Optional[str] = None
    filter_interest: Optional[str] = None


class SegmentRecommendation(BaseModel):
    ad_id: int
    campaign_id: int
    age: str
    gender: str
    interest: int
    impressions: int
    clicks: int
    spend: float
    actual_purchases: int
    conversion_probability: float
    predicted_class: int
    ctr: Optional[float]
    cpc: Optional[float]
    cac: Optional[float]
    purchase_conversion_rate: Optional[float]
    estimated_revenue: float
    estimated_profit: float
    recommendation: str
    recommendation_reason: str


class ExecutiveSummary(BaseModel):
    best_campaign_by_profit: Optional[str]
    lowest_cac_campaign: Optional[str]
    best_age_group: Optional[str]
    best_interest_group: Optional[str]
    largest_inefficient_spend_area: Optional[str]
    segments_by_recommendation: dict[str, int]
    estimated_profit_selected: float
    main_limitation: str
    recommended_next_action: str


class RecommendationRule(BaseModel):
    recommendation: str
    conditions: List[str]


class RecommendationResponse(BaseModel):
    segments: List[SegmentRecommendation]
    executive_summary: ExecutiveSummary
    rules: List[RecommendationRule]
    threshold_used: float
    total_segments: int
    limitations: List[str]
