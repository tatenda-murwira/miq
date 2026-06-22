import { describe, it, expect } from "vitest";
import type { RecommendationResponse, SegmentRecommendation } from "../types/recommendation";

describe("Recommendation types", () => {
  it("SegmentRecommendation has all required fields", () => {
    const segment: SegmentRecommendation = {
      ad_id: 1,
      campaign_id: 916,
      age: "30-34",
      gender: "M",
      interest: 15,
      impressions: 5000,
      clicks: 100,
      spend: 50.0,
      actual_purchases: 2,
      conversion_probability: 0.72,
      predicted_class: 1,
      ctr: 0.02,
      cpc: 0.5,
      cac: 25.0,
      purchase_conversion_rate: 0.02,
      estimated_revenue: 150.0,
      estimated_profit: 74.0,
      recommendation: "Continue",
      recommendation_reason: "Test reason",
    };
    expect(segment.recommendation).toBe("Continue");
    expect(segment.conversion_probability).toBeGreaterThan(0);
  });

  it("RecommendationResponse structure is valid", () => {
    const response: RecommendationResponse = {
      segments: [],
      executive_summary: {
        best_campaign_by_profit: "916",
        lowest_cac_campaign: "916",
        best_age_group: "30-34",
        best_interest_group: "15",
        largest_inefficient_spend_area: "Campaign 936",
        segments_by_recommendation: {
          "Increase budget carefully": 10,
          Continue: 20,
          Monitor: 15,
          "Reduce budget": 8,
          Pause: 5,
        },
        estimated_profit_selected: 1200.5,
        main_limitation: "Test limitation",
        recommended_next_action: "Test action",
      },
      rules: [
        { recommendation: "Continue", conditions: ["Prob >= threshold", "Profit > 0"] },
      ],
      threshold_used: 0.5,
      total_segments: 58,
      limitations: ["Test limitation"],
    };
    expect(response.total_segments).toBe(58);
    expect(response.rules.length).toBeGreaterThan(0);
  });
});

describe("Recommendation labels", () => {
  const validLabels = [
    "Increase budget carefully",
    "Continue",
    "Monitor",
    "Reduce budget",
    "Pause",
  ];

  it("all valid labels are recognized", () => {
    expect(validLabels).toHaveLength(5);
    validLabels.forEach((label) => expect(label.length).toBeGreaterThan(0));
  });
});
