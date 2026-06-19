type BadgeVariant = "success" | "warning" | "danger" | "neutral";

interface StatusBadgeProps {
  label: string;
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: "border-teal-200 bg-teal-50 text-signal",
  warning: "border-amber-200 bg-amber-50 text-harvest",
  danger: "border-rose-200 bg-rose-50 text-coral",
  neutral: "border-stone-200 bg-stone-100 text-graphite",
};

export function StatusBadge({ label, variant = "neutral" }: StatusBadgeProps) {
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${variantClasses[variant]}`}>
      {label}
    </span>
  );
}

