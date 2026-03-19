import { Card, CardContent, CardHeader } from "../ui/card";
import { cn } from "../../lib/utils";

interface InsightCardProps {
  title: string;
  content?: string;
  summary?: string;
  caveats?: string[];
  icon?: React.ReactNode;
  className?: string;
}

export function InsightCard({ title, content, summary, caveats, icon, className }: InsightCardProps) {
  const body = content ?? summary ?? "";
  return (
    <Card className={cn("shadow-sm border-slate-200", className)}>
      <CardHeader className="pb-1 pt-4 px-4 flex flex-row items-center gap-2">
        {icon && <span className="text-teal-500">{icon}</span>}
        <p className="text-sm font-medium text-slate-700">{title}</p>
      </CardHeader>
      <CardContent className="pb-4 px-4">
        {body && <p className="text-slate-600 text-sm leading-relaxed">{body}</p>}
        {caveats && caveats.length > 0 && (
          <ul className="mt-2 list-disc list-inside text-xs text-slate-500 space-y-1">
            {caveats.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
