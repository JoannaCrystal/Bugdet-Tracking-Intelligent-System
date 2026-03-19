"""
Deduplication engine tests.

Validates duplicate detection, filtering, and unique insert behavior.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from processing.deduplication_engine import DeduplicationEngine, compute_fingerprint
from schemas.transaction import NormalizedTransaction


def test_duplicate_detection_same_transaction() -> None:
    """Verify identical transactions (same date, merchant, amount) are duplicates."""
    tx1 = NormalizedTransaction(
        transaction_id="dup_1",
        date=datetime(2026, 3, 1),
        merchant="STARBUCKS",
        normalized_merchant="starbucks",
        amount=-5.75,
        account="Checking",
        source="upload",
    )
    tx2 = NormalizedTransaction(
        transaction_id="dup_2",
        date=datetime(2026, 3, 1),
        merchant="STARBUCKS STORE 123",
        normalized_merchant="starbucks",
        amount=-5.75,
        account="Checking",
        source="upload",
    )

    # Same normalized_merchant, date, amount, account -> same fingerprint
    fp1 = compute_fingerprint(tx1.date, tx1.normalized_merchant, tx1.amount, tx1.account)
    fp2 = compute_fingerprint(tx2.date, tx2.normalized_merchant, tx2.amount, tx2.account)
    assert fp1 == fp2
    assert tx1.amount == tx2.amount
    assert tx1.date.date() == tx2.date.date()


def test_deduplication_engine_filters_duplicates(sample_transactions) -> None:
    """Verify engine detects and filters duplicate transactions."""
    engine = DeduplicationEngine()
    engine.load_existing([])

    # tx_001 and tx_002 are duplicates (same starbucks, date, amount)
    unique = engine.filter_duplicates(sample_transactions, add_to_cache=True)

    # Should keep 2: one starbucks, one netflix (starbucks dup removed)
    assert len(unique) == 2
    merchants = {t.normalized_merchant for t in unique}
    assert "starbucks" in merchants
    assert "netflix" in merchants


def test_deduplication_ignores_duplicates_on_reinsert(sample_transactions) -> None:
    """Verify re-inserting same transactions yields no new unique items."""
    engine = DeduplicationEngine()
    engine.load_existing([])

    first_pass = engine.filter_duplicates(sample_transactions, add_to_cache=True)
    second_pass = engine.filter_duplicates(sample_transactions, add_to_cache=False)

    assert len(second_pass) == 0, "All should be duplicates on second pass"


def test_deduplication_inserts_only_unique() -> None:
    """Verify only unique transactions pass through filter."""
    from datetime import datetime

    engine = DeduplicationEngine()
    engine.load_existing([])

    txs = [
        NormalizedTransaction(
            transaction_id=f"tx_{i}",
            date=datetime(2026, 3, i),
            merchant=f"MERCHANT_{i}",
            normalized_merchant=f"merchant_{i}",
            amount=-10.0 * (i + 1),
            account="Checking",
            source="upload",
        )
        for i in range(1, 4)
    ]

    unique = engine.filter_duplicates(txs, add_to_cache=True)
    assert len(unique) == 3
