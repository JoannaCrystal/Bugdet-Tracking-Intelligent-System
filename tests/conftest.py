"""
Shared pytest fixtures for Phase 1 Finance Agentic System tests.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Ensure src is on path when run from project root
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "src"))

# Use SQLite in-memory for tests (set before any DB imports)
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

load_dotenv(_project_root / ".env")


@pytest.fixture(autouse=True)
def _patch_validate_environment():
    """Patch validate_environment so tests run without real API keys."""
    with patch("config.validate_env.validate_environment"):
        yield


@pytest.fixture
def db_session():
    """Database session for tests; rolls back after each test."""
    from database.db import SessionLocal, init_db

    init_db()  # Ensure tables exist (lifespan not run when client not used)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden DB session."""
    from main import app
    from database.db import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def test_user() -> dict:
    """Test user object for finance system initialization."""
    return {
        "user_id": "test_user_001",
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.fixture
def sample_statement_path() -> Path:
    """Path to sample bank statement CSV."""
    return Path(__file__).resolve().parent / "data" / "sample_statement.csv"


@pytest.fixture
def sample_statement(sample_statement_path: Path) -> pd.DataFrame:
    """Sample bank statement as DataFrame."""
    return pd.read_csv(sample_statement_path)


@pytest.fixture
def plaid_config() -> dict:
    """Plaid configuration from environment."""
    return {
        "client_id": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
        "env": os.getenv("PLAID_ENV", "sandbox"),
    }


@pytest.fixture
def sample_transactions():
    """Sample normalized transaction data for deduplication tests."""
    from datetime import datetime

    from schemas.transaction import NormalizedTransaction

    return [
        NormalizedTransaction(
            transaction_id="tx_001",
            date=datetime(2026, 3, 1),
            merchant="STARBUCKS",
            normalized_merchant="starbucks",
            amount=-5.75,
            category="Food & Drink",
            account="Checking",
            source="upload",
        ),
        NormalizedTransaction(
            transaction_id="tx_002",
            date=datetime(2026, 3, 1),
            merchant="STARBUCKS STORE 123",
            normalized_merchant="starbucks",
            amount=-5.75,
            category="Food & Drink",
            account="Checking",
            source="upload",
        ),
        NormalizedTransaction(
            transaction_id="tx_003",
            date=datetime(2026, 3, 2),
            merchant="NETFLIX",
            normalized_merchant="netflix",
            amount=-15.99,
            category="Subscriptions",
            account="Checking",
            source="upload",
        ),
    ]
