import { cn } from "../../lib/utils";
import { Button } from "../ui/button";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 rounded-lg border border-red-100 bg-red-50/50",
        className
      )}
    >
      <h3 className="text-base font-medium text-red-800">{title}</h3>
      <p className="mt-2 text-sm text-red-600 text-center max-w-md">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="mt-4">
          Try again
        </Button>
      )}
    </div>
  );
}
