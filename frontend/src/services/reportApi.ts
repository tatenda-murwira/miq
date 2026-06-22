import { apiClient } from "./api";
import type { FinancialAssumptions } from "../types/api";

interface DownloadOptions {
  assumptions: FinancialAssumptions;
  probabilityThreshold?: number | null;
}

async function downloadBlob(
  url: string,
  method: "get" | "post",
  filename: string,
  body?: unknown,
): Promise<void> {
  const response = await apiClient.request({
    url,
    method,
    data: body,
    responseType: "blob",
    timeout: 60000,
  });

  // Extract filename from Content-Disposition if available
  const disposition = response.headers["content-disposition"] ?? "";
  const match = disposition.match(/filename=([^\s;]+)/);
  const resolvedFilename = match?.[1] ?? filename;

  const blob = new Blob([response.data]);
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = resolvedFilename;
  link.click();
  URL.revokeObjectURL(objectUrl);
}

export async function downloadCampaignSummaryCsv(options: DownloadOptions): Promise<void> {
  await downloadBlob(
    "/reports/campaign-summary-csv",
    "post",
    "campaigniq_campaign_summary.csv",
    options.assumptions,
  );
}

export async function downloadRecommendationsCsv(options: DownloadOptions): Promise<void> {
  const params = options.probabilityThreshold != null
    ? `?probability_threshold=${options.probabilityThreshold}`
    : "";
  await downloadBlob(
    `/reports/recommendations-csv${params}`,
    "post",
    "campaigniq_recommendations.csv",
    options.assumptions,
  );
}

export async function downloadModelMetricsCsv(): Promise<void> {
  await downloadBlob(
    "/reports/model-metrics-csv",
    "get",
    "campaigniq_model_metrics.csv",
  );
}

export async function downloadExecutiveSummaryPdf(options: DownloadOptions): Promise<void> {
  const params = options.probabilityThreshold != null
    ? `?probability_threshold=${options.probabilityThreshold}`
    : "";
  await downloadBlob(
    `/reports/executive-summary-pdf${params}`,
    "post",
    "campaigniq_executive_summary.pdf",
    options.assumptions,
  );
}
