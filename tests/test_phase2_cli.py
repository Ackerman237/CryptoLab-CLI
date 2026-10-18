"""Unit tests for Phase 2 CLI commands, options, and flags."""

import pytest
from cryptolab.cli import create_parser, handle_cli_args
from cryptolab.utils.history import clear_history, read_history


class TestCLIPhase2:
    """Test suite for Phase 2 CLI subcommands and options."""

    @pytest.fixture(autouse=True)
    def clean_history(self):
        clear_history()
        yield
        clear_history()

    def test_caesar_brute_force_command(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["caesar", "brute-force", "--text", "KHOOR"])
        code = handle_cli_args(args)
        assert code == 0
        out = capsys.readouterr().out
        assert "HELLO" in out
        assert "[03]" in out
        assert "CAESAR BRUTE FORCE (26 KANDIDAT)" in out

    def test_caesar_brute_force_best_option(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["caesar", "brute-force", "--text", "KHOOR", "--best"])
        code = handle_cli_args(args)
        assert code == 0
        out = capsys.readouterr().out
        assert "KANDIDAT TERBAIK" in out
        assert "HELLO" in out
        assert "Shift        : 03" in out
        assert "estimasi heuristik" in out

    def test_analyze_command(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["analyze", "--text", "48656c6c6f"])
        code = handle_cli_args(args)
        assert code == 0
        out = capsys.readouterr().out
        assert "ANALISIS DETEKSI FORMAT" in out
        assert "Hexadecimal" in out
        assert "Hello" in out

    def test_binary_encode_with_custom_delimiter(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["binary", "encode", "-t", "kriptografi", "-d", "_"])
        code = handle_cli_args(args)
        assert code == 0
        out = capsys.readouterr().out
        expected = "01101011_01110010_01101001_01110000_01110100_01101111_01100111_01110010_01100001_01100110_01101001"
        assert expected in out

    def test_hex_encode_with_custom_delimiter(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["hex", "encode", "-t", "Hi", "-d", ":"])
        code = handle_cli_args(args)
        assert code == 0
        out = capsys.readouterr().out
        assert "48:69" in out

    def test_history_commands(self, capsys):
        parser = create_parser()

        # Run an operation that logs
        args_op = parser.parse_args(["base64", "encode", "-t", "HistTest"])
        handle_cli_args(args_op)
        capsys.readouterr()

        # Check history command
        args_hist = parser.parse_args(["history"])
        code_hist = handle_cli_args(args_hist)
        assert code_hist == 0
        out_hist = capsys.readouterr().out
        assert "RIWAYAT ANALISIS LOKAL" in out_hist
        assert "Base64 Encode" in out_hist

        # Clear history command
        args_clear = parser.parse_args(["history", "--clear"])
        code_clear = handle_cli_args(args_clear)
        assert code_clear == 0
        out_clear = capsys.readouterr().out
        assert "berhasil dibersihkan" in out_clear
        assert len(read_history()) == 0

    def test_no_history_flag(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["--no-history", "base64", "encode", "-t", "PrivateData"])
        handle_cli_args(args)
        capsys.readouterr()

        assert len(read_history()) == 0
