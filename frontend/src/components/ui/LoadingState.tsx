interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Loading analytics" }: LoadingStateProps) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white p-6 text-center text-sm font-medium text-graphite">
      {label}...
    </div>
  );
}

