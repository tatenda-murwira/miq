from typing import List, Optional

from pydantic import BaseModel, Field


class ThresholdAssumptions(BaseModel):
    average_order_value: float = Field(75, ge=0)
    fulfilment_cost_per_purchase: float = Field(35, ge=0)
    transaction_cost_per_purchase: float = Field(2, ge=0)
    fixed_campaign_operating_cost: float = Field(0, ge=0)


class ThresholdResult(BaseModel):
    threshold: float
    segments_selected: int
    pct_segments_selected: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    actual_purchases: float
    selected_spend: float
    estimated_revenue: float
    estimated_total_cost: float
    estimated_profit: float


class StrategyComparison(BaseModel):
    strategy: str
    segments_selected: int
    actual_purchases: float
    selected_spend: float
    estimated_revenue: float
    estimated_profit: float


class ThresholdAnalysisResponse(BaseModel):
    thresholds: List[ThresholdResult]
    recommended_threshold: float
    recommended_reason: str
    recommended_metrics: ThresholdResult
    strategy_comparisons: List[StrategyComparison]
    limitations: List[str]
