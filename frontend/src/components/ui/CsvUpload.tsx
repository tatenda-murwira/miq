import { type ChangeEvent, type DragEvent, useRef, useState } from "react";

import type { DataQualityReport } from "../../types/api";

interface CsvUploadProps {
  error: string | null;
  isUploading: boolean;
  onUpload: (file: File) => Promise<void>;
  onUseDefault: () => Promise<void>;
  uploadProgress: number;
  validationReport: DataQualityReport | null;
}

export function CsvUpload({
  error,
  isUploading,
  onUpload,
  onUseDefault,
  uploadProgress,
  validationReport,
}: CsvUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  function handleFile(file: File | undefined) {
    if (!file || isUploading) {
      return;
    }

    setSelectedFileName(file.name);
    void onUpload(file);
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    handleFile(event.target.files?.[0]);
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    handleFile(event.dataTransfer.files?.[0]);
  }

  return (
    <div className="space-y-4">
      <div
        className={[
          "rounded-lg border border-dashed p-6 text-center transition",
          isDragging ? "border-teal-400 bg-teal-50" : "border-stone-300 bg-stone-50",
        ].join(" ")}
        onDragLeave={() => setIsDragging(false)}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          accept=".csv,text/csv"
          className="hidden"
          disabled={isUploading}
          onChange={handleInputChange}
          type="file"
        />
        <p className="text-sm font-semibold text-ink">
          Drop a CSV here, or select one from your computer.
        </p>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Expected fields are the Facebook ad conversion columns. The backend validates and stores
          only the normalized analysis dataset.
        </p>
        {selectedFileName ? (
          <p className="mt-3 text-xs font-semibold uppercase text-signal">{selectedFileName}</p>
        ) : null}

        <div className="mt-5 flex flex-col justify-center gap-3 sm:flex-row">
          <button
            className="rounded-lg bg-signal px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isUploading}
            onClick={() => inputRef.current?.click()}
            type="button"
          >
            Select CSV
          </button>
          <button
            className="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isUploading}
            onClick={() => void onUseDefault()}
            type="button"
          >
            Use default dataset
          </button>
        </div>
      </div>

      {isUploading && uploadProgress > 0 ? (
        <div>
          <div className="flex items-center justify-between text-xs font-semibold uppercase text-graphite">
            <span>Upload progress</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-200">
            <div
              className="h-full rounded-full bg-signal transition-all"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-coral">
          <p className="font-semibold">Validation failed</p>
          <p className="mt-1">{error}</p>
          {validationReport?.warnings.length ? (
            <ul className="mt-3 space-y-1">
              {validationReport.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
