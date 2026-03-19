/**
 * General formatting utilities
 */

import { formatCurrency } from "./currency";
import { formatDate } from "./date";

export { formatCurrency, formatDate };

export function truncate(str: string | null | undefined, maxLen: number): string {
  if (!str) return "";
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + "...";
}

export function capitalize(str: string | null | undefined): string {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}
