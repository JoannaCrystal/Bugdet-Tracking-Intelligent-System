"""
Database connection and session management for the Finance Agentic System.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base
from utils.config import get_config
from utils.logging import get_logger

logger = get_logger(__name__)

_config = get_config()
_engine = create_engine(
    _config.database.url,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _migrate_phase2_columns() -> None:
    """Add Phase 2 columns to existing transactions table if missing."""
    from sqlalchemy import text

    url = _config.database.url.lower()
    if "postgresql" not in url:
        return  # Only auto-migrate PostgreSQL for now

    columns = [
        ("user_id", "VARCHAR(64) DEFAULT 'default'"),
        ("category_confidence", "FLOAT"),
        ("is_subscription", "BOOLEAN DEFAULT FALSE"),
        ("subscription_confidence", "FLOAT"),
    ]
    with _engine.connect() as conn:
        for col_name, col_def in columns:
            try:
                conn.execute(
                    text(
                        f"ALTER TABLE transactions ADD COLUMN IF NOT EXISTS {col_name} {col_def}"
                    )
                )
                conn.commit()
            except Exception as e:
                if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                    logger.warning("Phase 2 migration column %s: %s", col_name, e)
                conn.rollback()


def init_db() -> None:
    """Create all database tables and run Phase 2 migration if needed."""
    Base.metadata.create_all(bind=_engine)
    logger.info("Database tables created successfully.")
    try:
        _migrate_phase2_columns()
    except Exception as e:
        logger.warning("Phase 2 migration (non-fatal): %s", e)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Yields:
        Database session.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.

    Session is committed on success, rolled back on exception, and closed when done.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
