export interface HealthResponse {
  status: "healthy" | string;
  service: string;
}

export interface DataQualityReport {
  row_count: number;
  column_count: number;
  duplicate_count: number;
  missing_values_by_column: Record<string, number>;
  invalid_numeric_values: Record<string, number>;
  negative_values: Record<string, number>;
  clicks_greater_than_impressions: number;
  purchases_greater_than_leads: number;
  ready_for_analysis: boolean;
  warnings: string[];
}

export interface DataStatusResponse {
  default_dataset_exists: boolean;
  default_dataset_valid: boolean;
  current_dataset_exists: boolean;
  current_dataset_valid: boolean;
  latest_report: DataQualityReport | null;
  warnings: string[];
}

export interface DataUploadResponse {
  message: string;
  stored: boolean;
  report: DataQualityReport;
}

export type DataPreviewRow = Record<string, string | number | null>;

export interface DataPreviewResponse {
  columns: string[];
  rows: DataPreviewRow[];
  row_count: number;
}

export interface FinancialAssumptions {
  average_order_value: number;
  fulfilment_cost_per_purchase: number;
  transaction_cost_per_purchase: number;
  fixed_campaign_operating_cost: number;
}

export interface FunnelStage {
  stage: string;
  value: number;
}

export interface MetricSummary {
  impressions: number;
  clicks: number;
  leads: number;
  purchases: number;
  spend: number;
  ctr: number | null;
  cpc: number | null;
  lead_conversion_rate: number | null;
  purchase_conversion_rate: number | null;
  cost_per_lead: number | null;
  cac: number | null;
  estimated_revenue: number;
  estimated_variable_cost: number;
  estimated_total_cost: number;
  estimated_profit: number;
  estimated_roas: number | null;
  estimated_romi: number | null;
}

export interface CampaignAnalyticsRow extends MetricSummary {
  campaign_id: string;
}

export interface OverviewAnalyticsResponse {
  assumptions: FinancialAssumptions;
  totals: MetricSummary;
  funnel: FunnelStage[];
  campaign_rollup: CampaignAnalyticsRow[];
  observations: string[];
}

export interface CampaignAnalyticsResponse {
  assumptions: FinancialAssumptions;
  campaigns: CampaignAnalyticsRow[];
  observations: string[];
}

export interface AudienceSegmentRow extends MetricSummary {
  group_type: string;
  group_value: string;
  campaign_id: string | null;
  age: string | null;
  gender: string | null;
  interest: string | null;
}

export interface AudienceAnalyticsResponse {
  assumptions: FinancialAssumptions;
  by_age: AudienceSegmentRow[];
  by_gender: AudienceSegmentRow[];
  by_interest: AudienceSegmentRow[];
  by_campaign_age: AudienceSegmentRow[];
  by_campaign_gender: AudienceSegmentRow[];
  high_spend_low_conversion_segments: AudienceSegmentRow[];
  observations: string[];
}

export interface SensitivityScenario {
  average_order_value: number;
  estimated_revenue: number;
  estimated_profit: number;
  estimated_roas: number | null;
  estimated_romi: number | null;
}

export interface SensitivityAnalyticsResponse {
  assumptions: FinancialAssumptions;
  scenarios: SensitivityScenario[];
  observations: string[];
}

export interface CampaignRecord {
  id: string;
  name: string;
  channel: string;
  segment: string;
  spend: number;
  conversions: number;
  startedAt: string;
  endedAt: string;
}

export interface AudienceSegment {
  id: string;
  name: string;
  channel: string;
  conversionIntent: string;
}

export interface ModelSummary {
  trainedAt: string | null;
  target: string | null;
  featureCount: number | null;
  metrics: Record<string, number>;
}

export interface BudgetRecommendation {
  id: string;
  scope: "campaign" | "segment";
  action: "increase" | "decrease" | "hold";
  rationale: string;
}
