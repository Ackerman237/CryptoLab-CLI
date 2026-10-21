"""Tests for interactive ctx handlers: Caesar, Vigenere, and Auto Analyze.

Verifies:
1. Caesar brute force works properly without AttributeError and formats best + all 26 shifts.
2. Vigenere encrypt/decrypt works with key validation.
3. Auto Analyze correctly displays candidates (method, category, status, score, output_text)
   and handles keyed cipher flows (Vigenere, AES/DES).
"""

import pytest

from cryptolab.flow import Result
from cryptolab.interactive.handlers.ctx_classical import fn_caesar, fn_vigenere
from cryptolab.interactive.handlers.ctx_analysis import fn_auto


class FakeCtx:
    """Mock Ctx that returns answers sequentially from a predefined list."""

    def __init__(self, answers):
        self._answers = iter(answers)
        self.inputs = []

    def choose(self, label, options, default=1):
        ans = next(self._answers)
        self.inputs.append((label, ans))
        return ans

    def ask(self, label, default=None, cast=str, secret=False):
        raw = next(self._answers)
        if raw == "" and default is not None:
            ans = default
        else:
            ans = cast(raw)
        self.inputs.append((label, str(ans)))
        return ans

    def work(self, text, fn):
        return fn()


@pytest.fixture(autouse=True)
def no_history(monkeypatch):
    """Disable history logging during tests."""
    from cryptolab.interactive.handlers import ctx_classical, ctx_analysis
    monkeypatch.setattr(ctx_classical, "log_history", lambda *a, **k: True)
    monkeypatch.setattr(ctx_analysis, "log_history", lambda *a, **k: True)


class TestCaesarHandler:
    def test_caesar_encrypt(self):
        ctx = FakeCtx(["Enkripsi", "Hello World", 3])
        res: Result = fn_caesar(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)
        assert rows_dict["Plaintext"] == "Hello World"
        assert rows_dict["Shift"] == "3"
        assert rows_dict["Ciphertext"] == "Khoor Zruog"

    def test_caesar_decrypt(self):
        ctx = FakeCtx(["Dekripsi", "Khoor Zruog", 3])
        res: Result = fn_caesar(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)
        assert rows_dict["Ciphertext"] == "Khoor Zruog"
        assert rows_dict["Shift"] == "3"
        assert rows_dict["Plaintext"] == "Hello World"

    def test_caesar_bruteforce_success(self):
        # Ciphertext "Khoor Zruog" -> best candidate is shift 3 "Hello World"
        ctx = FakeCtx(["Brute-force", "Khoor Zruog"])
        res: Result = fn_caesar(ctx)
        assert isinstance(res, Result)

        rows_dict = dict(res.rows)
        assert rows_dict["Teks asli"] == "Khoor Zruog"
        assert rows_dict["Shift terbaik"] == "Shift 03"
        assert rows_dict["Hasil terbaik"] == "Hello World"
        assert "Tinggi" in rows_dict["Skor"]

        # Check that all 26 shifts are listed
        shift_rows = [k for k in rows_dict.keys() if k.startswith("Shift ")]
        # 1 row for "Shift terbaik", 26 rows for shifts 00-25
        assert len(shift_rows) == 27
        # Shift 03 should have the star marker
        assert "Shift 03 ★" in rows_dict
        assert "Hello World" in rows_dict["Shift 03 ★"]


    def test_caesar_bruteforce_flag_detected(self):
        # Caesar encrypted flag e.g. "KHOOR{IODJ_WHVW}" (shift 3 of "HELLO{FLAG_TEST}")
        ctx = FakeCtx(["Brute-force", "KHOOR{IODJ_WHVW}"])
        res: Result = fn_caesar(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)

        assert rows_dict["Shift terbaik"] == "Shift 03"
        assert rows_dict["Hasil terbaik"] == "HELLO{FLAG_TEST}"
        assert "Flag" in rows_dict
        assert "Shift 03 ★" in rows_dict
        assert "[FLAG]" in rows_dict["Shift 03 ★"]


class TestVigenereHandler:
    def test_vigenere_encrypt(self):
        ctx = FakeCtx(["Enkripsi", "Hello World", "KEY"])
        res: Result = fn_vigenere(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)
        assert rows_dict["Plaintext"] == "Hello World"
        assert rows_dict["Kunci"] == "KEY"
        assert rows_dict["Ciphertext"] == "Rijvs Uyvjn"

    def test_vigenere_decrypt(self):
        ctx = FakeCtx(["Dekripsi", "Rijvs Uyvjn", "KEY"])
        res: Result = fn_vigenere(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)
        assert rows_dict["Ciphertext"] == "Rijvs Uyvjn"
        assert rows_dict["Kunci"] == "KEY"
        assert rows_dict["Plaintext"] == "Hello World"

    def test_vigenere_key_validation(self):
        from cryptolab.interactive.handlers.ctx_classical import _validate_vigenere_key
        assert _validate_vigenere_key("secret") == "secret"
        assert _validate_vigenere_key("  ABC  ") == "ABC"
        with pytest.raises(ValueError, match="kunci tidak boleh kosong"):
            _validate_vigenere_key("   ")
        with pytest.raises(ValueError, match="hanya boleh berisi huruf"):
            _validate_vigenere_key("kunci123")
        with pytest.raises(ValueError, match="hanya boleh berisi huruf"):
            _validate_vigenere_key("kunci rahasia")


class TestAutoAnalyzeHandler:
    def test_auto_analyze_base64(self):
        # Base64 of "Hello World! Antigravity"
        b64 = "SGVsbG8gV29ybGQhIEFudGlncmF2aXR5"
        ctx = FakeCtx([b64, ""])
        res: Result = fn_auto(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)

        assert rows_dict["Metode"] == "Base64"
        assert rows_dict["Kategori"] == "Encoding"
        assert rows_dict["Hasil"] == "Hello World! Antigravity"
        assert rows_dict["Metode"] != "-"
        assert rows_dict["Hasil"] != "-"

    def test_auto_analyze_caesar(self):
        # "KHOOR ZRUOG" -> Caesar shift 3 "HELLO WORLD"
        ctx = FakeCtx(["KHOOR ZRUOG", ""])
        res: Result = fn_auto(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)

        assert "Caesar Cipher (Shift 03)" in rows_dict["Metode"]
        assert rows_dict["Kategori"] == "Kriptografi Klasik"
        assert rows_dict["Hasil"] == "HELLO WORLD"
        assert rows_dict["Metode"] != "-"
        assert rows_dict["Hasil"] != "-"

    def test_auto_analyze_vigenere_with_key(self):
        # "LXFOPV" encrypted with "LEMON" -> "ATTACK"
        ctx = FakeCtx(["LXFOPV", "LEMON", ""])
        res: Result = fn_auto(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)

        assert "Vigenere Cipher (Key: LEMON)" in rows_dict["Metode"]
        assert rows_dict["Hasil"] == "ATTACK"
        assert rows_dict["Metode"] != "-"

    def test_auto_analyze_des_with_key_and_iv(self):
        # DES hex ciphertext from test_analysis.py
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21"
        ctx = FakeCtx([ct_hex, "abcdefgh", "hgfedcba"])
        res: Result = fn_auto(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)

        assert "DES" in rows_dict["Metode"]
        assert rows_dict["Hasil"] == "des_enkripsi"

    def test_auto_analyze_no_candidates(self):
        # Random non-decodeable string skipped key
        ctx = FakeCtx(["???@@@###$$$", ""])
        res: Result = fn_auto(ctx)
        assert isinstance(res, Result)
        rows_dict = dict(res.rows)
        assert "Hasil" in rows_dict
        assert len(rows_dict["Hasil"]) > 0

