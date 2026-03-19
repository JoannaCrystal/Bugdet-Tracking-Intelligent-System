import { Card, CardContent, CardHeader } from "../ui/card";
import { cn } from "../../lib/utils";

interface SummaryCardProps {
  title?: string;
  label?: string;
  value: string | number | null | undefined;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function SummaryCard({ title, label, value, subtitle, trend, className }: SummaryCardProps) {
  const displayTitle = title || label || "";
  const displayValue = value != null ? String(value) : "—";
  const trendColor =
    trend === "up"
      ? "text-emerald-600"
      : trend === "down"
      ? "text-rose-600"
      : "text-slate-700";

  return (
    <Card className={cn("shadow-sm border-slate-200", className)}>
      <CardHeader className="pb-1 pt-4 px-4">
        <p className="text-sm font-medium text-slate-500">{displayTitle}</p>
      </CardHeader>
      <CardContent className="pb-4 px-4">
        <p className={cn("text-2xl font-semibold", trendColor)}>{displayValue}</p>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}
