/**
 * API response types aligned with backend.
 */

export interface Transaction {
  transaction_id: string;
  date: string;
  merchant: string;
  normalized_merchant: string;
  amount: number;
  category: string | null;
  account: string | null;
  source: "plaid" | "upload" | "synthetic";
  created_at: string;
}

export interface MonthlySummaryItem {
  year: number;
  month: number;
  total_amount: number;
  transaction_count: number;
}

export interface PlaidSyncResponse {
  message: string;
  fetched: number;
  duplicates_filtered: number;
  added: number;
}

export interface CreateLinkTokenRequest {
  user_id?: string;
  use_sample_data?: boolean;
}

export interface CreateLinkTokenResponse {
  link_token: string;
  expiration?: string | null;
}

export interface ExchangePublicTokenRequest {
  public_token: string;
  user_id?: string;
}

export interface ExchangePublicTokenResponse {
  success: boolean;
  item_id?: string | null;
  message: string;
  added?: number | null;
}

export interface SyntheticIngestResponse {
  message: string;
  generated: number;
  duplicates_filtered: number;
  added: number;
}

export interface UploadStatementResponse {
  message: string;
  parsed: number;
  duplicates_filtered: number;
  added: number;
}
