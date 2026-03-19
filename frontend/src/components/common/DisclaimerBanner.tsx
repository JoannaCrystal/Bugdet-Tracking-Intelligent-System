import { cn } from "../../lib/utils";

interface DisclaimerBannerProps {
  text: string;
  className?: string;
}

export function DisclaimerBanner({ text, className }: DisclaimerBannerProps) {
  if (!text?.trim()) return null;
  return (
    <div
      className={cn(
        "flex items-start gap-3 p-4 rounded-lg border border-slate-200 bg-slate-50",
        className
      )}
      role="alert"
    >
      <span className="text-slate-500 shrink-0" aria-hidden>
        ℹ
      </span>
      <p className="text-sm text-slate-600">{text}</p>
    </div>
  );
}
