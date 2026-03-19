import { cn } from "../../lib/utils";
import { Card, CardContent, CardHeader } from "../ui/card";

interface LimitationsCardProps {
  limitations: string[];
  title?: string;
  className?: string;
}

export function LimitationsCard({
  limitations,
  title = "Data limitations & coverage",
  className,
}: LimitationsCardProps) {
  if (!limitations?.length) return null;
  return (
    <Card className={cn("border-amber-200 bg-amber-50/50 shadow-sm", className)}>
      <CardHeader className="pb-2">
        <h3 className="text-sm font-medium text-amber-800 flex items-center gap-2">
          <span aria-hidden>⚠</span>
          {title}
        </h3>
      </CardHeader>
      <CardContent>
        <ul className="list-disc list-inside space-y-1 text-sm text-amber-700">
          {limitations.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
