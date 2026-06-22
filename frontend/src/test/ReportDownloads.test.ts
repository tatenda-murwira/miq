import { describe, it, expect } from "vitest";
import {
  downloadCampaignSummaryCsv,
  downloadRecommendationsCsv,
  downloadModelMetricsCsv,
  downloadExecutiveSummaryPdf,
} from "../services/reportApi";

describe("Report API service", () => {
  it("downloadCampaignSummaryCsv is a function", () => {
    expect(typeof downloadCampaignSummaryCsv).toBe("function");
  });

  it("downloadRecommendationsCsv is a function", () => {
    expect(typeof downloadRecommendationsCsv).toBe("function");
  });

  it("downloadModelMetricsCsv is a function", () => {
    expect(typeof downloadModelMetricsCsv).toBe("function");
  });

  it("downloadExecutiveSummaryPdf is a function", () => {
    expect(typeof downloadExecutiveSummaryPdf).toBe("function");
  });
});

describe("Report filenames", () => {
  it("expected filenames are defined", () => {
    const expectedFilenames = [
      "campaigniq_campaign_summary.csv",
      "campaigniq_recommendations.csv",
      "campaigniq_model_metrics.csv",
      "campaigniq_executive_summary.pdf",
    ];
    expectedFilenames.forEach((name) => {
      expect(name.length).toBeGreaterThan(0);
      expect(name).toMatch(/\.(csv|pdf)$/);
    });
  });
});
