import { cn } from "../../lib/utils";

type StatusVariant = "default" | "neutral" | "success" | "warning" | "error" | "plaid" | "upload" | "synthetic";

interface StatusPillProps {
  label: string;
  variant?: StatusVariant;
  className?: string;
}

const variantStyles: Record<StatusVariant, string> = {
  default: "bg-slate-100 text-slate-700",
  neutral: "bg-slate-100 text-slate-600",
  success: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  error: "bg-red-100 text-red-700",
  plaid: "bg-blue-100 text-blue-700",
  upload: "bg-teal-100 text-teal-700",
  synthetic: "bg-violet-100 text-violet-700",
};

export function StatusPill({ label, variant = "default", className }: StatusPillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {label}
    </span>
  );
}
