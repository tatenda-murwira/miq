import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardLayout } from "./components/layout/DashboardLayout";
import { AudiencesPage } from "./pages/AudiencesPage";
import { CampaignsPage } from "./pages/CampaignsPage";
import { HomePage } from "./pages/HomePage";
import { ModelPage } from "./pages/ModelPage";
import { OverviewPage } from "./pages/OverviewPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";

export default function App() {
  return (
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
  );
}

