import { Panel } from "../ui/Panel";
import { KpiCard } from "../ui/KpiCard";
import type { ModelStatusResponse } from "../../types/model";

interface Props {
  status: ModelStatusResponse | null;
  training: boolean;
  onTrain: () => void;
}

export function ModelStatus({ status, training, onTrain }: Props) {
  return (
    <Panel
      eyebrow="Model"
      title="Training status"
      actions={
        <button
          className="rounded-lg bg-signal px-4 py-2 text-sm font-semibold text-white transition hover:bg-signal/90 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={training}
          onClick={onTrain}
          type="button"
        >
          {training ? "Training..." : "Train and evaluate models"}
        </button>
      }
    >
      {training && (
        <p className="mb-4 text-sm text-graphite animate-pulse">
          Training models on the current dataset. This may take a few seconds...
        </p>
      )}
      {status?.model_exists ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard label="Selected model" value={status.selected_model_name ?? "—"} />
          <KpiCard label="Last trained" value={status.training_timestamp ? new Date(status.training_timestamp).toLocaleString() : "—"} />
          <KpiCard label="Dataset rows" value={status.dataset_row_count?.toLocaleString() ?? "—"} />
          <KpiCard label="Target" value={status.target_definition ?? "—"} />
          <KpiCard label="Model version" value={status.model_version} />
        </div>
      ) : (
        <p className="text-sm text-graphite">
          No trained model exists. Click "Train and evaluate models" to begin.
        </p>
      )}
    </Panel>
  );
}
