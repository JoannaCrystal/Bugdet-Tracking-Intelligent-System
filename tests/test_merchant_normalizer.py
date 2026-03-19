"""
Tests for merchant normalizer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from processing.merchant_normalizer import normalize_merchant


def test_normalize_starbucks_store():
    """STARBUCKS STORE #123 -> starbucks"""
    assert normalize_merchant("STARBUCKS STORE #123") == "starbucks"


def test_normalize_lowercase():
    """Convert to lowercase."""
    assert normalize_merchant("AMAZON") == "amazon"


def test_normalize_empty():
    """Empty or invalid returns unknown."""
    assert normalize_merchant("") == "unknown"
    assert normalize_merchant("   ") == "unknown"
