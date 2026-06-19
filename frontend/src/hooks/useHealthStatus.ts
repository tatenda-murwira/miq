import { useEffect, useState } from "react";

import { fetchHealthStatus } from "../services/api";
import type { HealthResponse } from "../types/api";

type RequestStatus = "idle" | "loading" | "success" | "error";

interface HealthState {
  data: HealthResponse | null;
  error: string | null;
  status: RequestStatus;
}

export function useHealthStatus() {
  const [state, setState] = useState<HealthState>({
    data: null,
    error: null,
    status: "idle",
  });

  useEffect(() => {
    let isMounted = true;

    async function loadHealth() {
      setState((current) => ({ ...current, status: "loading", error: null }));

      try {
        const data = await fetchHealthStatus();

        if (isMounted) {
          setState({ data, error: null, status: "success" });
        }
      } catch (error) {
        if (isMounted) {
          const message = error instanceof Error ? error.message : "Unable to reach the API";
          setState({ data: null, error: message, status: "error" });
        }
      }
    }

    void loadHealth();

    return () => {
      isMounted = false;
    };
  }, []);

  return state;
}

