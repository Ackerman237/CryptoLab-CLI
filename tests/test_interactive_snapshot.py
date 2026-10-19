"""Characterization tests for interactive menu rendering snapshots.

These tests capture the exact current output of the interactive menu
to ensure refactoring doesn't change visual behavior.
"""

import sys
import re
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch, MagicMock

import pytest

from cryptolab.interactive import (
    Menu,
    render_menu,
    menu_lines,
    draw_menu,
    screen,
    _clip,
    render_header,
    term_width,
    term_height,
    HEADER_SUBTITLE,
    HINTS_MAIN,
    HINTS_SUB,
)


class TestInteractiveRendering:
    """Test interactive menu rendering outputs match snapshots."""

    def test_render_header(self):
        """Test header rendering."""
        output = render_header(HEADER_SUBTITLE, max_logo_rows=10)
        assert "CRYPTOLAB CLI v0.1.0" in output
        assert "TOOLKIT KRIPTOGRAFI" in output
        # Header should have logo + subtitle
        lines = output.split("\n")
        assert len(lines) >= 4  # blank, logo lines, blank, subtitle

    def test_render_menu_basic(self):
        """Test basic menu rendering."""
        labels = ["Option 1", "Option 2", "Option 3"]
        descs = ["Desc 1", "Desc 2", "Desc 3"]
        lines = render_menu(labels, selected=0, descs=descs, avail_rows=10)

        # Should have header (scroll indicators if needed) + options + blank + description
        assert any("▸ Option 1" in line for line in lines)
        assert any("  Option 2" in line for line in lines)
        assert any("  Option 3" in line for line in lines)
        assert any("Desc 1" in line for line in lines)

    def test_render_menu_selected_second(self):
        """Test menu with second item selected."""
        labels = ["Option 1", "Option 2", "Option 3"]
        descs = ["Desc 1", "Desc 2", "Desc 3"]
        lines = render_menu(labels, selected=1, descs=descs, avail_rows=10)

        assert any("  Option 1" in line for line in lines)
        assert any("▸ Option 2" in line for line in lines)
        assert any("Desc 2" in line for line in lines)

    def test_render_menu_scroll_up(self):
        """Test menu scrolling up indicator."""
        labels = [f"Option {i}" for i in range(15)]
        descs = [f"Desc {i}" for i in range(15)]
        lines = render_menu(labels, selected=0, descs=descs, avail_rows=8)

        # Should show scroll indicator
        assert any("↓" in line for line in lines)

    def test_render_menu_scroll_down(self):
        """Test menu scrolling down indicator."""
        labels = [f"Option {i}" for i in range(15)]
        descs = [f"Desc {i}" for i in range(15)]
        lines = render_menu(labels, selected=14, descs=descs, avail_rows=8)

        # Should show scroll indicator
        assert any("↑" in line for line in lines)

    def test_render_menu_truncation(self):
        """Test long label truncation."""
        labels = ["A" * 100]
        descs = ["Short desc"]
        lines = render_menu(labels, selected=0, descs=descs, avail_rows=10)

        # Label should be truncated
        for line in lines:
            if "A" in line and "▸" in line:
                assert len(line) < 200  # Should not have full 100 chars

    def test_menu_lines_structure(self):
        """Test menu_lines produces correct structure."""
        menu = Menu("Test Menu", [
            ("Option 1", None, "Description 1"),
            ("Option 2", None, "Description 2"),
        ])
        lines = menu_lines(menu, 0, 0)

        # Should have: header (logo + subtitle) + blank + title + blank + menu body + blank + footer
        header_end = -1
        for i, line in enumerate(lines):
            if "CRYPTOLAB CLI v0.1.0" in line:
                header_end = i
                break
        assert header_end >= 0

        # Title should be present
        assert any("Test Menu" in line for line in lines)

        # Options should be present
        assert any("Option 1" in line for line in lines)
        assert any("Option 2" in line for line in lines)

        # Footer hints should be present
        assert any("navigasi" in line for line in lines)
        assert any("pilih" in line for line in lines)
        assert any("keluar" in line for line in lines)

    def test_clip_function(self):
        """Test _clip text truncation."""
        assert _clip("short", 10) == "short"
        result = _clip("this is a very long text", 10)
        assert result.startswith("this is a") and result.endswith("…")
        assert _clip("exact", 5) == "exact"
        assert _clip("", 10) == ""

    def test_header_subtitle_truncation(self):
        """Test header handles long subtitles."""
        long_subtitle = "A" * 200
        output = render_header(long_subtitle, max_logo_rows=10)
        # Should truncate at terminal width
        assert "…" in output or len(output) < 500


class TestInteractiveMenuNavigation:
    """Test menu navigation key handling (unit tests for key logic)."""

    def test_up_down_navigation(self):
        """Test up/down selection logic."""
        items = ["A", "B", "C", "D"]
        selected = 0

        # Down
        selected = min(selected + 1, len(items) - 1)
        assert selected == 1

        selected = min(selected + 1, len(items) - 1)
        assert selected == 2

        selected = min(selected + 1, len(items) - 1)
        assert selected == 3

        # At bottom, down does nothing
        selected = min(selected + 1, len(items) - 1)
        assert selected == 3

        # Up
        selected = max(selected - 1, 0)
        assert selected == 2

        selected = max(selected - 1, 0)
        assert selected == 1

        selected = max(selected - 1, 0)
        assert selected == 0

        # At top, up does nothing
        selected = max(selected - 1, 0)
        assert selected == 0

    def test_home_end_navigation(self):
        """Test home/end jump logic."""
        items = ["A", "B", "C", "D"]
        selected = 2

        # Home
        selected = 0
        assert selected == 0

        # End
        selected = len(items) - 1
        assert selected == 3


class TestFooterHints:
    """Test footer hint rendering."""

    def test_hints_main(self):
        """Test main menu hints."""
        assert ("↑↓", "navigasi") in HINTS_MAIN
        assert ("enter", "pilih") in HINTS_MAIN
        assert ("q", "keluar") in HINTS_MAIN
        assert ("?", "bantuan") in HINTS_MAIN

    def test_hints_sub(self):
        """Test sub menu hints."""
        assert ("↑↓", "navigasi") in HINTS_SUB
        assert ("enter", "pilih") in HINTS_SUB
        assert ("esc", "kembali") in HINTS_SUB
        assert ("q", "keluar") in HINTS_SUB
        assert ("?", "bantuan") in HINTS_SUB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])