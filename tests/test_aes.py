"""Unit tests for AES (Advanced Encryption Standard) CBC and ECB modes, padding, and validation."""

import pytest
from cryptolab.exceptions import (
    CryptoLabError,
    DecodingError,
    InvalidInputError,
    InvalidKeyError,
)
from cryptolab.symmetric.aes import (
    aes_encrypt,
    aes_decrypt,
    aes_auto_analyze,
    AesResult,
)


class TestAES:
    """Test suite for AES-128 encryption, decryption, auto analyze, and validation."""

    def test_aes_cbc_round_trip_pkcs7(self):
        plaintext = "Praktikum Kripto Modern AES-128!"
        key = "1234567890abcdef"  # exactly 16 bytes (128-bit)
        iv = "fedcba0987654321"   # exactly 16 bytes (128-bit)

        enc_res = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7")
        assert enc_res.technical_success
        assert len(enc_res.output_text) % 32 == 0  # 16-byte block = 32 hex chars

        dec_res = aes_decrypt(enc_res.output_text, key=key, mode="CBC", iv=iv, padding="PKCS7")
        assert dec_res.technical_success
        assert dec_res.output_text == plaintext
        assert dec_res.is_utf8
        assert dec_res.readable_success

    def test_aes_ecb_round_trip_pkcs7(self):
        plaintext = "Kerahasiaan AES ECB Mode"
        key = "abcdef0123456789"  # 16 bytes

        enc_res = aes_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7")
        assert enc_res.technical_success
        assert len(enc_res.output_text) % 32 == 0

        dec_res = aes_decrypt(enc_res.output_text, key=key, mode="ECB", padding="PKCS7")
        assert dec_res.technical_success
        assert dec_res.output_text == plaintext

    def test_aes_without_padding_exact_block(self):
        plaintext = "1234567890123456"  # exactly 16 bytes
        key = "mysecretkey12345"
        iv = "myivvector123456"

        enc_res = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="None")
        dec_res = aes_decrypt(enc_res.output_text, key=key, mode="CBC", iv=iv, padding="None")
        assert dec_res.output_text == plaintext

    def test_aes_without_padding_invalid_length_raises_error(self):
        plaintext = "short text"  # not multiple of 16
        key = "mysecretkey12345"
        with pytest.raises(InvalidInputError) as exc_info:
            aes_encrypt(plaintext, key=key, mode="CBC", iv="myivvector123456", padding="None")
        assert "kelipatan blok 16 byte" in str(exc_info.value)

    def test_aes_invalid_key_length(self):
        # 8 bytes (DES length) should be rejected for AES
        with pytest.raises(InvalidKeyError) as exc_info:
            aes_encrypt("test", key="12345678", mode="CBC", iv="myivvector123456")
        assert "Panjang key AES" in str(exc_info.value)

        with pytest.raises(InvalidKeyError):
            aes_decrypt("a" * 32, key="too_short_123", mode="ECB")

    def test_aes_cbc_missing_iv(self):
        with pytest.raises(InvalidInputError) as exc_info:
            aes_decrypt("a" * 32, key="1234567890123456", mode="CBC", iv=None)
        assert "memerlukan IV" in str(exc_info.value)

    def test_aes_cbc_invalid_iv_length(self):
        # 8 bytes IV should be rejected (AES needs 16 bytes)
        with pytest.raises(InvalidInputError) as exc_info:
            aes_decrypt("a" * 32, key="1234567890123456", mode="CBC", iv="8byteiv_")
        assert "Panjang IV AES CBC harus tepat 16 byte" in str(exc_info.value)

    def test_aes_invalid_hex_input(self):
        # Odd length hex
        with pytest.raises(DecodingError):
            aes_decrypt("abc", key="1234567890123456", mode="ECB")

        # Non-hex characters
        with pytest.raises(DecodingError):
            aes_decrypt("g" * 32, key="1234567890123456", mode="ECB")

        # Not multiple of 16 bytes (e.g. 16 hex chars = 8 bytes)
        with pytest.raises(InvalidInputError) as exc_info:
            aes_decrypt("0123456789abcdef", key="1234567890123456", mode="ECB")
        assert "kelipatan blok 16 byte" in str(exc_info.value)

    def test_aes_non_utf8_fallback_to_hex(self):
        # Ciphertext 32 hex chars (1 block)
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21a1b2c3d4e5f60718293a4b5c6d7e8f90"
        key = "1234567890123456"
        res = aes_decrypt(ct_hex, key=key, mode="ECB", padding="None")
        assert res.technical_success
        assert not res.is_utf8
        assert not res.readable_success
        assert len(res.output_text) == len(ct_hex)

    def test_aes_auto_analyze_with_key_and_iv(self):
        plaintext = "Flag Lab Keamanan AES 128"
        key = "kuncirahasia1234"
        iv = "vektorinisialisasi"[:16]

        enc = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7")
        candidates = aes_auto_analyze(enc.output_text, key=key, iv=iv)

        assert len(candidates) >= 1
        best = candidates[0]
        assert best.mode == "CBC"
        assert best.padding == "PKCS7"
        assert best.output_text == plaintext
        assert best.readable_success

    def test_aes_auto_analyze_without_iv(self):
        # When IV is omitted, ECB candidates should be tested
        plaintext = "Testing AES ECB Auto Mode"
        key = "kuncirahasia1234"
        enc = aes_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7")

        candidates = aes_auto_analyze(enc.output_text, key=key, iv=None)
        assert len(candidates) >= 1
        modes = [c.mode for c in candidates]
        assert "ECB" in modes
        assert "CBC" not in modes
        assert candidates[0].output_text == plaintext

    def test_aes_cli_encrypt_and_decrypt(self, capsys):
        from cryptolab.cli import create_parser, handle_cli_args
        parser = create_parser()

        # Encrypt
        args_enc = parser.parse_args([
            "aes", "encrypt", "-t", "PlaintextAES128",
            "-k", "mysecretkey12345", "-m", "CBC", "--iv", "myivvector123456"
        ])
        code_enc = handle_cli_args(args_enc)
        assert code_enc == 0
        captured_enc = capsys.readouterr().out
        assert "AES (CBC) (ENCRYPT)" in captured_enc

        # Decrypt
        # Round-trip decrypt
        enc_res = aes_encrypt("PlaintextAES128", key="mysecretkey12345", mode="CBC", iv="myivvector123456")
        args_dec = parser.parse_args([
            "aes", "decrypt", "-t", enc_res.output_text,
            "-k", "mysecretkey12345", "-m", "CBC", "--iv", "myivvector123456"
        ])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "PlaintextAES128" in captured_dec

    def test_aes_cli_auto(self, capsys):
        from cryptolab.cli import create_parser, handle_cli_args
        parser = create_parser()

        enc_res = aes_encrypt("SolusiAutoAES", key="mysecretkey12345", mode="CBC", iv="myivvector123456")
        args_auto = parser.parse_args([
            "aes", "auto", "-t", enc_res.output_text,
            "-k", "mysecretkey12345", "--iv", "myivvector123456"
        ])
        code_auto = handle_cli_args(args_auto)
        assert code_auto == 0
        captured_auto = capsys.readouterr().out
        assert "SolusiAutoAES" in captured_auto
        assert "AES Auto (CBC, Padding PKCS7)" in captured_auto

