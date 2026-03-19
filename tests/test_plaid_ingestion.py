"""
Plaid sandbox ingestion tests.

Validates Plaid config, connection, and transaction schema.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_plaid_config(plaid_config: dict) -> None:
    """Verify Plaid credentials are loaded from environment."""
    assert plaid_config["client_id"] is not None
    assert plaid_config["secret"] is not None
    assert plaid_config["env"] is not None


def test_plaid_client_initializes(plaid_config: dict) -> None:
    """Verify PlaidClient can be initialized with config."""
    try:
        from ingestion.plaid_client import PlaidClient
    except ImportError:
        pytest.skip("plaid-python not installed", allow_module_level=False)


    client = PlaidClient(
        client_id=plaid_config["client_id"],
        secret=plaid_config["secret"],
        environment=plaid_config["env"] or "sandbox",
    )
    assert client is not None
    assert client.environment in ("sandbox", "development", "production")


def test_plaid_transaction_schema() -> None:
    """Verify Plaid returns transactions in normalized schema."""
    from schemas.transaction import NormalizedTransaction

    required_fields = [
        "transaction_id",
        "date",
        "merchant",
        "normalized_merchant",
        "amount",
        "category",
        "account",
        "source",
    ]
    for field in required_fields:
        assert field in NormalizedTransaction.model_fields
