"""
Synthetic transaction generator for the Finance Agentic System.

Uses Faker to generate continuous simulated transactions for testing.
"""

import random
from datetime import datetime, timedelta
from typing import Iterator, List

from faker import Faker
from pydantic import Field

from processing.merchant_normalizer import normalize_merchant
from schemas.transaction import NormalizedTransaction
from utils.logging import get_logger

logger = get_logger(__name__)

# Merchant and category mappings for realistic synthetic data (expenses)
SYNTHETIC_MERCHANTS = [
    ("Amazon", "Shopping"),
    ("Starbucks", "Food & Drink"),
    ("Uber", "Travel"),
    ("Netflix", "Subscriptions"),
    ("Spotify", "Subscriptions"),
    ("Whole Foods", "Food & Drink"),
    ("Target", "Shopping"),
    ("Shell", "Gas & Fuel"),
    ("Apple Store", "Shopping"),
    ("Walmart", "Shopping"),
    ("McDonald's", "Food & Drink"),
    ("Chase", "Bank Fees"),
    ("AT&T", "Subscriptions"),
    ("CVS", "Shopping"),
    ("Chipotle", "Food & Drink"),
]

# Income sources: (description, category)
SYNTHETIC_INCOME_SOURCES = [
    ("Payroll Deposit", "income"),
    ("Salary", "income"),
    ("Freelance Payment", "income"),
    ("Dividends", "investments"),
    ("Interest", "income"),
    ("Refund", "income"),
    ("Reimbursement", "income"),
    ("Venmo Payment Received", "transfers"),
    ("Direct Deposit", "income"),
    ("Side Gig", "income"),
]

# Amount ranges by category for expenses (min, max) in dollars
AMOUNT_RANGES = {
    "Shopping": (5.99, 250.00),
    "Food & Drink": (3.50, 85.00),
    "Travel": (8.00, 75.00),
    "Subscriptions": (4.99, 29.99),
    "Gas & Fuel": (25.00, 80.00),
    "Bank Fees": (0.00, 25.00),
}

# Amount ranges for income (min, max) in dollars
INCOME_AMOUNT_RANGES = {
    "income": (2000.00, 6500.00),      # Payroll, salary, direct deposit
    "investments": (50.00, 400.00),    # Dividends
    "transfers": (25.00, 200.00),      # P2P received
}

# Approximate fraction of transactions that are income (rest are expenses)
INCOME_RATIO = 0.12


class SyntheticTransactionGenerator:
    """
    Generates synthetic transactions continuously using Faker.

    Simulates merchants like Amazon, Starbucks, Uber, Netflix, Spotify, Whole Foods.
    """

    def __init__(self, seed: int | None = None) -> None:
        """
        Initialize the synthetic generator.

        Args:
            seed: Optional seed for reproducible random generation.
        """
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def _generate_transaction_id(self, date: datetime, merchant: str, amount: float) -> str:
        """Generate a unique transaction ID for synthetic transactions."""
        import hashlib
        raw = f"synthetic_{date.isoformat()}_{merchant}_{amount}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def generate_single(
        self,
        date: datetime | None = None,
        merchant: str | None = None,
        amount: float | None = None,
        category: str | None = None,
        force_income: bool | None = None,
    ) -> NormalizedTransaction:
        """
        Generate a single synthetic transaction.

        Args:
            date: Transaction date. Random within last 90 days if not provided.
            merchant: Merchant name. Random from predefined list if not provided.
            amount: Transaction amount. Random based on category if not provided.
            category: Transaction category. Derived from merchant if not provided.
            force_income: If True, generate income; if False, expense; if None, random per INCOME_RATIO.

        Returns:
            NormalizedTransaction instance.
        """
        if date is None:
            date = self.faker.date_time_between(
                start_date="-90d", end_date="now"
            )

        is_income = force_income if force_income is not None else random.random() < INCOME_RATIO

        if is_income:
            merchant, category = random.choice(SYNTHETIC_INCOME_SOURCES)
            normalized_merchant = normalize_merchant(merchant)
            if amount is None:
                range_tuple = INCOME_AMOUNT_RANGES.get(category, (500.00, 3000.00))
                amount = round(random.uniform(range_tuple[0], range_tuple[1]), 2)
        else:
            if merchant is None and category is None:
                merchant, category = random.choice(SYNTHETIC_MERCHANTS)
            elif merchant is None:
                matches = [m for m in SYNTHETIC_MERCHANTS if m[1] == category]
                merchant, _ = random.choice(matches) if matches else SYNTHETIC_MERCHANTS[0]
            elif category is None:
                matches = [m for m in SYNTHETIC_MERCHANTS if m[0] == merchant]
                _, category = matches[0] if matches else ("Other", "Shopping")
            normalized_merchant = normalize_merchant(merchant)
            if amount is None:
                range_tuple = AMOUNT_RANGES.get(category, (1.00, 50.00))
                amount = -round(random.uniform(range_tuple[0], range_tuple[1]), 2)

        transaction_id = self._generate_transaction_id(date, merchant, amount)

        return NormalizedTransaction(
            transaction_id=transaction_id,
            date=date,
            merchant=merchant,
            normalized_merchant=normalized_merchant,
            amount=amount,
            category=category,
            account="Synthetic Checking",
            source="synthetic",
        )

    def generate_batch(self, count: int, days_back: int = 90) -> List[NormalizedTransaction]:
        """
        Generate a batch of synthetic transactions.

        Args:
            count: Number of transactions to generate.
            days_back: How many days back to randomize dates.

        Returns:
            List of NormalizedTransaction instances.
        """
        transactions: List[NormalizedTransaction] = []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        for _ in range(count):
            date = self.faker.date_time_between(
                start_date=start_date,
                end_date=end_date,
            )
            tx = self.generate_single(date=date)
            transactions.append(tx)

        logger.info("Generated %d synthetic transactions.", len(transactions))
        return transactions

    def generate_continuous(
        self,
        interval_seconds: float = 60.0,
        batch_size: int = 1,
    ) -> Iterator[NormalizedTransaction]:
        """
        Continuously yield synthetic transactions at given interval.

        Args:
            interval_seconds: Seconds between transaction batches.
            batch_size: Number of transactions per batch.

        Yields:
            NormalizedTransaction instances.
        """
        import time

        while True:
            for _ in range(batch_size):
                yield self.generate_single()
            time.sleep(interval_seconds)
