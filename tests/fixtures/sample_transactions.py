"""
Sample transaction fixtures for Finance Agentic System tests.

Includes: payroll/income, rent, groceries, dining, utilities, subscriptions,
shopping, transfers, investment, ambiguous merchants.
"""

from datetime import datetime, timedelta

# Realistic sample transactions by category
SAMPLE_PAYROLL = {
    "transaction_id": "tx_payroll_001",
    "date": datetime(2026, 3, 15),
    "merchant": "ACME CORP PAYROLL",
    "normalized_merchant": "acme corp payroll",
    "amount": 4500.00,
    "category": "income",
    "account": "Checking",
    "source": "plaid",
}

SAMPLE_RENT = {
    "transaction_id": "tx_rent_001",
    "date": datetime(2026, 3, 1),
    "merchant": "RENT PAYMENT LANDLORD",
    "normalized_merchant": "rent payment landlord",
    "amount": -1850.00,
    "category": "rent",
    "account": "Checking",
    "source": "upload",
}

SAMPLE_GROCERIES = [
    {
        "transaction_id": "tx_grocery_001",
        "date": datetime(2026, 3, 5),
        "merchant": "WHOLE FOODS",
        "normalized_merchant": "whole foods",
        "amount": -87.42,
        "category": "groceries",
        "account": "Checking",
        "source": "plaid",
    },
    {
        "transaction_id": "tx_grocery_002",
        "date": datetime(2026, 3, 12),
        "merchant": "TRADER JOES",
        "normalized_merchant": "trader joes",
        "amount": -52.30,
        "category": "groceries",
        "account": "Checking",
        "source": "plaid",
    },
]

SAMPLE_DINING = [
    {
        "transaction_id": "tx_dining_001",
        "date": datetime(2026, 3, 3),
        "merchant": "STARBUCKS STORE 123",
        "normalized_merchant": "starbucks",
        "amount": -5.75,
        "category": "dining",
        "account": "Checking",
        "source": "upload",
    },
    {
        "transaction_id": "tx_dining_002",
        "date": datetime(2026, 3, 8),
        "merchant": "UBER EATS",
        "normalized_merchant": "uber eats",
        "amount": -32.50,
        "category": "dining",
        "account": "Checking",
        "source": "plaid",
    },
]

SAMPLE_UTILITIES = {
    "transaction_id": "tx_util_001",
    "date": datetime(2026, 3, 10),
    "merchant": "CON EDISON",
    "normalized_merchant": "con edison",
    "amount": -125.00,
    "category": "utilities",
    "account": "Checking",
    "source": "plaid",
}

SAMPLE_SUBSCRIPTIONS = [
    {
        "transaction_id": "tx_netflix_001",
        "date": datetime(2026, 3, 2),
        "merchant": "NETFLIX.COM",
        "normalized_merchant": "netflix",
        "amount": -15.99,
        "category": "subscriptions",
        "account": "Checking",
        "source": "plaid",
    },
    {
        "transaction_id": "tx_netflix_002",
        "date": datetime(2026, 4, 2),
        "merchant": "NETFLIX.COM",
        "normalized_merchant": "netflix",
        "amount": -15.99,
        "category": "subscriptions",
        "account": "Checking",
        "source": "plaid",
    },
    {
        "transaction_id": "tx_spotify_001",
        "date": datetime(2026, 3, 5),
        "merchant": "SPOTIFY",
        "normalized_merchant": "spotify",
        "amount": -9.99,
        "category": "subscriptions",
        "account": "Checking",
        "source": "plaid",
    },
]

SAMPLE_SHOPPING = {
    "transaction_id": "tx_shop_001",
    "date": datetime(2026, 3, 7),
    "merchant": "AMAZON",
    "normalized_merchant": "amazon",
    "amount": -89.99,
    "category": "shopping",
    "account": "Checking",
    "source": "plaid",
}

SAMPLE_TRANSFER = {
    "transaction_id": "tx_transfer_001",
    "date": datetime(2026, 3, 14),
    "merchant": "VENMO",
    "normalized_merchant": "venmo",
    "amount": -50.00,
    "category": "transfers",
    "account": "Checking",
    "source": "plaid",
}

SAMPLE_INVESTMENT = {
    "transaction_id": "tx_inv_001",
    "date": datetime(2026, 3, 1),
    "merchant": "VANGUARD",
    "normalized_merchant": "vanguard",
    "amount": -500.00,
    "category": "investments",
    "account": "Brokerage",
    "source": "plaid",
}

# Ambiguous merchants (hard to categorize)
SAMPLE_AMBIGUOUS = [
    {
        "transaction_id": "tx_ambig_001",
        "date": datetime(2026, 3, 6),
        "merchant": "SQ *MERCHANT XYZ",
        "normalized_merchant": "sq merchant xyz",
        "amount": -24.99,
        "category": None,
        "account": "Checking",
        "source": "upload",
    },
    {
        "transaction_id": "tx_ambig_002",
        "date": datetime(2026, 3, 9),
        "merchant": "POS PURCHASE 123456",
        "normalized_merchant": "pos purchase 123456",
        "amount": -12.00,
        "category": None,
        "account": "Checking",
        "source": "upload",
    },
]


def get_full_sample_transactions():
    """Return a complete list of sample transactions."""
    return [
        SAMPLE_PAYROLL,
        SAMPLE_RENT,
        SAMPLE_UTILITIES,
        SAMPLE_SHOPPING,
        SAMPLE_TRANSFER,
        SAMPLE_INVESTMENT,
        *SAMPLE_GROCERIES,
        *SAMPLE_DINING,
        *SAMPLE_SUBSCRIPTIONS,
        *SAMPLE_AMBIGUOUS,
    ]


def get_short_incomplete_dataset():
    """Minimal dataset (too short for reliable analysis)."""
    return [SAMPLE_PAYROLL, SAMPLE_RENT]  # Only 2 transactions


def get_duplicate_transactions():
    """Same transaction repeated (for dedup tests)."""
    base = dict(SAMPLE_NETFLIX)
    return [
        {**base, "transaction_id": "dup_netflix_1"},
        {**base, "transaction_id": "dup_netflix_2"},
    ]


# Alias for subscription
SAMPLE_NETFLIX = SAMPLE_SUBSCRIPTIONS[0]


def get_mixed_source_overlap():
    """Overlap between plaid and upload (same merchant, similar amount)."""
    return [
        {
            **SAMPLE_SUBSCRIPTIONS[0],
            "transaction_id": "plaid_netflix_001",
            "source": "plaid",
        },
        {
            **SAMPLE_SUBSCRIPTIONS[0],
            "transaction_id": "upload_netflix_001",
            "merchant": "NETFLIX",
            "source": "upload",
        },
    ]
