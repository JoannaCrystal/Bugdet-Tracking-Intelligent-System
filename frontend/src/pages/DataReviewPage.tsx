import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/common/PageHeader";
import { SectionCard } from "../components/common/SectionCard";
import { Button } from "../components/ui/button";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { StatusPill } from "../components/common/StatusPill";
import { LoadingState, EmptyState, ErrorState } from "../components/common";
import { getTransactions, getMonthlySummary } from "../services/ingestionApi";
import type { Transaction } from "../types/api";
import { formatCurrency } from "../utils/currency";
import { formatDate } from "../utils/date";

const DEFAULT_USER = "default";

export function DataReviewPage() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ min?: string; max?: string }>({});
  const [limitations, setLimitations] = useState<string[]>([]);

  useEffect(() => {
    Promise.all([
      getTransactions({ limit: 500, user_id: DEFAULT_USER }),
      getMonthlySummary({ user_id: DEFAULT_USER }),
    ])
      .then(([txs, summary]) => {
        setTransactions(txs);
        if (txs.length > 0) {
          const dates = txs.map((t) => t.date);
          const min = dates.reduce((a, b) => (a < b ? a : b));
          const max = dates.reduce((a, b) => (a > b ? a : b));
          setDateRange({ min: min.split("T")[0], max: max.split("T")[0] });
        }
        if (txs.length < 10) {
          setLimitations(["Short coverage period – consider uploading more transactions for better insights."]);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const sources = [...new Set(transactions.map((t) => t.source))];

  const handleRunAnalysis = () => {
    navigate("/dashboard");
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  if (transactions.length === 0) {
    return (
      <EmptyState
        title="No data to review"
        description="Add transactions from Data Sources to review your data."
        actionLabel="Go to Data Sources"
        onAction={() => navigate("/data-sources")}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Review"
        description="Review your transaction data before running financial analysis"
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SectionCard title="Total Transactions">
          <p className="text-2xl font-semibold text-slate-800">{transactions.length}</p>
        </SectionCard>
        <SectionCard title="Date Range">
          <p className="text-sm text-slate-700">
            {dateRange.min && dateRange.max ? `${dateRange.min} – ${dateRange.max}` : "N/A"}
          </p>
        </SectionCard>
        <SectionCard title="Sources">
          <div className="flex flex-wrap gap-1">
            {sources.map((s) => (
              <StatusPill key={s} label={s} variant="default" />
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Transaction Preview">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-3">Date</th>
                <th className="text-left py-2 px-3">Raw Description</th>
                <th className="text-left py-2 px-3">Merchant</th>
                <th className="text-right py-2 px-3">Amount</th>
                <th className="text-left py-2 px-3">Source</th>
                <th className="text-left py-2 px-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 50).map((t) => (
                <tr key={t.transaction_id} className="border-b border-slate-100">
                  <td className="py-2 px-3">{formatDate(t.date)}</td>
                  <td className="py-2 px-3 text-slate-600 truncate max-w-[180px]">{t.merchant}</td>
                  <td className="py-2 px-3">{t.normalized_merchant}</td>
                  <td
                    className={`py-2 px-3 text-right font-medium ${
                      t.amount >= 0 ? "text-emerald-600" : "text-red-600"
                    }`}
                  >
                    {formatCurrency(t.amount)}
                  </td>
                  <td className="py-2 px-3">
                    <StatusPill label={t.source} variant="default" />
                  </td>
                  <td className="py-2 px-3">
                    <StatusPill label="included" variant="success" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {transactions.length > 50 && (
          <p className="text-xs text-slate-500 mt-2">Showing first 50 of {transactions.length}</p>
        )}
      </SectionCard>

      {limitations.length > 0 && (
        <LimitationsCard limitations={limitations} title="Data coverage" />
      )}

      <div className="flex justify-end">
        <Button onClick={handleRunAnalysis}>Run Financial Analysis</Button>
      </div>
    </div>
  );
}
