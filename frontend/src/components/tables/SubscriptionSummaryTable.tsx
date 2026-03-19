import type { SubscriptionItem } from "../../types/finance";
import { formatCurrency } from "../../utils/format";
import { StatusPill } from "../common/StatusPill";

interface SubscriptionSummaryTableProps {
  subscriptions: SubscriptionItem[];
}

export function SubscriptionSummaryTable({ subscriptions }: SubscriptionSummaryTableProps) {
  if (!subscriptions.length) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-6 text-center text-slate-600">
        No subscriptions detected
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Merchant</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Frequency</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">Avg Amount</th>
            <th className="px-4 py-3 text-right font-medium text-slate-700">Annual Cost</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">Confidence</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {subscriptions.map((s, i) => (
            <tr key={`${s.merchant}-${i}`} className="hover:bg-slate-50/50">
              <td className="px-4 py-2.5 font-medium text-slate-900">{s.merchant}</td>
              <td className="px-4 py-2.5 text-slate-600">{s.frequency || "—"}</td>
              <td className="px-4 py-2.5 text-right text-slate-700">
                {s.avg_amount != null ? formatCurrency(-s.avg_amount) : "—"}
              </td>
              <td className="px-4 py-2.5 text-right text-slate-700">
                {s.annual_cost != null ? formatCurrency(-s.annual_cost) : "—"}
              </td>
              <td className="px-4 py-2.5">
                <StatusPill
                  variant={
                    s.confidence === "high"
                      ? "success"
                      : s.confidence === "medium"
                      ? "warning"
                      : "neutral"
                  }
                  label={s.confidence || "—"}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
