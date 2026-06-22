import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardLayout } from "./components/layout/DashboardLayout";

const HomePage = lazy(() => import("./pages/HomePage").then((module) => ({ default: module.HomePage })));
const OverviewPage = lazy(() =>
  import("./pages/OverviewPage").then((module) => ({ default: module.OverviewPage })),
);
const CampaignsPage = lazy(() =>
  import("./pages/CampaignsPage").then((module) => ({ default: module.CampaignsPage })),
);
const AudiencesPage = lazy(() =>
  import("./pages/AudiencesPage").then((module) => ({ default: module.AudiencesPage })),
);
const ModelPage = lazy(() => import("./pages/ModelPage").then((module) => ({ default: module.ModelPage })));
const RecommendationsPage = lazy(() =>
  import("./pages/RecommendationsPage").then((module) => ({ default: module.RecommendationsPage })),
);

export default function App() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-stone-50 px-4 text-sm font-medium text-graphite">
          Loading CampaignIQ...
        </div>
      }
    >
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/campaigns" element={<CampaignsPage />} />
          <Route path="/audiences" element={<AudiencesPage />} />
          <Route path="/model" element={<ModelPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
