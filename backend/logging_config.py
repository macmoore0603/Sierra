"""
Centralized logging configuration for Sierra backend.

Usage:
    from logging_config import get_logger
    logger = get_logger(__name__)

All Sierra loggers share the ``sierra.*`` hierarchy so a single handler
attached to the ``sierra`` root logger controls output for every module.
"""

import logging
import os
import sys

LOG_LEVEL = os.environ.get("SIERRA_LOG_LEVEL", "INFO").upper()

_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
_DATE_FMT = "%H:%M:%S"


def _configure_root() -> None:
    """One-time setup of the ``sierra`` root logger."""
    root = logging.getLogger("sierra")
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FMT))
    root.addHandler(handler)
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


_configure_root()


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the ``sierra`` namespace.

    If *name* already starts with ``sierra.`` it is used as-is; otherwise
    ``sierra.`` is prepended automatically.
    """
    if not name.startswith("sierra."):
        name = f"sierra.{name}"
    return logging.getLogger(name)
