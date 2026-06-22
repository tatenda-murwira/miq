import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { FinancialAssumptionsProvider } from "./hooks/useFinancialAssumptions";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <FinancialAssumptionsProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </FinancialAssumptionsProvider>
  </React.StrictMode>,
);
