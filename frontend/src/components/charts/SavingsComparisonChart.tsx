import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatCurrency } from "../../utils/currency";

interface SavingsComparisonChartProps {
  currentSavings: number;
  requiredSavings: number;
}

export function SavingsComparisonChart({
  currentSavings,
  requiredSavings,
}: SavingsComparisonChartProps) {
  const data = [
    { name: "Current Avg", amount: Math.max(0, currentSavings), fill: "#0d9488" },
    { name: "Required", amount: Math.max(0, requiredSavings), fill: "#64748b" },
  ];

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" />
        <YAxis tickFormatter={(v) => formatCurrency(v)} />
        <Tooltip formatter={(v: number) => [formatCurrency(v), "Amount"]} />
        <Legend />
        <Bar dataKey="amount" name="Monthly" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
