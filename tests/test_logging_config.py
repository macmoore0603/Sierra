"""Tests for the centralized logging configuration."""

import logging
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from logging_config import get_logger


class TestGetLogger:
    def test_returns_logger_under_sierra_namespace(self):
        lg = get_logger("mymodule")
        assert lg.name == "sierra.mymodule"

    def test_already_prefixed_name_unchanged(self):
        lg = get_logger("sierra.server")
        assert lg.name == "sierra.server"

    def test_logger_is_a_real_logger(self):
        lg = get_logger("test_check")
        assert isinstance(lg, logging.Logger)

    def test_root_sierra_logger_has_handler(self):
        root = logging.getLogger("sierra")
        assert len(root.handlers) >= 1
