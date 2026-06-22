import axios from "axios";
import { useCallback, useEffect, useState } from "react";

import { fetchModelStatus, trainModel } from "../services/modelApi";
import type { ModelStatusResponse, TrainingResult } from "../types/model";

interface ModelState {
  status: ModelStatusResponse | null;
  trainingResult: TrainingResult | null;
  loading: boolean;
  training: boolean;
  error: string | null;
  train: () => void;
  refresh: () => void;
}

export function useModel(): ModelState {
  const [status, setStatus] = useState<ModelStatusResponse | null>(null);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const s = await fetchModelStatus();
      setStatus(s);
    } catch (err) {
      setError(parseError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const train = useCallback(async () => {
    if (training) return;
    try {
      setTraining(true);
      setError(null);
      const result = await trainModel();
      setTrainingResult(result);
      setStatus({
        model_exists: true,
        selected_model_name: result.selected_model,
        training_timestamp: result.metadata.training_timestamp,
        dataset_row_count: result.metadata.dataset_row_count,
        target_definition: result.metadata.target_definition,
        model_version: status?.model_version ?? "1.0.0",
      });
    } catch (err) {
      setError(parseError(err));
    } finally {
      setTraining(false);
    }
  }, [training, status?.model_version]);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  return { status, trainingResult, loading, training, error, train, refresh: loadStatus };
}

function parseError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    return err.message || "Request failed.";
  }
  return err instanceof Error ? err.message : "An unexpected error occurred.";
}
