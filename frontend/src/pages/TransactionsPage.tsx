import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTransactions } from "../hooks/useTransactions";
import { PageHeader } from "../components/common/PageHeader";
import { TransactionsTable } from "../components/tables/TransactionsTable";
import { Input } from "../components/ui/input";
import { LoadingState, EmptyState, ErrorState } from "../components/common";

export function TransactionsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState<"all" | "plaid" | "upload" | "synthetic">("all");
  const { transactions, loading, error, refetch } = useTransactions();

  const filtered = transactions.filter((t) => {
    const matchesSearch =
      !search ||
      t.merchant.toLowerCase().includes(search.toLowerCase()) ||
      t.normalized_merchant.toLowerCase().includes(search.toLowerCase()) ||
      (t.category ?? "").toLowerCase().includes(search.toLowerCase());
    const matchesSource =
      sourceFilter === "all" || t.source === sourceFilter;
    return matchesSearch && matchesSource;
  });

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (transactions.length === 0) {
    return (
      <EmptyState
        title="No transactions"
        description="Add data from Data Sources to see transactions."
        actionLabel="Go to Data Sources"
        onAction={() => navigate("/data-sources")}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Transactions"
        description="Browse and filter your transaction history"
      />

      <div className="flex flex-wrap gap-4">
        <Input
          type="search"
          placeholder="Search merchant, category..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value as typeof sourceFilter)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm bg-white"
        >
          <option value="all">All sources</option>
          <option value="plaid">Plaid</option>
          <option value="upload">Upload</option>
          <option value="synthetic">Synthetic</option>
        </select>
      </div>

      <TransactionsTable transactions={filtered} />
    </div>
  );
}
