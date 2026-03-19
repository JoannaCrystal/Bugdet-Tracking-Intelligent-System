import type { CategorySummary } from "../../types/finance";
import { formatCurrency } from "../../utils/format";

interface CategorySummaryTableProps {
  categories: CategorySummary[];
  totalExpenses: number;
}

export function CategorySummaryTable({ categories = [], totalExpenses }: CategorySummaryTableProps) {
  const safeCategories = categories ?? [];
  if (!safeCategories.length) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-6 text-center text-slate-600">
        No category data
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Category</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">Amount</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">% of Expenses</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {categories.map((c) => {
            const pct = totalExpenses > 0 ? (c.total_amount / totalExpenses) * 100 : 0;
            return (
              <tr key={c.category} className="hover:bg-slate-50/50">
                <td className="px-4 py-2.5 font-medium text-slate-900">{c.category}</td>
                <td className="px-4 py-2.5 text-right text-slate-700">
                  {formatCurrency(-Math.abs(c.total_amount))}
                </td>
                <td className="px-4 py-2.5 text-right text-slate-600">{pct.toFixed(1)}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
