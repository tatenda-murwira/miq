from typing import List

from pydantic import BaseModel, Field


class FinancialAssumptions(BaseModel):
    average_order_value: float = Field(75, ge=0)
    fulfilment_cost_per_purchase: float = Field(35, ge=0)
    transaction_cost_per_purchase: float = Field(2, ge=0)
    fixed_campaign_operating_cost: float = Field(0, ge=0)


class FunnelStage(BaseModel):
    stage: str
    value: float


class MetricSummary(BaseModel):
    impressions: float
    clicks: float
    leads: float
    purchases: float
    spend: float
    ctr: float | None
    cpc: float | None
    lead_conversion_rate: float | None
    purchase_conversion_rate: float | None
    cost_per_lead: float | None
    cac: float | None
    estimated_revenue: float
    estimated_variable_cost: float
    estimated_total_cost: float
    estimated_profit: float
    estimated_roas: float | None
    estimated_romi: float | None


class OverviewAnalyticsResponse(BaseModel):
    assumptions: FinancialAssumptions
    totals: MetricSummary
    funnel: List[FunnelStage]
    campaign_rollup: List["CampaignAnalyticsRow"]
    observations: List[str]


class CampaignAnalyticsRow(MetricSummary):
    campaign_id: str


class CampaignAnalyticsResponse(BaseModel):
    assumptions: FinancialAssumptions
    campaigns: List[CampaignAnalyticsRow]
    observations: List[str]


class AudienceSegmentRow(MetricSummary):
    group_type: str
    group_value: str
    campaign_id: str | None = None
    age: str | None = None
    gender: str | None = None
    interest: str | None = None


class AudienceAnalyticsResponse(BaseModel):
    assumptions: FinancialAssumptions
    by_age: List[AudienceSegmentRow]
    by_gender: List[AudienceSegmentRow]
    by_interest: List[AudienceSegmentRow]
    by_campaign_age: List[AudienceSegmentRow]
    by_campaign_gender: List[AudienceSegmentRow]
    high_spend_low_conversion_segments: List[AudienceSegmentRow]
    observations: List[str]


class SensitivityScenario(BaseModel):
    average_order_value: float
    estimated_revenue: float
    estimated_profit: float
    estimated_roas: float | None
    estimated_romi: float | None


class SensitivityAnalyticsResponse(BaseModel):
    assumptions: FinancialAssumptions
    scenarios: List[SensitivityScenario]
    observations: List[str]

