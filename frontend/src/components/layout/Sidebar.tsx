import { NavLink } from "react-router-dom";

import { navigationItems } from "../../utils/navigation";

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-stone-200 bg-white px-5 py-6 md:block">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase text-signal">Campaign Intelligence</p>
        <h1 className="mt-2 text-2xl font-semibold text-ink">CampaignIQ</h1>
      </div>

      <nav className="space-y-1" aria-label="Primary navigation">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              [
                "block rounded-lg px-3 py-2 text-sm font-medium transition",
                isActive
                  ? "bg-teal-50 text-signal"
                  : "text-graphite hover:bg-stone-100 hover:text-ink",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

