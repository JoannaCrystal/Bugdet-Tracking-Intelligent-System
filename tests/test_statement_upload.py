"""
Statement upload and CSV parsing tests.

Validates reading, parsing, and schema of bank statement uploads.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ingestion.csv_parser import CSVParser
from schemas.transaction import NormalizedTransaction


def test_statement_csv_readable(sample_statement) -> None:
    """Verify sample statement CSV can be read as DataFrame."""
    import pandas as pd

    assert isinstance(sample_statement, pd.DataFrame)
    assert len(sample_statement) == 4
    cols_lower = [c.lower() for c in sample_statement.columns]
    assert "date" in cols_lower or "date" in sample_statement.columns
    assert "amount" in cols_lower or "amount" in sample_statement.columns
    assert "description" in cols_lower or "description" in sample_statement.columns


def test_statement_parsing(sample_statement_path) -> None:
    """Verify CSVParser parses bank statement into normalized transactions."""
    parser = CSVParser()
    transactions = parser.parse_file(sample_statement_path)

    assert len(transactions) == 4
    assert all(isinstance(tx, NormalizedTransaction) for tx in transactions)


def test_parsed_transaction_schema(sample_statement_path) -> None:
    """Verify parsed transactions have required schema fields."""
    parser = CSVParser()
    transactions = parser.parse_file(sample_statement_path)

    for tx in transactions:
        assert hasattr(tx, "transaction_id")
        assert hasattr(tx, "date")
        assert hasattr(tx, "merchant")
        assert hasattr(tx, "normalized_merchant")
        assert hasattr(tx, "amount")
        assert hasattr(tx, "source")
        assert tx.source == "upload"


def test_merchant_normalization_in_parsing(sample_statement_path) -> None:
    """Verify merchants are normalized during parsing."""
    parser = CSVParser()
    transactions = parser.parse_file(sample_statement_path)

    # STARBUCKS STORE 123 -> starbucks
    starbucks_tx = next((t for t in transactions if "starbucks" in t.normalized_merchant.lower()), None)
    assert starbucks_tx is not None
    assert starbucks_tx.normalized_merchant == "starbucks"
