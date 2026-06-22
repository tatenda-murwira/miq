export function formatNumber(value: number | null | undefined, maximumFractionDigits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }

  return value.toLocaleString(undefined, { maximumFractionDigits });
}

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }

  return value.toLocaleString(undefined, {
    currency: "USD",
    maximumFractionDigits: 2,
    style: "currency",
  });
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }

  return `${(value * 100).toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
}

export function formatRatio(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }

  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}x`;
}

