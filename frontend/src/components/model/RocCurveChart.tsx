import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Panel } from "../ui/Panel";
import type { ModelResult } from "../../types/model";

interface Props {
  leaderboard: ModelResult[];
}

const COLORS = ["#3b82f6", "#f59e0b"];

export function RocCurveChart({ leaderboard }: Props) {
  // Merge curve points from all models into a unified dataset
  const maxLen = Math.max(...leaderboard.map((m) => m.roc_curve.length));
  const data = Array.from({ length: maxLen }, (_, i) => {
    const point: Record<string, number> = {};
    leaderboard.forEach((model) => {
      const p = model.roc_curve[Math.min(i, model.roc_curve.length - 1)];
      point[`${model.model_name}_fpr`] = p.x;
      point[`${model.model_name}_tpr`] = p.y;
    });
    return point;
  });

  return (
    <Panel eyebrow="Curves" title="ROC curve">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart margin={{ top: 10, right: 20, bottom: 30, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="x"
              type="number"
              domain={[0, 1]}
              label={{ value: "False Positive Rate", position: "bottom", offset: 10, fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <YAxis
              type="number"
              domain={[0, 1]}
              label={{ value: "True Positive Rate", angle: -90, position: "left", offset: 0, fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <Tooltip formatter={(v: number) => v.toFixed(3)} />
            <Legend verticalAlign="top" />
            {leaderboard.map((model, idx) => (
              <Line
                key={model.model_name}
                data={model.roc_curve.map((p) => ({ x: p.x, y: p.y }))}
                dataKey="y"
                name={model.model_name}
                stroke={COLORS[idx % COLORS.length]}
                dot={false}
                strokeWidth={2}
              />
            ))}
            <Line
              data={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
              dataKey="y"
              name="Random (baseline)"
              stroke="#d1d5db"
              strokeDasharray="5 5"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
