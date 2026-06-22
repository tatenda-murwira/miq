import { Panel } from "../ui/Panel";
import type { ClassDistribution as ClassDist } from "../../types/model";
import { formatPercent } from "../../utils/format";

interface Props {
  distribution: ClassDist;
}

export function ClassDistributionPanel({ distribution }: Props) {
  const total0 = distribution.total[0] ?? 0;
  const total1 = distribution.total[1] ?? 0;
  const totalAll = total0 + total1;
  const pct0 = totalAll > 0 ? total0 / totalAll : 0;
  const pct1 = totalAll > 0 ? total1 / totalAll : 0;

  return (
    <Panel eyebrow="Target" title="Class distribution">
      <div className="space-y-4">
        <div className="flex gap-6 text-sm">
          <div>
            <span className="font-semibold text-emerald-600">{total1.toLocaleString()}</span>{" "}
            <span className="text-graphite">converting segments ({formatPercent(pct1)})</span>
          </div>
          <div>
            <span className="font-semibold text-stone-600">{total0.toLocaleString()}</span>{" "}
            <span className="text-graphite">non-converting segments ({formatPercent(pct0)})</span>
          </div>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-stone-200">
          <div
            className="h-full rounded-full bg-emerald-500"
            style={{ width: `${pct1 * 100}%` }}
          />
        </div>
        <p className="text-xs leading-5 text-graphite">
          Class imbalance means the model sees far more non-converting segments than converting ones.
          The training uses balanced class weights to compensate, and model selection uses average precision
          rather than accuracy to avoid rewarding a model that simply predicts "no conversion" for everything.
        </p>
      </div>
    </Panel>
  );
}
