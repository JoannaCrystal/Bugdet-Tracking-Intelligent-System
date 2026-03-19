import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { formatCurrency } from "../../utils/currency";

interface IncomeExpenseSavingsChartProps {
  income: number;
  expenses: number;
  savings: number;
}

const COLORS = ["#0d9488", "#dc2626", "#22c55e"];

export function IncomeExpenseSavingsChart({
  income,
  expenses,
  savings,
}: IncomeExpenseSavingsChartProps) {
  const data = [
    { name: "Income", value: Math.max(0, income) },
    { name: "Expenses", value: Math.abs(Math.min(0, expenses)) },
    { name: "Savings", value: Math.max(0, savings) },
  ].filter((d) => d.value > 0);

  if (data.every((d) => d.value === 0)) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        No data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
          label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v: number) => formatCurrency(v)} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
