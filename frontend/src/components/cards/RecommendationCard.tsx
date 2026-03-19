import { Card, CardContent } from "../ui/card";
import { cn } from "../../lib/utils";
import { Lightbulb } from "lucide-react";

interface RecommendationCardProps {
  recommendation: string;
  area?: string;
  potentialSavings?: number;
  className?: string;
}

export function RecommendationCard({
  recommendation,
  area,
  potentialSavings,
  className,
}: RecommendationCardProps) {
  return (
    <Card className={cn("shadow-sm border-slate-200 bg-amber-50/50", className)}>
      <CardContent className="pt-4 pb-4 px-4 flex gap-3">
        <Lightbulb className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div>
          <p className="text-slate-700 font-medium">{recommendation}</p>
          {area && (
            <p className="text-xs text-slate-500 mt-1">
              Area: {area}
              {potentialSavings != null && (
                <span className="ml-1">
                  • Potential savings: ${potentialSavings.toLocaleString()}
                </span>
              )}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
