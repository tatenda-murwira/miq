import axios from "axios";
import { useCallback, useEffect, useState } from "react";

import {
  fetchDataPreview,
  fetchDataQuality,
  fetchDataStatus,
  uploadDataset,
  useDefaultDataset,
} from "../services/api";
import type { DataPreviewResponse, DataQualityReport, DataStatusResponse } from "../types/api";

interface CampaignDataState {
  actionLoading: boolean;
  error: string | null;
  loading: boolean;
  preview: DataPreviewResponse | null;
  quality: DataQualityReport | null;
  status: DataStatusResponse | null;
  uploadProgress: number;
  validationReport: DataQualityReport | null;
}

interface ParsedApiError {
  message: string;
  report: DataQualityReport | null;
}

export function useCampaignData() {
  const [state, setState] = useState<CampaignDataState>({
    actionLoading: false,
    error: null,
    loading: true,
    preview: null,
    quality: null,
    status: null,
    uploadProgress: 0,
    validationReport: null,
  });

  const refreshData = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));

    try {
      const status = await fetchDataStatus();
      const quality = await fetchDataQuality().catch(() => status.latest_report);
      const preview = await fetchDataPreview().catch(() => null);

      setState((current) => ({
        ...current,
        loading: false,
        preview,
        quality,
        status,
      }));
    } catch (error) {
      const parsed = parseApiError(error);
      setState((current) => ({
        ...current,
        error: parsed.message,
        loading: false,
        validationReport: parsed.report,
      }));
    }
  }, []);

  const uploadCsv = useCallback(
    async (file: File) => {
      setState((current) => ({
        ...current,
        actionLoading: true,
        error: null,
        uploadProgress: 0,
        validationReport: null,
      }));

      try {
        const response = await uploadDataset(file, (progress) => {
          setState((current) => ({ ...current, uploadProgress: progress }));
        });

        setState((current) => ({
          ...current,
          uploadProgress: 100,
          validationReport: response.report,
        }));
        await refreshData();
      } catch (error) {
        const parsed = parseApiError(error);
        setState((current) => ({
          ...current,
          actionLoading: false,
          error: parsed.message,
          uploadProgress: 0,
          validationReport: parsed.report,
        }));
        return;
      }

      setState((current) => ({ ...current, actionLoading: false }));
    },
    [refreshData],
  );

  const useDefault = useCallback(async () => {
    setState((current) => ({
      ...current,
      actionLoading: true,
      error: null,
      uploadProgress: 0,
      validationReport: null,
    }));

    try {
      const response = await useDefaultDataset();
      setState((current) => ({ ...current, validationReport: response.report }));
      await refreshData();
    } catch (error) {
      const parsed = parseApiError(error);
      setState((current) => ({
        ...current,
        actionLoading: false,
        error: parsed.message,
        validationReport: parsed.report,
      }));
      return;
    }

    setState((current) => ({ ...current, actionLoading: false }));
  }, [refreshData]);

  useEffect(() => {
    void refreshData();
  }, [refreshData]);

  return {
    ...state,
    refreshData,
    uploadCsv,
    useDefault,
  };
}

function parseApiError(error: unknown): ParsedApiError {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (detail && typeof detail === "object" && "message" in detail) {
      return {
        message: String(detail.message),
        report:
          "report" in detail && detail.report
            ? (detail.report as DataQualityReport)
            : null,
      };
    }

    return {
      message: error.message || "The API request failed.",
      report: null,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      report: null,
    };
  }

  return {
    message: "The API request failed.",
    report: null,
  };
}

