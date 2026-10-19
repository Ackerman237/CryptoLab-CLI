"""Unit tests for Base64, Hexadecimal, and Binary codecs."""

import pytest
from cryptolab import base64_encode, base64_decode
from cryptolab import hex_encode, hex_decode
from cryptolab import binary_encode, binary_decode
from cryptolab import InvalidInputError, DecodingError


class TestBase64Codec:
    """Test suite for Base64 encoder and decoder."""

    def test_ascii_round_trip(self):
        text = "Hello, CTF Player 2026! Base64 test."
        encoded = base64_encode(text)
        assert encoded == "SGVsbG8sIENURiBQbGF5ZXIgMjAyNiEgQmFzZTY0IHRlc3Qu"
        assert base64_decode(encoded) == text

    def test_unicode_round_trip(self):
        # Indonesian text with symbols and accented/multibyte chars
        text = "Kriptografi & Keamanan 🚀: © 2026 — café naïve!"
        encoded = base64_encode(text)
        assert base64_decode(encoded) == text

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            base64_encode("")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            base64_decode("")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            base64_decode("   ")

    def test_invalid_length_raises_decoding_error(self):
        # Length not multiple of 4
        with pytest.raises(DecodingError, match="Panjang string Base64 tidak valid"):
            base64_decode("abc")

    def test_invalid_characters_raises_decoding_error(self):
        with pytest.raises(DecodingError, match="bukan format Base64"):
            base64_decode("####")


class TestHexCodec:
    """Test suite for Hexadecimal encoder and decoder."""

    def test_ascii_round_trip(self):
        text = "CryptoLab"
        encoded = hex_encode(text)
        assert encoded == "43 72 79 70 74 6f 4c 61 62"
        assert hex_decode(encoded) == text

    def test_unicode_round_trip(self):
        text = "Kunci Rahasia 🔒: €100"
        encoded = hex_encode(text, delimiter="")
        assert hex_decode(encoded) == text

    def test_flexible_formatting_support(self):
        # Continuous, spaced, colon-separated, 0x prefix
        expected = "Hello"
        assert hex_decode("48656c6c6f") == expected
        assert hex_decode("48 65 6c 6c 6f") == expected
        assert hex_decode("48:65:6c:6c:6f") == expected
        assert hex_decode("0x48656c6c6f") == expected
        assert hex_decode("0X48 65 6C 6C 6F") == expected

    def test_odd_length_raises_decoding_error(self):
        with pytest.raises(DecodingError, match="Panjang string Hexadecimal ganjil"):
            hex_decode("48656c6c6")

    def test_invalid_hex_character_raises_decoding_error(self):
        with pytest.raises(DecodingError, match="karakter tidak valid"):
            hex_decode("48 65 6c 6c ZZ")

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            hex_encode("")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            hex_decode("")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            hex_decode("  0x  ")


class TestBinaryCodec:
    """Test suite for 8-bit Binary encoder and decoder."""

    def test_ascii_round_trip(self):
        text = "Lab"
        encoded = binary_encode(text)
        # 'L' = 76 = 01001100, 'a' = 97 = 01100001, 'b' = 98 = 01100010
        assert encoded == "01001100 01100001 01100010"
        assert binary_decode(encoded) == text

    def test_unicode_round_trip(self):
        text = "Aman ✨"
        encoded = binary_encode(text)
        assert binary_decode(encoded) == text

    def test_continuous_binary_string_decode(self):
        continuous = "010011000110000101100010"
        assert binary_decode(continuous) == "Lab"

    def test_non_binary_chars_raises_decoding_error(self):
        with pytest.raises(DecodingError, match="bukan biner|karakter tidak valid"):
            binary_decode("01001102 01100001")
        with pytest.raises(DecodingError, match="bukan biner|karakter tidak valid"):
            binary_decode("01001100abc")

    def test_invalid_bit_length_raises_decoding_error(self):
        # 7 bits instead of 8 bits
        with pytest.raises(DecodingError, match="harus 8-bit per byte"):
            binary_decode("0100110 01100001")
        # Continuous binary with length not divisible by 8
        with pytest.raises(DecodingError, match="bukan kelipatan 8 bit"):
            binary_decode("010011001")

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            binary_encode("")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            binary_decode("")
