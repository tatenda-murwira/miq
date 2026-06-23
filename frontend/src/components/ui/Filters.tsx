import { formatCampaignName } from "../../utils/format";

interface FiltersProps {
  campaignOptions?: string[];
  campaignValue?: string;
  onCampaignChange?: (value: string) => void;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  searchValue?: string;
}

export function Filters({
  campaignOptions = [],
  campaignValue = "",
  onCampaignChange,
  onSearchChange,
  searchPlaceholder = "Search",
  searchValue = "",
}: FiltersProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-[1fr_220px]">
      {onSearchChange ? (
        <input
          className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-teal-400"
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={searchPlaceholder}
          type="search"
          value={searchValue}
        />
      ) : null}
      {onCampaignChange ? (
        <select
          className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-teal-400"
          onChange={(event) => onCampaignChange(event.target.value)}
          value={campaignValue}
        >
          <option value="">All campaigns</option>
          {campaignOptions.map((campaignId) => (
            <option key={campaignId} value={campaignId}>
              {formatCampaignName(campaignId, campaignOptions)}
            </option>
          ))}
        </select>
      ) : null}
    </div>
  );
}
