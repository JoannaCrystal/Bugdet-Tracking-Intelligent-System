"""
FastAPI endpoints for transaction management.

Provides GET /transactions, GET /transactions/monthly-summary, POST /upload-statement.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import Integer, cast, func, or_
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Transaction
from ingestion.csv_parser import CSVParser
from services.transaction_query_service import (
    DEFAULT_USER_ID,
    _user_filter,
    get_transactions_for_user,
)
from ingestion.synthetic_generator import SyntheticTransactionGenerator
from processing.deduplication_engine import DeduplicationEngine
from schemas.transaction import NormalizedTransaction
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionResponse(BaseModel):
    """API response schema for a single transaction."""

    transaction_id: str
    date: datetime
    merchant: str
    normalized_merchant: str
    amount: float
    category: Optional[str] = None
    account: Optional[str] = None
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlySummaryItem(BaseModel):
    """Monthly summary item."""

    year: int
    month: int
    total_amount: float
    transaction_count: int


class MonthlySummaryResponse(BaseModel):
    """API response for monthly summary."""

    summary: List[MonthlySummaryItem]


class PlaidSyncRequest(BaseModel):
    """Request body for Plaid sync."""

    access_token: str


def _transaction_to_response(tx: Transaction) -> TransactionResponse:
    """Convert database model to API response."""
    return TransactionResponse(
        transaction_id=tx.transaction_id,
        date=tx.date,
        merchant=tx.merchant,
        normalized_merchant=tx.normalized_merchant,
        amount=tx.amount,
        category=tx.category,
        account=tx.account,
        source=tx.source,
        created_at=tx.created_at,
    )


@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    source: Optional[str] = Query(default=None, pattern="^(plaid|upload|synthetic)$"),
    user_id: Optional[str] = Query(default=None, description="Phase 2: filter by user (default=all)"),
    db: Session = Depends(get_db),
) -> List[TransactionResponse]:
    """
    List transactions with optional filtering and pagination.

    Args:
        limit: Max number of transactions to return.
        offset: Number of transactions to skip.
        source: Filter by source (plaid, upload, synthetic).
        user_id: Optional user filter (Phase 2). Omit to return all transactions.
    """
    if user_id is not None:
        transactions = get_transactions_for_user(
            db, user_id=user_id, limit=limit, offset=offset, source=source
        )
    else:
        query = db.query(Transaction).order_by(Transaction.date.desc())
        if source:
            query = query.filter(Transaction.source == source)
        transactions = query.offset(offset).limit(limit).all()
    return [_transaction_to_response(tx) for tx in transactions]


def _year_month_expr(db_session: Session):
    """Use SQLite-safe strftime for SQLite, extract for PostgreSQL."""
    dialect = db_session.get_bind().dialect.name
    if dialect == "sqlite":
        return (
            cast(func.strftime("%Y", Transaction.date), Integer).label("year"),
            cast(func.strftime("%m", Transaction.date), Integer).label("month"),
        )
    return (
        func.extract("year", Transaction.date).label("year"),
        func.extract("month", Transaction.date).label("month"),
    )


@router.get("/monthly-summary", response_model=MonthlySummaryResponse)
def get_monthly_summary(
    year: Optional[int] = Query(default=None),
    user_id: Optional[str] = Query(default=None, description="Phase 2: filter by user (default=all)"),
    db: Session = Depends(get_db),
) -> MonthlySummaryResponse:
    """
    Get monthly transaction summary (total amount and count per month).

    Args:
        year: Optional year filter. If not provided, returns all months.
        user_id: Optional user filter (Phase 2). Omit to return all transactions.
    """
    year_col, month_col = _year_month_expr(db)
    query = db.query(
        year_col,
        month_col,
        func.sum(Transaction.amount).label("total_amount"),
        func.count(Transaction.transaction_id).label("transaction_count"),
    )
    if user_id is not None and hasattr(Transaction, "user_id"):
        query = _user_filter(query, user_id)
    if year is not None:
        query = query.filter(year_col == year)
    query = query.group_by(year_col, month_col)

    rows = query.order_by(year_col, month_col).all()

    summary = [
        MonthlySummaryItem(
            year=int(r.year),
            month=int(r.month),
            total_amount=float(r.total_amount or 0),
            transaction_count=int(r.transaction_count or 0),
        )
        for r in rows
    ]

    return MonthlySummaryResponse(summary=summary)


@router.post("/sync-plaid", response_model=dict)
def sync_plaid(body: PlaidSyncRequest, db: Session = Depends(get_db)) -> dict:
    """
    Sync transactions from Plaid using an access token.

    Used for direct access-token sync. Prefer POST /plaid/exchange-public-token
    for the Plaid Link flow (exchange public token then sync).
    """
    try:
        return sync_plaid_transactions(body.access_token, db)
    except Exception as e:
        logger.exception("Plaid sync failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


def sync_plaid_transactions(access_token: str, db: Session) -> dict:
    """
    Reusable logic: fetch Plaid transactions, deduplicate, and store.
    Used by POST /transactions/sync-plaid and POST /plaid/exchange-public-token.
    """
    from ingestion.plaid_client import PlaidClient

    client = PlaidClient()
    client.set_access_token(access_token)
    transactions = client.get_transactions()

    existing = db.query(Transaction).all()
    existing_normalized = [
        NormalizedTransaction(
            transaction_id=t.transaction_id,
            date=t.date,
            merchant=t.merchant,
            normalized_merchant=t.normalized_merchant,
            amount=t.amount,
            category=t.category,
            account=t.account,
            source=t.source,
        )
        for t in existing
    ]

    engine = DeduplicationEngine()
    engine.load_existing(existing_normalized)
    unique = engine.filter_duplicates(transactions, add_to_cache=True)

    added = 0
    for tx in unique:
        existing_tx = db.query(Transaction).filter(Transaction.transaction_id == tx.transaction_id).first()
        if not existing_tx:
            db_tx = Transaction(
                transaction_id=tx.transaction_id,
                date=tx.date,
                merchant=tx.merchant,
                normalized_merchant=tx.normalized_merchant,
                amount=tx.amount,
                category=tx.category,
                account=tx.account,
                source=tx.source,
                user_id=DEFAULT_USER_ID,
            )
            db.add(db_tx)
            added += 1

    logger.info("Synced %d Plaid transactions (%d added).", len(transactions), added)

    return {
        "message": "Plaid sync complete",
        "fetched": len(transactions),
        "duplicates_filtered": len(transactions) - len(unique),
        "added": added,
    }


@router.post("/sync-plaid", response_model=dict)
def sync_plaid(body: PlaidSyncRequest, db: Session = Depends(get_db)) -> dict:
    """
    Sync transactions from Plaid using an access token.

    Typically used after POST /plaid/exchange-public-token; this endpoint
    supports direct sync when an access token is already available.
    """
    return sync_plaid_transactions(body.access_token, db)


@router.post("/ingest-synthetic", response_model=dict)
def ingest_synthetic(
    count: int = Query(default=10, ge=1, le=1000),
    days_back: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict:
    """
    Generate and ingest synthetic transactions.

    Uses Faker to create transactions from merchants like Amazon, Starbucks, Netflix.
    Normalizes and deduplicates before storing.
    """
    generator = SyntheticTransactionGenerator()
    transactions = generator.generate_batch(count=count, days_back=days_back)

    existing = db.query(Transaction).all()
    existing_normalized = [
        NormalizedTransaction(
            transaction_id=t.transaction_id,
            date=t.date,
            merchant=t.merchant,
            normalized_merchant=t.normalized_merchant,
            amount=t.amount,
            category=t.category,
            account=t.account,
            source=t.source,
        )
        for t in existing
    ]

    engine = DeduplicationEngine()
    engine.load_existing(existing_normalized)
    unique = engine.filter_duplicates(transactions, add_to_cache=True)

    added = 0
    for tx in unique:
        existing_tx = db.query(Transaction).filter(Transaction.transaction_id == tx.transaction_id).first()
        if not existing_tx:
            db_tx = Transaction(
                transaction_id=tx.transaction_id,
                date=tx.date,
                merchant=tx.merchant,
                normalized_merchant=tx.normalized_merchant,
                amount=tx.amount,
                category=tx.category,
                account=tx.account,
                source=tx.source,
                user_id=DEFAULT_USER_ID,
            )
            db.add(db_tx)
            added += 1

    logger.info("Ingested %d synthetic transactions (%d duplicates filtered).", added, len(transactions) - added)

    return {
        "message": "Synthetic transactions ingested",
        "generated": len(transactions),
        "duplicates_filtered": len(transactions) - len(unique),
        "added": added,
    }


@router.post("/upload-statement", response_model=dict)
def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    """
    Upload a CSV bank statement.

    Parses the CSV, normalizes merchants, deduplicates, and stores transactions.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = file.file.read()
    parser = CSVParser()
    try:
        transactions = parser.parse_bytes(content)
    except Exception as e:
        logger.exception("Failed to parse CSV: %s", e)
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}") from e

    # Load existing for deduplication
    existing = db.query(Transaction).all()
    existing_normalized = [
        NormalizedTransaction(
            transaction_id=t.transaction_id,
            date=t.date,
            merchant=t.merchant,
            normalized_merchant=t.normalized_merchant,
            amount=t.amount,
            category=t.category,
            account=t.account,
            source=t.source,
        )
        for t in existing
    ]

    engine = DeduplicationEngine()
    engine.load_existing(existing_normalized)
    unique = engine.filter_duplicates(transactions, add_to_cache=True)

    added = 0
    for tx in unique:
        existing_tx = db.query(Transaction).filter(Transaction.transaction_id == tx.transaction_id).first()
        if not existing_tx:
            db_tx = Transaction(
                transaction_id=tx.transaction_id,
                date=tx.date,
                merchant=tx.merchant,
                normalized_merchant=tx.normalized_merchant,
                amount=tx.amount,
                category=tx.category,
                account=tx.account,
                source=tx.source,
                user_id=DEFAULT_USER_ID,
            )
            db.add(db_tx)
            added += 1

    logger.info("Uploaded statement: %d new transactions, %d duplicates filtered.", added, len(transactions) - added)

    return {
        "message": "Statement uploaded successfully",
        "parsed": len(transactions),
        "duplicates_filtered": len(transactions) - len(unique),
        "added": added,
    }
