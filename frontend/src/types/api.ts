export interface HealthResponse {
  status: "healthy" | string;
  service: string;
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

