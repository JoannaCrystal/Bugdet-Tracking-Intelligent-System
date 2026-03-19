import { cn } from "../../lib/utils";
import { Button } from "../ui/button";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 rounded-lg border border-dashed border-slate-200 bg-slate-50/50",
        className
      )}
    >
      {icon && <div className="mb-4 text-slate-400">{icon}</div>}
      <h3 className="text-base font-medium text-slate-700">{title}</h3>
      {description && <p className="mt-1 text-sm text-slate-500 text-center max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-4">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
