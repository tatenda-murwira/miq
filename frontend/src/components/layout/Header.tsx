import { NavLink, useLocation } from "react-router-dom";

import { getRouteTitle, navigationItems } from "../../utils/navigation";

export function Header() {
  const location = useLocation();
  const title = getRouteTitle(location.pathname);

  return (
    <header className="sticky top-0 z-20 border-b border-stone-200 bg-stone-50/95 px-4 py-4 backdrop-blur sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase text-harvest">Marketing analytics workspace</p>
            <h2 className="text-xl font-semibold text-ink sm:text-2xl">{title}</h2>
          </div>
          <div className="hidden rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-graphite shadow-sm sm:block">
            API driven dashboard
          </div>
        </div>

        <nav className="flex gap-2 overflow-x-auto pb-1 md:hidden" aria-label="Mobile navigation">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                [
                  "whitespace-nowrap rounded-lg border px-3 py-2 text-sm font-medium",
                  isActive
                    ? "border-teal-200 bg-teal-50 text-signal"
                    : "border-stone-200 bg-white text-graphite",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}

