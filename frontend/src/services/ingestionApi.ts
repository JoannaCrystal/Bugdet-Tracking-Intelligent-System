/**
 * Ingestion API: transactions, Plaid Link, upload, synthetic.
 *
 * Plaid Link flow:
 * 1. createPlaidLinkToken() -> link_token
 * 2. User completes Plaid Link (react-plaid-link)
 * 3. exchangePlaidPublicToken(public_token) -> sync + success
 */

import { apiClient } from "./api";
import type {
  Transaction,
  MonthlySummaryItem,
  PlaidSyncResponse,
  SyntheticIngestResponse,
  UploadStatementResponse,
  CreateLinkTokenRequest,
  CreateLinkTokenResponse,
  ExchangePublicTokenRequest,
  ExchangePublicTokenResponse,
} from "../types/api";

const DEFAULT_USER = "default";

export async function getTransactions(params?: {
  limit?: number;
  offset?: number;
  user_id?: string;
  source?: "plaid" | "upload" | "synthetic";
}): Promise<Transaction[]> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  if (params?.user_id) searchParams.set("user_id", params.user_id);
  if (params?.source) searchParams.set("source", params.source);
  const qs = searchParams.toString();
  const { data } = await apiClient.get<Transaction[]>(`/transactions${qs ? `?${qs}` : ""}`);
  return data;
}

export async function getMonthlySummary(params?: {
  user_id?: string;
  year?: number;
}): Promise<{ summary: MonthlySummaryItem[] }> {
  const searchParams = new URLSearchParams();
  if (params?.user_id) searchParams.set("user_id", params.user_id);
  if (params?.year) searchParams.set("year", String(params.year));
  const qs = searchParams.toString();
  const { data } = await apiClient.get<{ summary: MonthlySummaryItem[] }>(
    `/transactions/monthly-summary${qs ? `?${qs}` : ""}`
  );
  return data;
}

/** Create a short-lived link token for Plaid Link. Backend owns Plaid credentials. */
export async function createPlaidLinkToken(
  payload?: CreateLinkTokenRequest
): Promise<CreateLinkTokenResponse> {
  const { data } = await apiClient.post<CreateLinkTokenResponse>("/plaid/create-link-token", {
    user_id: payload?.user_id ?? DEFAULT_USER,
    use_sample_data: payload?.use_sample_data ?? false,
  });
  return data;
}

/** Exchange Plaid public token for access token and sync transactions. */
export async function exchangePlaidPublicToken(
  payload: ExchangePublicTokenRequest
): Promise<ExchangePublicTokenResponse> {
  const { data } = await apiClient.post<ExchangePublicTokenResponse>(
    "/plaid/exchange-public-token",
    { public_token: payload.public_token, user_id: payload.user_id ?? DEFAULT_USER }
  );
  return data;
}

/** Legacy: sync with raw access token. Use exchangePlaidPublicToken for Plaid Link flow. */
export async function syncPlaid(accessToken: string): Promise<PlaidSyncResponse> {
  const { data } = await apiClient.post<PlaidSyncResponse>("/transactions/sync-plaid", {
    access_token: accessToken,
  });
  return data;
}

export async function uploadStatement(file: File): Promise<UploadStatementResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<UploadStatementResponse>(
    "/transactions/upload-statement",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function ingestSynthetic(params?: {
  count?: number;
  days_back?: number;
}): Promise<SyntheticIngestResponse> {
  const count = params?.count ?? 50;
  const days_back = params?.days_back ?? 90;
  const { data } = await apiClient.post<SyntheticIngestResponse>(
    `/transactions/ingest-synthetic?count=${count}&days_back=${days_back}`
  );
  return data;
}
