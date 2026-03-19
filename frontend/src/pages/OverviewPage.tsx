import { useOverview } from "../hooks/useOverview";
import { PageHeader } from "../components/common/PageHeader";
import { SectionCard } from "../components/common/SectionCard";
import { SummaryCard } from "../components/cards/SummaryCard";
import { RecommendationCard } from "../components/cards/RecommendationCard";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { SpendingByCategoryChart } from "../components/charts/SpendingByCategoryChart";
import { IncomeExpenseSavingsChart } from "../components/charts/IncomeExpenseSavingsChart";
import { CategorySummaryTable } from "../components/tables/CategorySummaryTable";
import { LoadingState, EmptyState, ErrorState } from "../components/common";
import { formatCurrency } from "../utils/currency";

const DEFAULT_USER = "default";

export function OverviewPage() {
  const { overview, spending, loading, error, refetch } = useOverview(DEFAULT_USER);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!overview) return <EmptyState title="No overview" description="Run analysis or add data first." />;

  const catSummary = spending?.spending_by_category ?? [];
  const topCategories = overview.top_categories ?? spending?.top_categories ?? [];
  const cutdownAreas = overview.suggested_cutdown_areas ?? spending?.suggested_cutdown_areas ?? [];
  const limitations = overview.limitations ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overview"
        description="Your financial dashboard"
      />

      <SectionCard title="Executive Summary">
        <p className="text-slate-700 leading-relaxed">
          {overview.human_summary || "No summary available."}
        </p>
      </SectionCard>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <SummaryCard
          label="Total Income"
          value={overview.total_income != null ? formatCurrency(overview.total_income) : "—"}
        />
        <SummaryCard
          label="Total Expenses"
          value={overview.total_expenses != null ? formatCurrency(overview.total_expenses) : "—"}
        />
        <SummaryCard
          label="Net Savings"
          value={overview.net_savings != null ? formatCurrency(overview.net_savings) : "—"}
        />
        <SummaryCard
          label="Savings Rate"
          value={
            overview.savings_rate != null ? `${overview.savings_rate.toFixed(1)}%` : "—"
          }
        />
        <SummaryCard
          label="Subscription Spend"
          value={overview.subscription_spend != null ? formatCurrency(overview.subscription_spend) : "—"}
        />
        <SummaryCard
          label="Goal Gap"
          value={overview.goal_gap != null ? formatCurrency(overview.goal_gap) : "—"}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <SectionCard title="Spending by Category">
          <SpendingByCategoryChart data={catSummary} />
        </SectionCard>
        <SectionCard title="Income vs Expenses vs Savings">
          <IncomeExpenseSavingsChart
            income={overview.total_income ?? 0}
            expenses={overview.total_expenses ?? 0}
            savings={overview.net_savings ?? 0}
          />
        </SectionCard>
      </div>

      <SectionCard title="Category Summary">
        <CategorySummaryTable categories={catSummary} totalExpenses={overview.total_expenses ?? 0} />
      </SectionCard>

      {cutdownAreas.length > 0 && (
        <SectionCard title="Recommended Actions">
          <div className="space-y-2">
            {cutdownAreas.map((area, i) => (
              <RecommendationCard
                key={i}
                recommendation={`Consider reducing spend in ${area}`}
                area={area}
              />
            ))}
          </div>
        </SectionCard>
      )}

      {limitations.length > 0 && (
        <LimitationsCard limitations={limitations} title="Data coverage & limitations" />
      )}
    </div>
  );
}
