import axios from "axios";
import { useCallback, useEffect, useState } from "react";

import {
  fetchAnalyticsAudiences,
  fetchAnalyticsCampaigns,
  fetchAnalyticsOverview,
  fetchAnalyticsSensitivity,
} from "../services/api";
import type {
  AudienceAnalyticsResponse,
  CampaignAnalyticsResponse,
  FinancialAssumptions,
  OverviewAnalyticsResponse,
  SensitivityAnalyticsResponse,
} from "../types/api";
import { useFinancialAssumptions } from "./useFinancialAssumptions";

interface AnalyticsState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  refresh: () => void;
}

export function useOverviewAnalytics(): AnalyticsState<OverviewAnalyticsResponse> {
  return useAnalytics(fetchAnalyticsOverview);
}

export function useCampaignAnalytics(): AnalyticsState<CampaignAnalyticsResponse> {
  return useAnalytics(fetchAnalyticsCampaigns);
}

export function useAudienceAnalytics(): AnalyticsState<AudienceAnalyticsResponse> {
  return useAnalytics(fetchAnalyticsAudiences);
}

export function useSensitivityAnalytics(): AnalyticsState<SensitivityAnalyticsResponse> {
  return useAnalytics(fetchAnalyticsSensitivity);
}

function useAnalytics<T>(
  fetcher: (assumptions: FinancialAssumptions) => Promise<T>,
): AnalyticsState<T> {
  const { assumptions } = useFinancialAssumptions();
  const [refreshToken, setRefreshToken] = useState(0);
  const [state, setState] = useState<Omit<AnalyticsState<T>, "refresh">>({
    data: null,
    error: null,
    loading: true,
  });

  const refresh = useCallback(() => {
    setRefreshToken((current) => current + 1);
  }, []);

  useEffect(() => {
    let isMounted = true;
    setState((current) => ({ ...current, loading: true, error: null }));

    fetcher(assumptions)
      .then((data) => {
        if (isMounted) {
          setState({ data, error: null, loading: false });
        }
      })
      .catch((error: unknown) => {
        if (isMounted) {
          setState({
            data: null,
            error: parseApiError(error),
            loading: false,
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, [assumptions, fetcher, refreshToken]);

  return {
    ...state,
    refresh,
  };
}

function parseApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (detail && typeof detail === "object" && "message" in detail) {
      return String(detail.message);
    }
    return error.message || "The analytics request failed.";
  }

  return error instanceof Error ? error.message : "The analytics request failed.";
}

