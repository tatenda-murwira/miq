interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-5 text-sm text-coral">
      <p className="font-semibold">Unable to load analytics</p>
      <p className="mt-1">{message}</p>
      {onRetry ? (
        <button
          className="mt-4 rounded-lg border border-rose-200 bg-white px-3 py-2 text-sm font-semibold text-coral transition hover:bg-rose-100"
          onClick={onRetry}
          type="button"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

