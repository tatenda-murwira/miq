export interface NavigationItem {
  label: string;
  path: string;
}

export const navigationItems: NavigationItem[] = [
  { label: "Home", path: "/" },
  { label: "Overview", path: "/overview" },
  { label: "Campaigns", path: "/campaigns" },
  { label: "Audiences", path: "/audiences" },
  { label: "Model", path: "/model" },
  { label: "Recommendations", path: "/recommendations" },
];

export function getRouteTitle(pathname: string): string {
  const route = navigationItems.find((item) => item.path === pathname);
  return route?.label ?? "CampaignIQ";
}

