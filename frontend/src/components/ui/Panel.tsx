import type { ReactNode } from "react";

interface PanelProps {
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  eyebrow?: string;
  title?: string;
}

export function Panel({ actions, children, className = "", eyebrow, title }: PanelProps) {
  return (
    <section className={`rounded-lg border border-stone-200 bg-white p-5 shadow-panel ${className}`}>
      {(eyebrow || title || actions) && (
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {eyebrow ? <p className="text-xs font-semibold uppercase text-signal">{eyebrow}</p> : null}
            {title ? <h3 className="mt-1 text-lg font-semibold text-ink">{title}</h3> : null}
          </div>
          {actions ? <div className="shrink-0">{actions}</div> : null}
        </div>
      )}
      {children}
    </section>
  );
}

