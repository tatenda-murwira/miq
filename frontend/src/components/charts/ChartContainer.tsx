import type { ReactNode } from "react";

interface ChartContainerProps {
  children: ReactNode;
  title: string;
}

export function ChartContainer({ children, title }: ChartContainerProps) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white p-4">
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <div className="mt-4 h-72">{children}</div>
    </div>
  );
}

