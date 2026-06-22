interface KpiCardProps {
  helper?: string;
  label: string;
  value: string;
}

export function KpiCard({ helper, label, value }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase text-graphite">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
      {helper ? <p className="mt-2 text-sm leading-5 text-graphite">{helper}</p> : null}
    </div>
  );
}

