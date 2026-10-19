"""Unit tests for DES (Data Encryption Standard) CBC and ECB modes, padding, and CLI."""

import pytest
from cryptolab import (
    CryptoLabError,
    DecodingError,
    InvalidInputError,
    InvalidKeyError,
)
from cryptolab import (
    des_encrypt,
    des_decrypt,
    des_auto_analyze,
    DesResult,
)
from cryptolab import create_parser, handle_cli_args
from cryptolab import clear_history


class TestDES:
    """Test suite for DES encryption, decryption, auto analyze, and CLI."""

    @pytest.fixture(autouse=True)
    def clean_hist(self):
        clear_history()
        yield
        clear_history()

    def test_des_cbc_round_trip_pkcs7(self):
        plaintext = "Praktikum Kripto!"
        key = "kunci123"  # 8 bytes
        iv = "initvect"   # 8 bytes

        enc_res = des_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7")
        assert enc_res.technical_success
        assert len(enc_res.output_text) % 16 == 0

        dec_res = des_decrypt(enc_res.output_text, key=key, mode="CBC", iv=iv, padding="PKCS7")
        assert dec_res.technical_success
        assert dec_res.output_text == plaintext
        assert dec_res.is_utf8
        assert dec_res.readable_success

    def test_des_ecb_round_trip_pkcs7(self):
        plaintext = "Data Rahasia Lab"
        key = "password"  # 8 bytes

        enc_res = des_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7")
        assert enc_res.technical_success
        assert len(enc_res.output_text) % 16 == 0

        dec_res = des_decrypt(enc_res.output_text, key=key, mode="ECB", padding="PKCS7")
        assert dec_res.technical_success
        assert dec_res.output_text == plaintext

    def test_des_without_padding_exact_block(self):
        plaintext = "12345678"  # exactly 8 bytes
        key = "mysecret"
        iv = "initvect"

        enc_res = des_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="None")
        dec_res = des_decrypt(enc_res.output_text, key=key, mode="CBC", iv=iv, padding="None")
        assert dec_res.output_text == plaintext

    def test_des_without_padding_invalid_length_raises_error(self):
        plaintext = "12345"  # not multiple of 8
        key = "mysecret"
        with pytest.raises(InvalidInputError) as exc_info:
            des_encrypt(plaintext, key=key, mode="CBC", iv="initvect", padding="None")
        assert "kelipatan 8 byte" in str(exc_info.value)

    def test_des_invalid_key_length(self):
        with pytest.raises(InvalidKeyError) as exc_info:
            des_encrypt("test", key="short", mode="CBC", iv="initvect")
        assert "8 byte" in str(exc_info.value)

        with pytest.raises(InvalidKeyError):
            des_decrypt("5828b071ff8b9fe9f28e2f22bd9c3f21", key="too_long_key", mode="CBC", iv="initvect")

    def test_des_cbc_missing_iv(self):
        with pytest.raises(InvalidInputError) as exc_info:
            des_decrypt("5828b071ff8b9fe9f28e2f22bd9c3f21", key="12345678", mode="CBC", iv=None)
        assert "memerlukan IV" in str(exc_info.value)

    def test_des_cbc_invalid_iv_length(self):
        with pytest.raises(InvalidInputError) as exc_info:
            des_decrypt("5828b071ff8b9fe9f28e2f22bd9c3f21", key="12345678", mode="CBC", iv="short")
        assert "Panjang IV" in str(exc_info.value)

    def test_des_invalid_hex_input(self):
        # Odd length hex
        with pytest.raises(DecodingError):
            des_decrypt("5828b071ff8b9fe9f28e2f22bd9c3f2", key="12345678", mode="ECB")

        # Non-hex characters
        with pytest.raises(DecodingError):
            des_decrypt("5828b071ff8b9fe9f28e2f22bd9c3fZZ", key="12345678", mode="ECB")

    def test_des_non_utf8_fallback_to_hex(self):
        # Decrypting random ciphertext with wrong key usually produces non-UTF8 bytes
        # or corrupted padding if padding="None"
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21"
        res = des_decrypt(ct_hex, key="11111111", mode="ECB", padding="None")
        assert res.technical_success
        assert not res.is_utf8
        assert not res.readable_success
        assert len(res.output_text) == 32  # 16 bytes displayed as 32 hex chars

    def test_des_auto_analyze_known_challenge(self):
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21"
        key = "abcdefgh"
        iv = "hgfedcba"

        candidates = des_auto_analyze(ct_hex, key=key, iv=iv)
        assert len(candidates) >= 1
        best = candidates[0]
        assert best.mode == "CBC"
        assert best.padding == "PKCS7"
        assert best.output_text == "des_enkripsi"
        assert best.readable_success

    def test_des_auto_analyze_without_iv(self):
        # When IV is omitted, ECB candidates should still be tested
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21"
        key = "abcdefgh"
        candidates = des_auto_analyze(ct_hex, key=key, iv=None)
        # Should contain ECB candidates
        modes = [c.mode for c in candidates]
        assert "ECB" in modes
        assert "CBC" not in modes

    def test_des_cli_encrypt_and_decrypt(self, capsys):
        parser = create_parser()
        # Encrypt
        args_enc = parser.parse_args([
            "des", "encrypt", "-t", "HaloDES!", "-k", "kuncides", "-m", "CBC", "--iv", "ivvect12"
        ])
        code_enc = handle_cli_args(args_enc)
        assert code_enc == 0
        captured_enc = capsys.readouterr().out
        assert "DES (CBC) (ENCRYPT)" in captured_enc

        # Decrypt known challenge
        args_dec = parser.parse_args([
            "des", "decrypt", "-t", "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "-k", "abcdefgh", "-m", "CBC", "--iv", "hgfedcba"
        ])
        code_dec = handle_cli_args(args_dec)
        assert code_dec == 0
        captured_dec = capsys.readouterr().out
        assert "des_enkripsi" in captured_dec

    def test_des_cli_auto(self, capsys):
        parser = create_parser()
        args = parser.parse_args([
            "des", "auto", "-t", "5828b071ff8b9fe9f28e2f22bd9c3f21",
            "-k", "abcdefgh", "--iv", "hgfedcba"
        ])
        code = handle_cli_args(args)
        assert code == 0
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured
        assert "DES Auto (CBC, Padding PKCS7)" in captured
