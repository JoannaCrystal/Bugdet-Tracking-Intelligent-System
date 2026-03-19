import { Card, CardContent, CardHeader } from "../ui/card";
import { cn } from "../../lib/utils";
import type { RouterDecision } from "../../types/finance";
import { Bot } from "lucide-react";

interface AgentUsageCardProps {
  routerDecision?: RouterDecision | null;
  className?: string;
}

export function AgentUsageCard({ routerDecision, className }: AgentUsageCardProps) {
  if (!routerDecision) return null;

  const agents = routerDecision.required_agents || [];
  const intent = routerDecision.intent || "unknown";

  return (
    <Card className={cn("shadow-sm border-slate-200 bg-slate-50/50", className)}>
      <CardHeader className="pb-2 pt-4 px-4 flex flex-row items-center gap-2">
        <Bot className="w-4 h-4 text-teal-600" />
        <p className="text-sm font-medium text-slate-700">Agent usage</p>
      </CardHeader>
      <CardContent className="pb-4 px-4 space-y-2">
        <p className="text-xs text-slate-500">
          <span className="font-medium">Intent:</span> {intent}
        </p>
        {agents.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {agents.map((a) => (
              <span
                key={a}
                className="inline-flex items-center rounded-full bg-teal-100 px-2 py-0.5 text-xs font-medium text-teal-700"
              >
                {a}
              </span>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
