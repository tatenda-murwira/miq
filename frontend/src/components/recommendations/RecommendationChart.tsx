import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const COLORS: Record<string, string> = {
  "Increase budget carefully": "#0d9488",
  Continue: "#2563eb",
  Monitor: "#d97706",
  "Reduce budget": "#ea580c",
  Pause: "#e11d48",
};

interface Props {
  distribution: Record<string, number>;
}

export function RecommendationChart({ distribution }: Props) {
  const data = Object.entries(distribution)
    .map(([name, value]) => ({ name, value }))
    .filter((d) => d.value > 0);

  if (data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 120, right: 20, top: 10, bottom: 10 }}>
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] ?? "#94a3b8"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
