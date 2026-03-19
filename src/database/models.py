"""
SQLAlchemy database models for the Finance Agentic System.

Defines the transactions table and related schemas.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Transaction(Base):
    """
    Transaction model representing a financial transaction.

    Attributes:
        transaction_id: Unique identifier for the transaction.
        date: Transaction date.
        merchant: Original merchant name as provided by source.
        normalized_merchant: Cleaned/normalized merchant name.
        amount: Transaction amount (negative for debits).
        category: Transaction category.
        account: Account identifier.
        source: Data source (plaid, upload, synthetic).
        created_at: Record creation timestamp.
    """

    __tablename__ = "transactions"

    transaction_id = Column(String(64), primary_key=True)
    date = Column(DateTime, nullable=False)
    merchant = Column(String(255), nullable=False)
    normalized_merchant = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    account = Column(String(100), nullable=True)
    source = Column(String(50), nullable=False)  # plaid, upload, synthetic
    created_at = Column(DateTime, default=datetime.utcnow)

    # Phase 2 extensions
    user_id = Column(String(64), nullable=True, default="default")
    category_confidence = Column(Float, nullable=True)
    is_subscription = Column(Boolean, nullable=True, default=False)
    subscription_confidence = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction(id={self.transaction_id}, merchant={self.normalized_merchant}, amount={self.amount})>"
