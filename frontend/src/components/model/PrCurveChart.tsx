import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Panel } from "../ui/Panel";
import type { ModelResult } from "../../types/model";

interface Props {
  leaderboard: ModelResult[];
}

const COLORS = ["#3b82f6", "#f59e0b"];

export function PrCurveChart({ leaderboard }: Props) {
  return (
    <Panel eyebrow="Curves" title="Precision-recall curve">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart margin={{ top: 10, right: 20, bottom: 30, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="x"
              type="number"
              domain={[0, 1]}
              label={{ value: "Recall", position: "bottom", offset: 10, fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <YAxis
              type="number"
              domain={[0, 1]}
              label={{ value: "Precision", angle: -90, position: "left", offset: 0, fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <Tooltip formatter={(v: number) => v.toFixed(3)} />
            <Legend verticalAlign="top" />
            {leaderboard.map((model, idx) => (
              <Line
                key={model.model_name}
                data={model.precision_recall_curve.map((p) => ({ x: p.x, y: p.y }))}
                dataKey="y"
                name={model.model_name}
                stroke={COLORS[idx % COLORS.length]}
                dot={false}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-3 text-xs text-graphite">
        The precision-recall curve is especially useful when relatively few segments convert.
        It shows the tradeoff between catching more converters (recall) and avoiding wasted recommendations (precision).
      </p>
    </Panel>
  );
}
