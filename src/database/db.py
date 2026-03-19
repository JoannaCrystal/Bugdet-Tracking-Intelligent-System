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
_db_url = _config.database.url

# SQLite: check_same_thread=False for FastAPI/async; no pool_pre_ping
# PostgreSQL: pool_pre_ping for connection health checks
_engine_kwargs = {"echo": False}
if "sqlite" in _db_url.lower():
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs["pool_pre_ping"] = False
else:
    _engine_kwargs["pool_pre_ping"] = True

_engine = create_engine(_db_url, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _migrate_phase2_columns() -> None:
    """Add Phase 2 columns to existing transactions table if missing."""
    from sqlalchemy import text

    url = _config.database.url.lower()
    is_sqlite = "sqlite" in url

    # Column definitions: (name, postgres_def, sqlite_def)
    columns = [
        ("user_id", "VARCHAR(64) DEFAULT 'default'", "TEXT DEFAULT 'default'"),
        ("category_confidence", "FLOAT", "REAL"),
        ("is_subscription", "BOOLEAN DEFAULT FALSE", "INTEGER DEFAULT 0"),
        ("subscription_confidence", "FLOAT", "REAL"),
    ]
    with _engine.connect() as conn:
        for col_name, pg_def, sqlite_def in columns:
            col_def = sqlite_def if is_sqlite else pg_def
            try:
                if is_sqlite:
                    conn.execute(text(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_def}"))
                else:
                    conn.execute(
                        text(
                            f"ALTER TABLE transactions ADD COLUMN IF NOT EXISTS {col_name} {col_def}"
                        )
                    )
                conn.commit()
            except Exception as e:
                err_lower = str(e).lower()
                if "duplicate column" in err_lower or "already exists" in err_lower:
                    pass  # Column already exists
                else:
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
