"""Unit tests for interactive terminal menu, input validation, and navigation."""

import pytest
from pathlib import Path
from cryptolab.interactive import (
    run_interactive_menu,
    handle_auto_analyze,
    handle_caesar,
    handle_vigenere,
    handle_des,
    handle_base64,
    handle_hex,
    handle_binary,
    handle_history,
    save_result_prompt,
)
from cryptolab.utils.history import clear_history, read_history


class TestInteractive:
    """Test suite for interactive CLI menus."""

    @pytest.fixture(autouse=True)
    def clean_hist(self):
        clear_history()
        yield
        clear_history()

    def test_menu_exit_with_9(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "9")
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Sampai jumpa" in captured

    def test_menu_exit_with_0(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "0")
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Sampai jumpa" in captured

    def test_menu_invalid_input_retries(self, monkeypatch, capsys):
        inputs = iter(["abc", "99", "9"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Pilihan tidak valid" in captured
        assert "Sampai jumpa" in captured

    def test_caesar_interactive_encrypt_and_decrypt(self, monkeypatch, capsys):
        # 1. Caesar -> Enkripsi -> "Halo" -> shift 3 -> return to menu (0)
        # 2. Caesar -> Dekripsi -> "Kdor" -> shift 3 -> return to menu (0)
        # 3. Return to main menu (0)
        inputs = iter([
            "1", "Halo", "3", "0",
            "2", "Kdor", "3", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_caesar()
        captured = capsys.readouterr().out
        assert "Kdor" in captured
        assert "Halo" in captured

    def test_caesar_interactive_brute_force(self, monkeypatch, capsys):
        # Brute force option 3 -> "KHOOR" -> best only "y" -> return (0) -> exit (0)
        inputs = iter([
            "3", "KHOOR", "y", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_caesar()
        captured = capsys.readouterr().out
        assert "HELLO" in captured
        assert "Shift        : 03" in captured

    def test_vigenere_interactive(self, monkeypatch, capsys):
        # Enkripsi -> "ATTACK" -> "LEMON" -> return (0) -> exit (0)
        inputs = iter([
            "1", "ATTACK", "LEMON", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_vigenere()
        captured = capsys.readouterr().out
        assert "LXFOPV" in captured

    def test_vigenere_invalid_key_recovery(self, monkeypatch, capsys):
        # Try invalid key "123", then valid key "KEY", then exit
        inputs = iter([
            "1", "Hello", "123!", "1", "Hello", "KEY", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_vigenere()
        captured = capsys.readouterr().out
        assert "huruf alfabet" in captured
        assert "Rijvs" in captured


    def test_base64_interactive(self, monkeypatch, capsys):
        # Encode -> "Testing" -> return (0) -> Decode -> "VGVzdGluZw==" -> return (0) -> exit (0)
        inputs = iter([
            "1", "Testing", "0",
            "2", "VGVzdGluZw==", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_base64()
        captured = capsys.readouterr().out
        assert "VGVzdGluZw==" in captured
        assert "Testing" in captured

    def test_hex_interactive(self, monkeypatch, capsys):
        # Encode -> "Lab" -> default delimiter -> return (0) -> Decode -> "4c 61 62" -> return (0) -> exit (0)
        inputs = iter([
            "1", "Lab", "", "0",
            "2", "4c 61 62", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_hex()
        captured = capsys.readouterr().out
        assert "4c 61 62" in captured
        assert "Lab" in captured

    def test_binary_interactive(self, monkeypatch, capsys):
        # Encode -> "A" -> default delimiter -> return (0) -> Decode -> "01000001" -> return (0) -> exit (0)
        inputs = iter([
            "1", "A", "", "0",
            "2", "01000001", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_binary()
        captured = capsys.readouterr().out
        assert "01000001" in captured
        assert "A" in captured

    def test_des_interactive_cbc_decrypt(self, monkeypatch, capsys):
        # 1 (Dekripsi) -> ct -> 2 (CBC) -> key "abcdefgh" -> iv "hgfedcba" -> 1 (PKCS7) -> 0 (return) -> 0 (exit)
        inputs = iter([
            "1", "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "2", "abcdefgh", "hgfedcba", "1", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_des()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured
        assert "CBC" in captured

    def test_des_interactive_ecb_decrypt(self, monkeypatch, capsys):
        # 1 (Dekripsi) -> ct -> 3 (ECB) -> key "abcdefgh" -> 1 (PKCS7) -> 0 (return) -> 0 (exit)
        # Note: ECB does NOT prompt for IV
        inputs = iter([
            "1", "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "3", "abcdefgh", "2", "0",  # None padding to avoid padding error on mismatched mode
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_des()
        captured = capsys.readouterr().out
        assert "ECB" in captured

    def test_des_interactive_auto_mode(self, monkeypatch, capsys):
        # 1 (Dekripsi) -> ct -> 1 (Auto) -> key "abcdefgh" -> iv "hgfedcba" -> 0 (return) -> 0 (exit)
        inputs = iter([
            "1", "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "1", "abcdefgh", "hgfedcba", "0",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_des()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured
        assert "HASIL ANALISIS DES" in captured

    def test_auto_analyze_keyless_flow(self, monkeypatch, capsys):
        # Auto Analyze with Base64 flag string -> Enter to skip key -> 0 to return
        flag_b64 = "RkxBR3tjcnlwdG9fbGFiXzIwMjR9"  # FLAG{crypto_lab_2024} in base64
        inputs = iter([
            flag_b64, "", "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_auto_analyze()
        captured = capsys.readouterr().out
        assert "FLAG{crypto_lab_2024}" in captured

    def test_auto_analyze_des_challenge_flow(self, monkeypatch, capsys):
        # Auto Analyze with DES challenge -> asks key -> "abcdefgh" -> asks IV -> "hgfedcba" -> 0 to return
        inputs = iter([
            "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "abcdefgh",
            "hgfedcba",
            "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_auto_analyze()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured

    def test_history_interactive_view_and_clear(self, monkeypatch, capsys):
        # View history -> Option 1 (clear) -> confirm "y" -> option 0 (return)
        inputs = iter([
            "1", "y", "0",
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_history()
        captured = capsys.readouterr().out
        assert "berhasil dibersihkan" in captured

    def test_save_result_prompt(self, monkeypatch, tmp_path):
        target_file = tmp_path / "test_output.txt"
        inputs = iter(["y", str(target_file)])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        save_result_prompt("Teks Konten Uji Coba")
        assert target_file.exists()
        assert target_file.read_text(encoding="utf-8") == "Teks Konten Uji Coba"

    def test_back_navigation_with_b(self, monkeypatch, capsys):
        # User types "b" at first prompt, safely returns to menu
        inputs = iter(["b"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        handle_caesar()
        # Should exit cleanly without errors
        captured = capsys.readouterr().out
        assert "CAESAR CIPHER" in captured
