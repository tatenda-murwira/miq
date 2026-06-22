import { useState } from "react";

interface DownloadButtonProps {
  label: string;
  onDownload: () => Promise<void>;
  className?: string;
}

export function DownloadButton({ label, onDownload, className = "" }: DownloadButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      await onDownload();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? err?.message ?? "Download failed.";
      setError(typeof msg === "string" ? msg : "Download failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="inline-flex flex-col items-start">
      <button
        className={`rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-semibold text-ink transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
        disabled={loading}
        onClick={handleClick}
        type="button"
      >
        {loading ? "Downloading..." : label}
      </button>
      {error && <p className="mt-1 text-xs text-coral">{error}</p>}
    </div>
  );
}
