"""
Phase 2 database migration script.

Adds user_id, category_confidence, is_subscription, subscription_confidence
to the transactions table for existing deployments.

Run from project root: python scripts/migrate_phase2.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate() -> None:
    """Add Phase 2 columns to transactions table."""
    from sqlalchemy import create_engine, text
    from utils.config import get_config

    config = get_config()
    engine = create_engine(config.database.url)
    url = config.database.url.lower()

    columns_to_add = [
        ("user_id", "VARCHAR(64) DEFAULT 'default'"),
        ("category_confidence", "FLOAT"),
        ("is_subscription", "BOOLEAN DEFAULT FALSE"),
        ("subscription_confidence", "FLOAT"),
    ]

    with engine.connect() as conn:
        for col_name, col_def in columns_to_add:
            try:
                if "postgresql" in url:
                    conn.execute(
                        text(
                            f"ALTER TABLE transactions ADD COLUMN IF NOT EXISTS {col_name} {col_def}"
                        )
                    )
                else:
                    conn.execute(
                        text(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_def}")
                    )
                conn.commit()
                logger.info("Added column: %s", col_name)
            except Exception as e:  # noqa: BLE001
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("Column %s already exists, skipping.", col_name)
                else:
                    raise
                conn.rollback()

    logger.info("Phase 2 migration complete.")


if __name__ == "__main__":
    migrate()
