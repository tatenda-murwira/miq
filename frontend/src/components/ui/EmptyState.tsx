interface EmptyStateProps {
  description: string;
  title: string;
}

export function EmptyState({ description, title }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-stone-300 bg-stone-50 p-6 text-center">
      <h4 className="text-base font-semibold text-ink">{title}</h4>
      <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-graphite">{description}</p>
    </div>
  );
}

