"""
Deduplication engine for the Finance Agentic System.

Uses transaction fingerprinting (SHA256) and fuzzy matching (RapidFuzz)
to identify and filter duplicate transactions.
"""

import hashlib
from datetime import datetime
from typing import List, Optional, Set

from rapidfuzz.fuzz import ratio

from schemas.transaction import NormalizedTransaction
from utils.logging import get_logger

logger = get_logger(__name__)

FUZZY_SIMILARITY_THRESHOLD = 85


def _fingerprint_fields(date: datetime, normalized_merchant: str, amount: float, account: str) -> str:
    """
    Build fingerprint string from key transaction fields.

    Args:
        date: Transaction date.
        normalized_merchant: Normalized merchant name.
        amount: Transaction amount.
        account: Account identifier.

    Returns:
        Concatenated string for hashing.
    """
    date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
    account_val = account or ""
    return f"{date_str}|{normalized_merchant}|{amount}|{account_val}"


def compute_fingerprint(
    date: datetime,
    normalized_merchant: str,
    amount: float,
    account: Optional[str] = None,
) -> str:
    """
    Compute SHA256 fingerprint for a transaction.

    Fingerprint fields: date, normalized_merchant, amount, account.

    Args:
        date: Transaction date.
        normalized_merchant: Normalized merchant name.
        amount: Transaction amount.
        account: Account identifier.

    Returns:
        SHA256 hash hex string.
    """
    raw = _fingerprint_fields(date, normalized_merchant, amount, account or "")
    return hashlib.sha256(raw.encode()).hexdigest()


class DeduplicationEngine:
    """
    Deduplication engine using fingerprint and fuzzy matching.

    Two mechanisms:
    1. Exact fingerprint match: same date, normalized_merchant, amount, account.
    2. Fuzzy match: merchant similarity > 85, same amount, same date.
    """

    def __init__(self, similarity_threshold: int = FUZZY_SIMILARITY_THRESHOLD) -> None:
        """
        Initialize deduplication engine.

        Args:
            similarity_threshold: Minimum similarity score for fuzzy match (0-100).
        """
        self.similarity_threshold = similarity_threshold
        self._fingerprint_cache: Set[str] = set()
        self._existing_transactions: List[NormalizedTransaction] = []

    def load_existing(self, transactions: List[NormalizedTransaction]) -> None:
        """
        Load existing transactions for deduplication checks.

        Args:
            transactions: List of already-stored transactions.
        """
        self._existing_transactions = list(transactions)
        self._fingerprint_cache = set()
        for tx in transactions:
            fp = compute_fingerprint(
                tx.date,
                tx.normalized_merchant,
                tx.amount,
                tx.account,
            )
            self._fingerprint_cache.add(fp)
        logger.info("Loaded %d existing transactions for deduplication.", len(transactions))

    def _is_fuzzy_duplicate(self, candidate: NormalizedTransaction) -> bool:
        """
        Check if candidate is a fuzzy duplicate of any existing transaction.

        Criteria: merchant similarity > threshold, same amount, same date.

        Args:
            candidate: Transaction to check.

        Returns:
            True if fuzzy duplicate found.
        """
        cand_date = candidate.date.date() if hasattr(candidate.date, "date") else candidate.date
        cand_amount = candidate.amount

        for existing in self._existing_transactions:
            if existing.transaction_id == candidate.transaction_id:
                continue

            ex_date = existing.date.date() if hasattr(existing.date, "date") else existing.date
            if ex_date != cand_date:
                continue
            if abs(existing.amount - cand_amount) > 0.01:
                continue

            score = ratio(
                candidate.normalized_merchant,
                existing.normalized_merchant,
            )
            if score >= self.similarity_threshold:
                logger.debug(
                    "Fuzzy duplicate: %s ~ %s (score=%d)",
                    candidate.normalized_merchant,
                    existing.normalized_merchant,
                    score,
                )
                return True

        return False

    def is_duplicate(self, transaction: NormalizedTransaction) -> bool:
        """
        Check if transaction is a duplicate (fingerprint or fuzzy match).

        Args:
            transaction: Transaction to check.

        Returns:
            True if duplicate, False otherwise.
        """
        fp = compute_fingerprint(
            transaction.date,
            transaction.normalized_merchant,
            transaction.amount,
            transaction.account,
        )
        if fp in self._fingerprint_cache:
            return True
        return self._is_fuzzy_duplicate(transaction)

    def filter_duplicates(
        self,
        transactions: List[NormalizedTransaction],
        add_to_cache: bool = True,
    ) -> List[NormalizedTransaction]:
        """
        Filter duplicate transactions from a list.

        Args:
            transactions: Incoming transactions to filter.
            add_to_cache: If True, add non-duplicates to cache for future checks.

        Returns:
            List of unique (non-duplicate) transactions.
        """
        unique: List[NormalizedTransaction] = []
        duplicates_count = 0

        for tx in transactions:
            if self.is_duplicate(tx):
                duplicates_count += 1
                continue
            unique.append(tx)
            if add_to_cache:
                fp = compute_fingerprint(tx.date, tx.normalized_merchant, tx.amount, tx.account)
                self._fingerprint_cache.add(fp)
                self._existing_transactions.append(tx)

        if duplicates_count > 0:
            logger.info("Filtered %d duplicates from %d transactions.", duplicates_count, len(transactions))

        return unique
