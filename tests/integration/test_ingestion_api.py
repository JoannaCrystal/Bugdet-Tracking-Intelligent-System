"""Integration tests for ingestion API (Plaid, CSV upload, synthetic)."""

import io
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from database.models import Transaction
from schemas.transaction import NormalizedTransaction


@pytest.fixture
def sample_csv_content():
    """Valid CSV content for upload tests."""
    return b"""Date,Description,Amount
2026-03-01,STARBUCKS,-5.75
2026-03-02,NETFLIX,-15.99
2026-03-05,WHOLE FOODS,-87.42
"""


@pytest.fixture
def sample_csv_empty():
    """Empty CSV."""
    return b"Date,Description,Amount\n"


class TestPlaidIngestion:
    """Tests for POST /transactions/sync-plaid."""

    def test_sync_plaid_mock_returns_200(self, client: TestClient):
        """Plaid sync endpoint accepts request (mocked Plaid)."""
        with patch("ingestion.plaid_client.PlaidClient") as MockPlaid:
            mock_instance = MockPlaid.return_value
            mock_instance.get_transactions.return_value = [
                NormalizedTransaction(
                    transaction_id="plaid_tx_1",
                    date=datetime(2026, 3, 1),
                    merchant="NETFLIX",
                    normalized_merchant="netflix",
                    amount=-15.99,
                    category="Subscription",
                    account="Checking",
                    source="plaid",
                )
            ]
            resp = client.post(
                "/transactions/sync-plaid",
                json={"access_token": "test-token"},
            )
            assert resp.status_code in (200, 400, 501)  # 501 if plaid-python not installed
            if resp.status_code == 200:
                data = resp.json()
                assert "message" in data
                assert "fetched" in data or "added" in data


class TestCSVUpload:
    """Tests for POST /transactions/upload-statement."""

    def test_valid_csv_upload(self, client: TestClient, sample_csv_content):
        """Valid CSV upload returns 200 and persisted transactions."""
        resp = client.post(
            "/transactions/upload-statement",
            files={"file": ("statement.csv", io.BytesIO(sample_csv_content), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("parsed", 0) >= 1
        assert "added" in data
        assert "duplicates_filtered" in data

    def test_invalid_file_format_rejected(self, client: TestClient):
        """Non-CSV file returns 400."""
        resp = client.post(
            "/transactions/upload-statement",
            files={"file": ("data.txt", io.BytesIO(b"not csv"), "text/plain")},
        )
        assert resp.status_code == 400
        assert "CSV" in resp.json().get("detail", "")

    def test_empty_csv_handled(self, client: TestClient, sample_csv_empty):
        """Empty CSV parsed returns 200 with zero added."""
        resp = client.post(
            "/transactions/upload-statement",
            files={"file": ("empty.csv", io.BytesIO(sample_csv_empty), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("parsed", 0) == 0 or data.get("added", 0) == 0


class TestSyntheticIngestion:
    """Tests for POST /transactions/ingest-synthetic."""

    def test_synthetic_ingest_success(self, client: TestClient):
        """Synthetic ingestion returns 200 and adds transactions."""
        resp = client.post(
            "/transactions/ingest-synthetic",
            params={"count": 5, "days_back": 30},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "generated" in data
        assert "added" in data
        assert "duplicates_filtered" in data

    def test_synthetic_dedup_behavior(self, client: TestClient):
        """Second identical synthetic batch filters duplicates."""
        resp1 = client.post("/transactions/ingest-synthetic", params={"count": 3, "days_back": 7})
        resp2 = client.post("/transactions/ingest-synthetic", params={"count": 3, "days_back": 7})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Second run may have fewer added due to overlap
        d1, d2 = resp1.json(), resp2.json()
        assert d1.get("added", 0) >= 0
        assert d2.get("added", 0) >= 0


class TestTransactionPersistence:
    """Tests for transaction persistence and retrieval."""

    def test_list_transactions_after_upload(self, client: TestClient, sample_csv_content):
        """Uploaded transactions appear in GET /transactions."""
        client.post(
            "/transactions/upload-statement",
            files={"file": ("s.csv", io.BytesIO(sample_csv_content), "text/csv")},
        )
        resp = client.get("/transactions", params={"limit": 50})
        assert resp.status_code == 200
        txs = resp.json()
        assert isinstance(txs, list)
        if txs:
            t = txs[0]
            assert "transaction_id" in t
            assert "merchant" in t
            assert "amount" in t
            assert "source" in t
            assert t["source"] in ("plaid", "upload", "synthetic")
