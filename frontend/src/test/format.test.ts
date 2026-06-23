import { describe, expect, it } from "vitest";
import { formatCampaignName } from "../utils/format";

describe("formatCampaignName", () => {
  it("uses readable names while keeping default campaign ids", () => {
    expect(formatCampaignName(916)).toBe("Campaign One (916)");
    expect(formatCampaignName(936)).toBe("Campaign Two (936)");
    expect(formatCampaignName(1178)).toBe("Campaign Three (1178)");
  });

  it("assigns readable names from sorted campaign ids", () => {
    const campaignIds = [300, 100, 200];

    expect(formatCampaignName(100, campaignIds)).toBe("Campaign One (100)");
    expect(formatCampaignName(200, campaignIds)).toBe("Campaign Two (200)");
    expect(formatCampaignName(300, campaignIds)).toBe("Campaign Three (300)");
  });
});
