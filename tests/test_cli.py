"""Unit tests for CLI parser, argument dispatching, and rendering."""

from cryptolab import create_parser, handle_cli_args, render_box, render_error


class TestCLI:
    """Test suite for CLI command dispatch and formatted rendering."""

    def test_caesar_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["caesar", "encrypt", "-t", "Halo", "-s", "3"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "Kdor" in captured
        assert "Caesar Cipher (ENCRYPT)" in captured

        args_dec = parser.parse_args(["caesar", "decrypt", "-t", "Kdor", "-s", "3"])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "Halo" in captured_dec

    def test_vigenere_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["vigenere", "encrypt", "-t", "ATTACK", "-k", "LEMON"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "LXFOPV" in captured

    def test_base64_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["base64", "encode", "-t", "Test64"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "VGVzdDY0" in captured

        args_dec = parser.parse_args(["base64", "decode", "-t", "VGVzdDY0"])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "Test64" in captured_dec

    def test_hex_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["hex", "encode", "-t", "Hi"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "48 69" in captured

        args_dec = parser.parse_args(["hex", "decode", "-t", "48 69"])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "Hi" in captured_dec

    def test_binary_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["binary", "encode", "-t", "A"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "01000001" in captured

        args_dec = parser.parse_args(["binary", "decode", "-t", "01000001"])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "A" in captured_dec

    def test_brute_force_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["brute", "-t", "Khoor"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "Hello" in captured
        assert "[03]" in captured

    def test_detect_cli(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["detect", "-t", "01000001"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "Binary" in captured

    def test_auto_cli(self, capsys):
        parser = create_parser()
        # "48656c6c6f" -> "Hello"
        args = parser.parse_args(["auto", "-t", "48656c6c6f"])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "Hello" in captured

    def test_invalid_key_error_handling(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["vigenere", "encrypt", "-t", "Test", "-k", "123!"])
        code = handle_cli_args(args)
        assert code == 1
        err_output = capsys.readouterr().err
        assert "INVALIDKEYERROR" in err_output

    def test_invalid_hex_error_handling(self, capsys):
        parser = create_parser()
        args = parser.parse_args(["hex", "decode", "-t", "4865ZZ"])
        code = handle_cli_args(args)
        assert code == 1
        err_output = capsys.readouterr().err
        assert "DECODINGERROR" in err_output

    def test_render_box_format(self):
        box = render_box("Title", "Op", "In", "Out", {"Param": 1})
        assert "CRYPTOLAB CLI" in box
        assert "Param" in box
        assert "BERHASIL (OK)" in box

    def test_render_error_format(self):
        err_box = render_error("CustomError", "Detail message")
        assert "ERROR: CUSTOMERROR" in err_box
        assert "Detail message" in err_box
