import { CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "../../lib/utils";

interface FeedbackMessageProps {
  type: "success" | "error";
  message: string;
  className?: string;
}

export function FeedbackMessage({ type, message, className }: FeedbackMessageProps) {
  const isSuccess = type === "success";
  return (
    <p
      className={cn(
        "mt-3 text-sm flex items-center gap-2",
        isSuccess ? "text-teal-700" : "text-red-600",
        className
      )}
    >
      {isSuccess ? (
        <CheckCircle className="h-4 w-4 shrink-0" />
      ) : (
        <AlertCircle className="h-4 w-4 shrink-0" />
      )}
      {message}
    </p>
  );
}
