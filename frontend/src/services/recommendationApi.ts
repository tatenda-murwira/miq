import { apiClient } from "./api";
import type { RecommendationRequest, RecommendationResponse } from "../types/recommendation";

export async function generateRecommendations(
  request: RecommendationRequest,
): Promise<RecommendationResponse> {
  const response = await apiClient.post<RecommendationResponse>(
    "/recommendations/generate",
    request,
    { timeout: 30000 },
  );
  return response.data;
}
