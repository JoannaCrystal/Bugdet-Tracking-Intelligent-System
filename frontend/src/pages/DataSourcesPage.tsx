import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePlaidLink } from "react-plaid-link";
import { PageHeader } from "../components/common/PageHeader";
import { SectionCard } from "../components/common/SectionCard";
import { Button } from "../components/ui/button";
import { FileUploadBox } from "../components/forms/FileUploadBox";
import { SyntheticDataForm } from "../components/forms/SyntheticDataForm";
import {
  createPlaidLinkToken,
  exchangePlaidPublicToken,
  uploadStatement,
  ingestSynthetic,
} from "../services/ingestionApi";
import { Link2 } from "lucide-react";

const DEFAULT_USER = "default";

export function DataSourcesPage() {
  const navigate = useNavigate();

  // Plaid Link state
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [plaidTokenLoading, setPlaidTokenLoading] = useState(false);
  const [plaidError, setPlaidError] = useState<string | null>(null);
  const [plaidSuccess, setPlaidSuccess] = useState<{ message: string; added?: number } | null>(null);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ message: string; added: number } | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Synthetic state
  const [syntheticLoading, setSyntheticLoading] = useState(false);
  const [syntheticResult, setSyntheticResult] = useState<{ message: string; added: number } | null>(null);
  const [syntheticError, setSyntheticError] = useState<string | null>(null);

  const onPlaidSuccess = useCallback(
    async (publicToken: string) => {
      setPlaidError(null);
      try {
        const res = await exchangePlaidPublicToken({
          public_token: publicToken,
          user_id: DEFAULT_USER,
        });
        setPlaidSuccess({
          message: res.message,
          added: res.added ?? undefined,
        });
        setLinkToken(null);
        // Refresh after short delay; user can navigate to Data Review
        setTimeout(() => navigate("/data-review"), 1500);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to connect account";
        setPlaidError(msg);
      }
    },
    [navigate]
  );

  const { open: openPlaidLink, ready: plaidReady } = usePlaidLink({
    token: linkToken,
    onSuccess: onPlaidSuccess,
    onExit: (_err, _metadata) => {
      setPlaidTokenLoading(false);
    },
  });

  // When linkToken is set and Plaid is ready, open Link
  useEffect(() => {
    if (linkToken && plaidReady) {
      openPlaidLink();
    }
  }, [linkToken, plaidReady, openPlaidLink]);

  const handleConnectPlaid = useCallback(async () => {
    setPlaidError(null);
    setPlaidSuccess(null);
    setPlaidTokenLoading(true);
    try {
      const res = await createPlaidLinkToken({
        user_id: DEFAULT_USER,
        use_sample_data: false,
      });
      setLinkToken(res.link_token);
    } catch (e) {
      setPlaidTokenLoading(false);
      const msg = e instanceof Error ? e.message : "Failed to get Plaid link";
      if (msg.includes("not configured") || msg.includes("503")) {
        setPlaidError(
          "Plaid sandbox is not configured yet. Use Upload Statement or Generate Demo Data instead."
        );
      } else {
        setPlaidError(msg);
      }
    }
  }, []);

  const handleUpload = useCallback(async (file: File) => {
    setUploadError(null);
    setUploadResult(null);
    setUploading(true);
    try {
      const res = await uploadStatement(file);
      setUploadResult({ message: res.message, added: res.added });
      setTimeout(() => navigate("/data-review"), 1500);
    } catch (e) {
      setUploadError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const handleSynthetic = useCallback(
    async (count: number, daysBack: number) => {
      setSyntheticError(null);
      setSyntheticResult(null);
      setSyntheticLoading(true);
      try {
        const res = await ingestSynthetic({ count, days_back: daysBack });
        setSyntheticResult({ message: res.message, added: res.added });
        setTimeout(() => navigate("/data-review"), 1500);
      } catch (e) {
        setSyntheticError(e instanceof Error ? e.message : "Generate failed");
      } finally {
        setSyntheticLoading(false);
      }
    },
    [navigate]
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Sources"
        description="Connect Plaid, upload a CSV statement, or generate demo data to get started"
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Plaid Sandbox */}
        <SectionCard title="Connect with Plaid Sandbox" className="flex flex-col">
          <p className="text-sm text-slate-600 mb-4">
            Connect a sandbox bank account via Plaid to import transactions. The backend owns Plaid
            credentials—no manual token setup needed.
          </p>
          {plaidError && (
            <p className="text-sm text-red-600 mb-4 p-3 rounded-md bg-red-50" role="alert">
              {plaidError}
            </p>
          )}
          {plaidSuccess && (
            <p className="text-sm text-emerald-700 mb-4 p-3 rounded-md bg-emerald-50" role="status">
              {plaidSuccess.message}
              {plaidSuccess.added != null && ` ${plaidSuccess.added} transactions synced.`}
            </p>
          )}
          <Button
            onClick={handleConnectPlaid}
            disabled={plaidTokenLoading}
            className="mt-auto"
          >
            {plaidTokenLoading ? (
              <>
                <span className="animate-pulse">Loading…</span>
              </>
            ) : (
              <>
                <Link2 className="mr-2 h-4 w-4" />
                Connect with Plaid Sandbox
              </>
            )}
          </Button>
        </SectionCard>

        {/* Upload Statement */}
        <SectionCard title="Upload Statement" className="flex flex-col">
          <p className="text-sm text-slate-600 mb-4">
            Upload a CSV bank statement. Date, Description, Amount columns are expected.
          </p>
          {uploadError && (
            <p className="text-sm text-red-600 mb-4 p-3 rounded-md bg-red-50" role="alert">
              {uploadError}
            </p>
          )}
          {uploadResult && (
            <p className="text-sm text-emerald-700 mb-4 p-3 rounded-md bg-emerald-50" role="status">
              {uploadResult.message} {uploadResult.added} new transactions added.
            </p>
          )}
          <div className="mt-auto">
            <FileUploadBox
              onUpload={handleUpload}
              disabled={uploading}
              accept=".csv"
            />
          </div>
        </SectionCard>

        {/* Generate Demo Data */}
        <SectionCard title="Generate Demo Data" className="flex flex-col">
          <p className="text-sm text-slate-600 mb-4">
            Create synthetic transactions for testing. Uses common merchants like Amazon, Netflix,
            Starbucks.
          </p>
          {syntheticError && (
            <p className="text-sm text-red-600 mb-4 p-3 rounded-md bg-red-50" role="alert">
              {syntheticError}
            </p>
          )}
          {syntheticResult && (
            <p className="text-sm text-emerald-700 mb-4 p-3 rounded-md bg-emerald-50" role="status">
              {syntheticResult.message} {syntheticResult.added} transactions added.
            </p>
          )}
          <div className="mt-auto">
            <SyntheticDataForm
              onSubmit={handleSynthetic}
              isLoading={syntheticLoading}
              disabled={syntheticLoading}
            />
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
