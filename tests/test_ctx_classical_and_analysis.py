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
        while True:
            raw = next(self._answers)
            if raw == "" and default is not None:
                ans = default
                break
            try:
                ans = cast(raw)
                break
            except ValueError:
                self.inputs.append((label, f"<invalid: {raw}>"))
                continue
        self.inputs.append((label, str(ans)))
        return ans

    def work(self, text, fn):
        return fn()


@pytest.fixture(autouse=True)
def no_history(monkeypatch):
    """Disable history logging during tests."""
    from cryptolab.interactive.handlers import (
        ctx_classical,
        ctx_analysis,
        ctx_asymmetric,
        ctx_encoding,
        ctx_hashing,
    )
    monkeypatch.setattr(ctx_classical, "log_history", lambda *a, **k: True)
    monkeypatch.setattr(ctx_analysis, "log_history", lambda *a, **k: True)
    monkeypatch.setattr(ctx_asymmetric, "log_history", lambda *a, **k: True)
    monkeypatch.setattr(ctx_encoding, "log_history", lambda *a, **k: True)
    monkeypatch.setattr(ctx_hashing, "log_history", lambda *a, **k: True)


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


class TestAsymmetricHandler:
    def test_rsa_keygen_sign_verify_base64(self):
        from cryptolab.interactive.handlers.ctx_asymmetric import fn_rsa

        # 1. KeyGen 1024-bit for fast testing
        ctx_kg = FakeCtx(["Generate Keypair", "1024"])
        res_kg = fn_rsa(ctx_kg)
        rows_kg = dict(res_kg.rows)
        pub_pem = rows_kg["Public Key"]
        priv_pem = rows_kg["Private Key"]

        # 2. Sign with base64 encoding
        ctx_sign = FakeCtx(["Tanda Tangan", "Pesan Rahasia", priv_pem, "PSS", "SHA256", "base64"])
        res_sign = fn_rsa(ctx_sign)
        rows_sign = dict(res_sign.rows)
        sig_b64 = rows_sign["Tanda Tangan"]

        # 3. Verify with base64 encoding (tests the base64 verify fix)
        ctx_verify = FakeCtx(["Verifikasi", "Pesan Rahasia", sig_b64, pub_pem, "PSS", "SHA256", "base64"])
        res_verify = fn_rsa(ctx_verify)
        rows_verify = dict(res_verify.rows)
        assert "VALID" in rows_verify["Status"]

    def test_rsa_encrypt_decrypt(self):
        from cryptolab.interactive.handlers.ctx_asymmetric import fn_rsa

        # KeyGen 1024-bit
        ctx_kg = FakeCtx(["Generate Keypair", "1024"])
        res_kg = fn_rsa(ctx_kg)
        pub_pem = dict(res_kg.rows)["Public Key"]
        priv_pem = dict(res_kg.rows)["Private Key"]

        # Encrypt
        ctx_enc = FakeCtx(["Enkripsi", "Secret Data", pub_pem, "OAEP", "SHA256", "hex"])
        res_enc = fn_rsa(ctx_enc)
        ct_hex = dict(res_enc.rows)["Ciphertext"]

        # Decrypt
        ctx_dec = FakeCtx(["Dekripsi", ct_hex, priv_pem, "OAEP", "SHA256", "hex"])
        res_dec = fn_rsa(ctx_dec)
        assert dict(res_dec.rows)["Plaintext"] == "Secret Data"

    def test_dh_exchange(self):
        from cryptolab.interactive.handlers.ctx_asymmetric import fn_dh

        ctx = FakeCtx(["2048", "Ya", 32, "SHA256"])
        res = fn_dh(ctx)
        rows = dict(res.rows)
        assert "Shared Secret" in rows
        assert "Derived Key" in rows


class TestEncodingHandlers:
    def test_base64_roundtrip(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_base64

        ctx_enc = FakeCtx(["Encode (Teks → Base64)", "CryptoLab"])
        res_enc = fn_base64(ctx_enc)
        b64 = dict(res_enc.rows)["Base64"]

        ctx_dec = FakeCtx(["Decode (Base64 → Teks)", b64])
        res_dec = fn_base64(ctx_dec)
        assert dict(res_dec.rows)["Teks"] == "CryptoLab"

    def test_hex_roundtrip(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_hex

        ctx_enc = FakeCtx(["Encode (Teks → Hex)", "CryptoLab"])
        res_enc = fn_hex(ctx_enc)
        hx = dict(res_enc.rows)["Hex"]

        ctx_dec = FakeCtx(["Decode (Hex → Teks)", hx])
        res_dec = fn_hex(ctx_dec)
        assert dict(res_dec.rows)["Teks"] == "CryptoLab"

    def test_binary_roundtrip(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_binary

        ctx_enc = FakeCtx(["Encode (Teks → Binary)", "AB", "Spasi (' ')"])
        res_enc = fn_binary(ctx_enc)
        bin_str = dict(res_enc.rows)["Binary"]
        assert bin_str == "01000001 01000010"
        assert dict(res_enc.rows)["Pemisah"] == "Spasi (' ')"

        ctx_dec = FakeCtx(["Decode (Binary → Teks)", bin_str])
        res_dec = fn_binary(ctx_dec)
        assert dict(res_dec.rows)["Teks"] == "AB"

    def test_binary_delimiters_preset(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_binary

        # Strip delimiter
        ctx_dash = FakeCtx(["Encode (Teks → Binary)", "Hi", "Strip ('-')"])
        res_dash = fn_binary(ctx_dash)
        assert dict(res_dash.rows)["Binary"] == "01001000-01101001"
        assert dict(res_dash.rows)["Pemisah"] == "'-'"

        # Decode dash separated string
        ctx_dec = FakeCtx(["Decode (Binary → Teks)", "01001000-01101001"])
        assert dict(fn_binary(ctx_dec).rows)["Teks"] == "Hi"

        # Dot delimiter
        ctx_dot = FakeCtx(["Encode (Teks → Binary)", "Hi", "Titik ('.')"])
        res_dot = fn_binary(ctx_dot)
        assert dict(res_dot.rows)["Binary"] == "01001000.01101001"
        assert dict(res_dot.rows)["Pemisah"] == "'.'"

        # Comma delimiter
        ctx_comma = FakeCtx(["Encode (Teks → Binary)", "Hi", "Koma (',')"])
        res_comma = fn_binary(ctx_comma)
        assert dict(res_comma.rows)["Binary"] == "01001000,01101001"

        # Tanpa pemisah
        ctx_none = FakeCtx(["Encode (Teks → Binary)", "Hi", "Tanpa pemisah"])
        res_none = fn_binary(ctx_none)
        assert dict(res_none.rows)["Binary"] == "0100100001101001"
        assert dict(res_none.rows)["Pemisah"] == "Tanpa pemisah"

    def test_binary_custom_delimiter_and_validation(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_binary

        # Custom delimiter with retry on invalid inputs (0, 1, alphanumeric)
        ctx_custom = FakeCtx([
            "Encode (Teks → Binary)",
            "OK",
            "Custom (input sendiri)",
            "0",         # Invalid: contains 0 (data bit) -> prompts re-input
            "1",         # Invalid: contains 1 (data bit) -> prompts re-input
            "sep",       # Invalid: letters -> prompts re-input
            "|",         # Valid custom delimiter!
        ])
        res_custom = fn_binary(ctx_custom)
        assert dict(res_custom.rows)["Binary"] == "01001111|01001011"
        assert dict(res_custom.rows)["Pemisah"] == "'|'"

        # Decode custom delimiter ignores '|' and decodes cleanly
        ctx_dec = FakeCtx(["Decode (Binary → Teks)", "01001111|01001011"])
        assert dict(fn_binary(ctx_dec).rows)["Teks"] == "OK"

    def test_binary_decode_ignores_non_binary_delimiters(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_binary

        # Mixed spaces, symbols, dashes
        ctx_dec = FakeCtx(["Decode (Binary → Teks)", "01001000 - 01101001"])
        assert dict(fn_binary(ctx_dec).rows)["Teks"] == "Hi"

        # Comma with space
        ctx_dec2 = FakeCtx(["Decode (Binary → Teks)", "01001000, 01101001"])
        assert dict(fn_binary(ctx_dec2).rows)["Teks"] == "Hi"

        # Hash custom separator
        ctx_dec3 = FakeCtx(["Decode (Binary → Teks)", "01001000##01101001"])
        assert dict(fn_binary(ctx_dec3).rows)["Teks"] == "Hi"

    def test_binary_decode_wrapped_terminal_paste(self):
        from cryptolab.interactive.handlers.ctx_encoding import fn_binary

        # Exact user scenario: assalamualaikum encoded with '=' custom delimiter
        # wrapped mid-byte across terminal lines with indentation/spaces
        wrapped_paste = (
            "01100001=01110011=01110011=01100001=01101100=01100001=01101101=01110101=01100001=01101100=0110000\n"
            "           1=01101001=01101011=01110101=01101101"
        )
        ctx_dec = FakeCtx(["Decode (Binary → Teks)", wrapped_paste])
        res = fn_binary(ctx_dec)
        assert dict(res.rows)["Teks"] == "assalamualaikum"

        # Space-separated binary wrapped mid-byte by terminal line-wrap
        space_wrapped = (
            "01100001 01110011 01110011 01100001 01101100 01100001 01101101 01110101 01100001 01101100 0110000\n"
            "1 01101001 01101011 01110101 01101101"
        )
        ctx_dec2 = FakeCtx(["Decode (Binary → Teks)", space_wrapped])
        res2 = fn_binary(ctx_dec2)
        assert dict(res2.rows)["Teks"] == "assalamualaikum"


class TestHashHandler:
    def test_hash_sha256(self):
        from cryptolab.interactive.handlers.ctx_hashing import fn_hash

        ctx = FakeCtx(["SHA-256", "Halo Dunia"])
        res = fn_hash(ctx)
        assert "Hash" in dict(res.rows)
        assert len(dict(res.rows)["Hash"]) == 64

    def test_hash_hmac_sha256(self):
        from cryptolab.interactive.handlers.ctx_hashing import fn_hash

        ctx = FakeCtx(["HMAC-SHA256", "Data", "secret-key"])
        res = fn_hash(ctx)
        assert "HMAC" in dict(res.rows)
        assert len(dict(res.rows)["HMAC"]) == 64


