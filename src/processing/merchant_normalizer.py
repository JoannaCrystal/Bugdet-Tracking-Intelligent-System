"""
Merchant normalization for the Finance Agentic System.

Cleans merchant strings by removing numbers, punctuation, and store IDs.
"""

import re
from typing import Optional

from utils.logging import get_logger

logger = get_logger(__name__)

# Pattern to match store IDs like #123, Store 456, Unit 789
STORE_ID_PATTERN = re.compile(
    r"\s*(?:store\s*#?|#|number\s*|no\.?\s*|unit\s*)\s*\d+[\w-]*",
    re.IGNORECASE,
)
# Pattern to match trailing numbers (e.g., last 4 of card, reference numbers)
TRAILING_NUMBERS = re.compile(r"\s+\d{4,}\s*$")
# Punctuation and extra whitespace
PUNCTUATION = re.compile(r"[^\w\s-]")
MULTI_SPACE = re.compile(r"\s+")


def normalize_merchant(merchant: str) -> str:
    """
    Normalize a merchant string for consistent matching and deduplication.

    Operations:
    - Remove store IDs (e.g., "STORE #123")
    - Remove trailing long numbers
    - Remove punctuation
    - Convert to lowercase
    - Collapse multiple spaces

    Args:
        merchant: Raw merchant string from source.

    Returns:
        Normalized merchant string.

    Example:
        >>> normalize_merchant("STARBUCKS STORE #123")
        'starbucks'
    """
    if not merchant or not isinstance(merchant, str):
        return "unknown"

    s = merchant.strip()
    s = STORE_ID_PATTERN.sub("", s)
    s = TRAILING_NUMBERS.sub("", s)
    s = PUNCTUATION.sub(" ", s)
    s = s.lower()
    s = MULTI_SPACE.sub(" ", s)
    s = s.strip()

    return s if s else "unknown"
