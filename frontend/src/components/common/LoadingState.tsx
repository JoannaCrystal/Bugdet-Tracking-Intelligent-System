import { cn } from "../../lib/utils";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 gap-4", className)}>
      <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  );
}
