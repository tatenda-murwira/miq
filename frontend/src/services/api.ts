import axios, { type AxiosProgressEvent } from "axios";

import type {
  AudienceAnalyticsResponse,
  CampaignAnalyticsResponse,
  DataPreviewResponse,
  DataQualityReport,
  DataStatusResponse,
  DataUploadResponse,
  FinancialAssumptions,
  HealthResponse,
  OverviewAnalyticsResponse,
  SensitivityAnalyticsResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function fetchHealthStatus(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}

export async function fetchDataStatus(): Promise<DataStatusResponse> {
  const response = await apiClient.get<DataStatusResponse>("/data/status");
  return response.data;
}

export async function fetchDataQuality(): Promise<DataQualityReport> {
  const response = await apiClient.get<DataQualityReport>("/data/quality");
  return response.data;
}

export async function fetchDataPreview(): Promise<DataPreviewResponse> {
  const response = await apiClient.get<DataPreviewResponse>("/data/preview");
  return response.data;
}

export async function uploadDataset(
  file: File,
  onUploadProgress?: (progress: number) => void,
): Promise<DataUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<DataUploadResponse>("/data/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (event.total && onUploadProgress) {
        onUploadProgress(Math.round((event.loaded / event.total) * 100));
      }
    },
  });

  return response.data;
}

export async function useDefaultDataset(): Promise<DataUploadResponse> {
  const response = await apiClient.post<DataUploadResponse>("/data/use-default");
  return response.data;
}

export async function fetchAnalyticsOverview(
  assumptions: FinancialAssumptions,
): Promise<OverviewAnalyticsResponse> {
  const response = await apiClient.post<OverviewAnalyticsResponse>("/analytics/overview", assumptions);
  return response.data;
}

export async function fetchAnalyticsCampaigns(
  assumptions: FinancialAssumptions,
): Promise<CampaignAnalyticsResponse> {
  const response = await apiClient.post<CampaignAnalyticsResponse>("/analytics/campaigns", assumptions);
  return response.data;
}

export async function fetchAnalyticsAudiences(
  assumptions: FinancialAssumptions,
): Promise<AudienceAnalyticsResponse> {
  const response = await apiClient.post<AudienceAnalyticsResponse>("/analytics/audiences", assumptions);
  return response.data;
}

export async function fetchAnalyticsSensitivity(
  assumptions: FinancialAssumptions,
): Promise<SensitivityAnalyticsResponse> {
  const response = await apiClient.post<SensitivityAnalyticsResponse>("/analytics/sensitivity", assumptions);
  return response.data;
}
