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

const campaignNameStems = [
  "Campaign Alpha",
  "Campaign Bravo",
  "Campaign Charlie",
  "Campaign Delta",
  "Campaign Echo",
  "Campaign Foxtrot",
  "Campaign Golf",
  "Campaign Hotel",
  "Campaign India",
  "Campaign Juliet",
  "Campaign Kilo",
  "Campaign Lima",
];

const defaultCampaignOrder = ["916", "936", "1178"];

export function formatCampaignName(
  campaignId: number | string | null | undefined,
  campaignIds: Array<number | string> = defaultCampaignOrder,
): string {
  if (campaignId === null || campaignId === undefined || campaignId === "") {
    return "N/A";
  }

  const normalizedId = normalizeCampaignId(campaignId);
  const orderedIds = orderCampaignIds(campaignIds);
  const index = orderedIds.includes(normalizedId)
    ? orderedIds.indexOf(normalizedId)
    : fallbackCampaignIndex(normalizedId);

  return `${campaignNameStems[index % campaignNameStems.length]} ${normalizedId}`;
}

function orderCampaignIds(campaignIds: Array<number | string>): string[] {
  return Array.from(new Set(campaignIds.map(normalizeCampaignId))).sort((a, b) => {
    const aNumber = Number(a);
    const bNumber = Number(b);
    if (Number.isFinite(aNumber) && Number.isFinite(bNumber)) {
      return aNumber - bNumber;
    }
    return a.localeCompare(b);
  });
}

function normalizeCampaignId(campaignId: number | string): string {
  const numericValue = Number(campaignId);
  if (Number.isFinite(numericValue) && Number.isInteger(numericValue)) {
    return String(numericValue);
  }
  return String(campaignId).trim();
}

function fallbackCampaignIndex(campaignId: string): number {
  const numericValue = Number(campaignId);
  if (Number.isFinite(numericValue)) {
    return Math.abs(Math.trunc(numericValue));
  }
  return [...campaignId].reduce((total, character) => total + character.charCodeAt(0), 0);
}
