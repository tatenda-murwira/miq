import { apiClient } from "./api";
import type {
  FeatureImportance,
  ModelStatusResponse,
  TrainingResult,
} from "../types/model";

export async function fetchModelStatus(): Promise<ModelStatusResponse> {
  const response = await apiClient.get<ModelStatusResponse>("/model/status");
  return response.data;
}

export async function trainModel(): Promise<TrainingResult> {
  const response = await apiClient.post<TrainingResult>("/model/train", undefined, {
    timeout: 60000,
  });
  return response.data;
}

export async function fetchModelResults(): Promise<TrainingResult["metadata"]> {
  const response = await apiClient.get<TrainingResult["metadata"]>("/model/results");
  return response.data;
}

export async function fetchFeatureImportance(): Promise<FeatureImportance[]> {
  const response = await apiClient.get<FeatureImportance[]>("/model/feature-importance");
  return response.data;
}
