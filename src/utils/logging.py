"""
Logging configuration for the Finance Agentic System.

Provides structured logging across all modules.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return the root logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_string: Optional custom format string for log messages.

    Returns:
        Configured root logger instance.
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
