import { Panel } from "../ui/Panel";
import { formatPercent } from "../../utils/format";
import type { ModelResult } from "../../types/model";

interface Props {
  leaderboard: ModelResult[];
  selectedModel: string;
}

const METRIC_TIPS: Record<string, string> = {
  precision: "Of segments the model recommends, what fraction actually converted? Higher = fewer wasted recommendations.",
  recall: "Of all segments that actually converted, how many did the model catch? Higher = fewer missed opportunities.",
  f1_score: "Harmonic mean of precision and recall. Balances wasted spend against missed conversions.",
  roc_auc: "Overall ranking ability. 1.0 = perfect separation. 0.5 = random guess.",
  average_precision: "Summarises precision-recall across all thresholds. Best single metric when conversions are rare.",
};

export function ModelLeaderboard({ leaderboard, selectedModel }: Props) {
  return (
    <Panel eyebrow="Comparison" title="Model leaderboard">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-200 text-left text-xs font-semibold uppercase text-graphite">
              <th className="pb-2 pr-4">Model</th>
              {Object.keys(METRIC_TIPS).map((key) => (
                <th key={key} className="pb-2 px-3 text-right" title={METRIC_TIPS[key]}>
                  {key.replace("_", " ")}
                </th>
              ))}
              <th className="pb-2 pl-3 text-center">Selected</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((model) => (
              <tr
                key={model.model_name}
                className={`border-b border-stone-100 ${model.model_name === selectedModel ? "bg-emerald-50" : ""}`}
              >
                <td className="py-2 pr-4 font-medium text-ink">{model.model_name}</td>
                <td className="py-2 px-3 text-right">{formatPercent(model.metrics.precision)}</td>
                <td className="py-2 px-3 text-right">{formatPercent(model.metrics.recall)}</td>
                <td className="py-2 px-3 text-right">{formatPercent(model.metrics.f1_score)}</td>
                <td className="py-2 px-3 text-right">{formatPercent(model.metrics.roc_auc)}</td>
                <td className="py-2 px-3 text-right">{formatPercent(model.metrics.average_precision)}</td>
                <td className="py-2 pl-3 text-center">
                  {model.model_name === selectedModel ? (
                    <span className="inline-block rounded bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                      ✓
                    </span>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-graphite">
        Selection priority: average precision → F1-score → ROC-AUC. Hover column headers for explanations.
      </p>
    </Panel>
  );
}
