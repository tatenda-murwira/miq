export interface RecommendationRequest {
  average_order_value: number;
  fulfilment_cost_per_purchase: number;
  transaction_cost_per_purchase: number;
  fixed_campaign_operating_cost: number;
  probability_threshold?: number | null;
  filter_campaign?: string | null;
  filter_age?: string | null;
  filter_gender?: string | null;
  filter_interest?: string | null;
}

export interface SegmentRecommendation {
  ad_id: number;
  campaign_id: number;
  age: string;
  gender: string;
  interest: number;
  impressions: number;
  clicks: number;
  spend: number;
  actual_purchases: number;
  conversion_probability: number;
  predicted_class: number;
  ctr: number | null;
  cpc: number | null;
  cac: number | null;
  purchase_conversion_rate: number | null;
  estimated_revenue: number;
  estimated_profit: number;
  recommendation: string;
  recommendation_reason: string;
}

export interface ExecutiveSummary {
  best_campaign_by_profit: string | null;
  lowest_cac_campaign: string | null;
  best_age_group: string | null;
  best_interest_group: string | null;
  largest_inefficient_spend_area: string | null;
  segments_by_recommendation: Record<string, number>;
  estimated_profit_selected: number;
  main_limitation: string;
  recommended_next_action: string;
}

export interface RecommendationRule {
  recommendation: string;
  conditions: string[];
}

export interface RecommendationResponse {
  segments: SegmentRecommendation[];
  executive_summary: ExecutiveSummary;
  rules: RecommendationRule[];
  threshold_used: number;
  total_segments: number;
  limitations: string[];
}

export type RecommendationLabel =
  | "Increase budget carefully"
  | "Continue"
  | "Monitor"
  | "Reduce budget"
  | "Pause";
