const BADGE_STYLES: Record<string, string> = {
  "Increase budget carefully": "border-teal-200 bg-teal-50 text-teal-700",
  Continue: "border-blue-200 bg-blue-50 text-blue-700",
  Monitor: "border-amber-200 bg-amber-50 text-amber-700",
  "Reduce budget": "border-orange-200 bg-orange-50 text-orange-700",
  Pause: "border-rose-200 bg-rose-50 text-rose-700",
};

export function RecommendationBadge({ label }: { label: string }) {
  const style = BADGE_STYLES[label] ?? "border-stone-200 bg-stone-100 text-graphite";
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold whitespace-nowrap ${style}`}>
      {label}
    </span>
  );
}
