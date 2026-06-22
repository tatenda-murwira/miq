import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Panel } from "../ui/Panel";
import type { FeatureImportance } from "../../types/model";

interface Props {
  features: FeatureImportance[];
  modelName: string;
}

export function FeatureImportanceChart({ features, modelName }: Props) {
  const top = features.slice(0, 15);
  const isLogistic = modelName === "LogisticRegression";

  const data = top.map((f) => ({
    name: f.feature,
    value: f.importance,
    direction: f.direction,
  }));

  return (
    <Panel eyebrow="Explainability" title="Feature importance">
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, bottom: 5, left: 100 }}>
            <XAxis type="number" tickFormatter={(v: number) => v.toFixed(2)} />
            <YAxis type="category" dataKey="name" width={95} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => v.toFixed(4)} />
            <Bar dataKey="value" name="Importance">
              {data.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={
                    isLogistic
                      ? entry.direction === "positive"
                        ? "#10b981"
                        : "#f43f5e"
                      : "#3b82f6"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {isLogistic && (
        <div className="mt-3 flex gap-4 text-xs text-graphite">
          <span className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded bg-emerald-500" /> Increases conversion probability
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded bg-rose-500" /> Decreases conversion probability
          </span>
        </div>
      )}
      <p className="mt-2 text-xs text-graphite">
        These are model associations, not proven causes. A feature's importance reflects its statistical relationship
        with conversions in the training data, not a guaranteed causal effect on future outcomes.
      </p>
    </Panel>
  );
}
