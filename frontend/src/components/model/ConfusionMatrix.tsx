import { Panel } from "../ui/Panel";
import type { ConfusionMatrixValues } from "../../types/model";

interface Props {
  matrix: ConfusionMatrixValues;
}

export function ConfusionMatrix({ matrix }: Props) {
  const cells = [
    { value: matrix.true_positives, label: "Correctly recommended converting segments", color: "bg-emerald-100 text-emerald-800" },
    { value: matrix.false_positives, label: "Incorrectly recommended segments", color: "bg-amber-100 text-amber-800" },
    { value: matrix.false_negatives, label: "Missed converting segments", color: "bg-rose-100 text-rose-800" },
    { value: matrix.true_negatives, label: "Correctly rejected non-converting segments", color: "bg-stone-100 text-stone-700" },
  ];

  return (
    <Panel eyebrow="Evaluation" title="Confusion matrix">
      <div className="grid grid-cols-2 gap-3 max-w-md">
        {cells.map((cell) => (
          <div key={cell.label} className={`rounded-lg p-4 text-center ${cell.color}`}>
            <p className="text-2xl font-bold">{cell.value.toLocaleString()}</p>
            <p className="mt-1 text-xs leading-4">{cell.label}</p>
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-4 text-xs text-graphite">
        <span>Rows: Actual (converted / not)</span>
        <span>Columns: Predicted (converted / not)</span>
      </div>
    </Panel>
  );
}
