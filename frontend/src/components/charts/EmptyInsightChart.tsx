import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface ChartDatum {
  name: string;
  value: number;
}

interface EmptyInsightChartProps {
  data?: ChartDatum[];
}

export function EmptyInsightChart({ data = [] }: EmptyInsightChartProps) {
  return (
    <div className="relative h-72 overflow-hidden rounded-lg border border-stone-200 bg-white">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 24, right: 24, bottom: 24, left: 8 }}>
          <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} width={36} />
          <Tooltip />
          <Bar dataKey="value" fill="#0f766e" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {data.length === 0 ? (
        <div className="absolute inset-0 flex items-center justify-center px-6 text-center">
          <div className="rounded-lg border border-stone-200 bg-white px-5 py-4 shadow-sm">
            <p className="text-sm font-semibold text-ink">No campaign dataset loaded</p>
            <p className="mt-1 text-sm text-graphite">Charts will render after real campaign data is connected.</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

