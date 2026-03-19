import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "../../utils/currency";
import type { SubscriptionItem } from "../../types/finance";

interface SubscriptionCostChartProps {
  subscriptions: SubscriptionItem[];
}

export function SubscriptionCostChart({ subscriptions }: SubscriptionCostChartProps) {
  const data = subscriptions
    .filter((s) => (s.avg_amount ?? s.annual_cost ?? 0) > 0)
    .map((s) => ({
      name: s.merchant,
      monthly: s.avg_amount ?? (s.annual_cost ?? 0) / 12,
      annual: s.annual_cost ?? s.avg_amount ?? 0,
    }));

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        No subscription amounts to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" tickFormatter={(v) => formatCurrency(v)} />
        <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(v: number, name: string) => [
            formatCurrency(v),
            name === "monthly" ? "Monthly" : "Annual",
          ]}
        />
        <Bar dataKey="monthly" fill="#0d9488" radius={[0, 4, 4, 0]} name="monthly" />
      </BarChart>
    </ResponsiveContainer>
  );
}
