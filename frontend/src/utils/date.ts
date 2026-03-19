/**
 * Date formatting utilities
 */

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function formatDateShort(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-US", {
      month: "numeric",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function formatDateRange(start: string | null, end: string | null): string {
  const s = start ? formatDate(start) : "?";
  const e = end ? formatDate(end) : "?";
  return `${s} – ${e}`;
}
