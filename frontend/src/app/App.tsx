import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { LandingPage } from "../pages/LandingPage";
import { DataSourcesPage } from "../pages/DataSourcesPage";
import { DataReviewPage } from "../pages/DataReviewPage";
import { OverviewPage } from "../pages/OverviewPage";
import { AskFinancePage } from "../pages/AskFinancePage";
import { TransactionsPage } from "../pages/TransactionsPage";
import { SubscriptionsPage } from "../pages/SubscriptionsPage";
import { SavingsGoalPage } from "../pages/SavingsGoalPage";
import { InvestmentsPage } from "../pages/InvestmentsPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<AppShell />}>
          <Route path="dashboard" element={<OverviewPage />} />
          <Route path="ask" element={<AskFinancePage />} />
          <Route path="transactions" element={<TransactionsPage />} />
          <Route path="subscriptions" element={<SubscriptionsPage />} />
          <Route path="savings-goal" element={<SavingsGoalPage />} />
          <Route path="investments" element={<InvestmentsPage />} />
          <Route path="data-sources" element={<DataSourcesPage />} />
          <Route path="data-review" element={<DataReviewPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
