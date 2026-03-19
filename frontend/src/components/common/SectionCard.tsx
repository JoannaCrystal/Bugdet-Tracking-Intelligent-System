import { cn } from "../../lib/utils";
import { Card, CardContent, CardHeader } from "../ui/card";

interface SectionCardProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function SectionCard({ title, description, children, className }: SectionCardProps) {
  return (
    <Card className={cn("shadow-sm border-slate-200", className)}>
      {(title || description) && (
        <CardHeader className="pb-2">
          {title && <h2 className="text-lg font-medium text-slate-900">{title}</h2>}
          {description && <p className="text-sm text-slate-500 mt-1">{description}</p>}
        </CardHeader>
      )}
      <CardContent>{children}</CardContent>
    </Card>
  );
}
