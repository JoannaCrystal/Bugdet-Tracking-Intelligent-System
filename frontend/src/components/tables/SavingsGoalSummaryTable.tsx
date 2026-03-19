import type { SavingsPlanResponse } from "../../types/finance";
import { formatCurrency } from "../../utils/format";

interface SavingsGoalSummaryTableProps {
  plan: SavingsPlanResponse;
}

export function SavingsGoalSummaryTable({ plan }: SavingsGoalSummaryTableProps) {
  const status =
    plan.is_achievable === true
      ? "On track"
      : plan.is_achievable === false
      ? "Off track"
      : "Unknown";

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Metric</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">Value</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Goal Amount</td>
            <td className="px-4 py-2.5 text-right text-slate-700">
              {formatCurrency(plan.goal_amount)}
            </td>
          </tr>
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Timeframe</td>
            <td className="px-4 py-2.5 text-right text-slate-700">{plan.target_months} months</td>
          </tr>
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Current Avg Savings</td>
            <td className="px-4 py-2.5 text-right text-slate-700">
              {plan.current_average_savings != null
                ? formatCurrency(plan.current_average_savings)
                : "—"}
            </td>
          </tr>
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Required Per Month</td>
            <td className="px-4 py-2.5 text-right text-slate-700">
              {plan.required_monthly_savings != null
                ? formatCurrency(plan.required_monthly_savings)
                : "—"}
            </td>
          </tr>
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Monthly Gap</td>
            <td
              className={`px-4 py-2.5 text-right font-medium ${
                plan.savings_gap_per_month != null && plan.savings_gap_per_month < 0
                  ? "text-rose-600"
                  : plan.savings_gap_per_month != null && plan.savings_gap_per_month >= 0
                  ? "text-emerald-600"
                  : "text-slate-700"
              }`}
            >
              {plan.savings_gap_per_month != null
                ? formatCurrency(plan.savings_gap_per_month)
                : "—"}
            </td>
          </tr>
          <tr className="hover:bg-slate-50/50">
            <td className="px-4 py-2.5 font-medium text-slate-900">Status</td>
            <td className="px-4 py-2.5 text-right">
              <span
                className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  status === "On track"
                    ? "bg-emerald-100 text-emerald-800"
                    : status === "Off track"
                    ? "bg-rose-100 text-rose-800"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                {status}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
