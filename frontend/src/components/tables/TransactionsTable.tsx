import type { Transaction } from "../../types/api";
import { formatCurrency, formatDate } from "../../utils/format";
import { StatusPill } from "../common/StatusPill";
import { cn } from "../../lib/utils";

interface TransactionsTableProps {
  transactions: Transaction[];
  loading?: boolean;
}

export function TransactionsTable({ transactions, loading }: TransactionsTableProps) {
  if (loading) {
    return (
      <div className="animate-pulse rounded-lg border border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
        Loading transactions…
      </div>
    );
  }

  if (!transactions.length) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-8 text-center text-slate-600">
        No transactions found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Date</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Merchant</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Raw Description</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">Amount</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Category</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Source</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {transactions.map((tx) => (
            <tr key={tx.transaction_id} className="hover:bg-slate-50/50">
              <td className="whitespace-nowrap px-4 py-2.5 text-slate-700">
                {formatDate(tx.date)}
              </td>
              <td className="max-w-[180px] truncate px-4 py-2.5 font-medium text-slate-900">
                {tx.normalized_merchant || tx.merchant}
              </td>
              <td className="max-w-[200px] truncate px-4 py-2.5 text-slate-600">
                {tx.merchant}
              </td>
              <td
                className={cn(
                  "whitespace-nowrap px-4 py-2.5 text-right font-medium",
                  tx.amount >= 0 ? "text-emerald-600" : "text-rose-600"
                )}
              >
                {formatCurrency(tx.amount)}
              </td>
              <td className="px-4 py-2.5">
                {tx.category ? (
                  <StatusPill variant="neutral" label={tx.category} />
                ) : (
                  <span className="text-slate-400">—</span>
                )}
              </td>
              <td className="px-4 py-2.5">
                <StatusPill
                  variant={
                    tx.source === "plaid" ? "plaid" : tx.source === "upload" ? "upload" : "synthetic"
                  }
                  label={tx.source}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
