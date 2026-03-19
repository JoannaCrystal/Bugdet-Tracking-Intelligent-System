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
import type { CategorySummary } from "../../types/finance";

interface SpendingByCategoryChartProps {
  data: CategorySummary[];
  maxItems?: number;
}

export function SpendingByCategoryChart({
  data,
  maxItems = 10,
}: SpendingByCategoryChartProps) {
  const chartData = data
    .filter((c) => c.total_amount > 0)
    .slice(0, maxItems)
    .map((c) => ({
      name: c.category || "Uncategorized",
      amount: Math.abs(c.total_amount),
    }));

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        No spending data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" tickFormatter={(v) => formatCurrency(v)} />
        <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 12 }} />
        <Tooltip formatter={(v: number) => [formatCurrency(v), "Spend"]} />
        <Bar dataKey="amount" fill="#0d9488" radius={[0, 4, 4, 0]} name="Amount" />
      </BarChart>
    </ResponsiveContainer>
  );
}
