"""Unit tests for Phase 2 history logger and persistence."""

import json
from pathlib import Path
from unittest.mock import patch
import pytest
from cryptolab.utils.history import (
    log_history,
    read_history,
    clear_history,
    get_history_file,
    get_history_dir,
)


class TestHistory:
    """Test suite for local history tracking."""

    @pytest.fixture(autouse=True)
    def clean_test_history(self):
        """Ensure clean history before and after each test."""
        clear_history()
        yield
        clear_history()

    def test_log_and_read_history_format(self):
        log_history(
            operation="Caesar Brute Force",
            input_text="KHOOR",
            output_summary="HELLO",
            params={"shift": 3},
            enabled=True,
        )

        records = read_history(limit=5)
        assert len(records) >= 1
        last = records[-1]
        assert last["operation"] == "Caesar Brute Force"
        assert last["input"] == "KHOOR"
        assert last["output"] == "HELLO"
        assert last["params"] == {"shift": 3}
        assert "timestamp" in last

        # Check actual file format is JSON Lines
        hist_file = get_history_file()
        assert hist_file.exists()
        with open(hist_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            assert len(lines) == len(records)
            for line in lines:
                parsed = json.loads(line)
                assert isinstance(parsed, dict)

    def test_disabled_history_does_not_log(self):
        logged = log_history(
            operation="Base64 Decode",
            input_text="SGVsbG8=",
            output_summary="Hello",
            enabled=False,
        )
        assert logged is False
        records = read_history(limit=5)
        assert len(records) == 0

    def test_write_failure_handled_gracefully(self):
        # Mock file write throwing an OSError (e.g. PermissionError or disk full)
        with patch("builtins.open", side_effect=OSError("Disk full or permission denied")):
            success = log_history(
                operation="Hex Decode",
                input_text="48656c6c6f",
                output_summary="Hello",
                enabled=True,
            )
            # Should not raise exception, but return False safely
            assert success is False

    def test_clear_history(self):
        log_history("Op1", "In1", "Out1")
        assert len(read_history()) >= 1

        cleared = clear_history()
        assert cleared is True
        assert len(read_history()) == 0
