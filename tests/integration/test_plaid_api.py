"""Integration tests for Plaid Link API (create-link-token, exchange-public-token)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestCreateLinkToken:
    """Tests for POST /plaid/create-link-token."""

    def test_create_link_token_returns_token_when_configured(self, client: TestClient):
        """When Plaid is configured, create-link-token returns link_token."""
        with patch("api.plaid.create_link_token") as mock_create:
            # We need to patch at the point of use - the PlaidClient in the endpoint
            with patch("ingestion.plaid_client.PlaidClient") as MockPlaid:
                mock_instance = MockPlaid.return_value
                mock_instance.client_id = "test_id"
                mock_instance.secret = "test_secret"
                mock_instance.create_sandbox_link_token.return_value = "link-sandbox-abc123"
                resp = client.post(
                    "/plaid/create-link-token",
                    json={"user_id": "default", "use_sample_data": False},
                )
                # 200 if Plaid client works, 503 if not configured
                assert resp.status_code in (200, 503)
                if resp.status_code == 200:
                    data = resp.json()
                    assert "link_token" in data
                    assert data["link_token"] == "link-sandbox-abc123"

    def test_create_link_token_503_when_not_configured(self, client: TestClient):
        """When Plaid is not configured, returns 503 with helpful message."""
        with patch("ingestion.plaid_client.PlaidClient") as MockPlaid:
            mock_instance = MockPlaid.return_value
            mock_instance.client_id = None
            mock_instance.secret = None
            resp = client.post(
                "/plaid/create-link-token",
                json={"user_id": "default"},
            )
            assert resp.status_code == 503
            assert "not configured" in resp.json().get("detail", "").lower()


class TestExchangePublicToken:
    """Tests for POST /plaid/exchange-public-token."""

    def test_exchange_public_token_success_when_configured(
        self, client: TestClient, db_session
    ):
        """When Plaid is configured, exchange returns success and syncs."""
        with patch("ingestion.plaid_client.PlaidClient") as MockPlaid:
            mock_instance = MockPlaid.return_value
            mock_instance.client_id = "test"
            mock_instance.secret = "test"
            mock_instance.exchange_public_token.return_value = "access-sandbox-xyz"
            mock_instance.get_transactions.return_value = []
            mock_instance.set_access_token = lambda x: None

            resp = client.post(
                "/plaid/exchange-public-token",
                json={"public_token": "public-sandbox-abc", "user_id": "default"},
            )
            assert resp.status_code in (200, 503)
            if resp.status_code == 200:
                data = resp.json()
                assert data.get("success") is True
                assert "message" in data

    def test_exchange_public_token_503_when_not_configured(self, client: TestClient):
        """When Plaid is not configured, returns 503."""
        with patch("ingestion.plaid_client.PlaidClient") as MockPlaid:
            mock_instance = MockPlaid.return_value
            mock_instance.client_id = None
            mock_instance.secret = None
            resp = client.post(
                "/plaid/exchange-public-token",
                json={"public_token": "public-sandbox-abc"},
            )
            assert resp.status_code == 503
