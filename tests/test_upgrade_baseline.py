"""Tahap 0 - Patokan regresi upgrade (upgrade-spec.md).

Semua nilai diambil dari output tool SEBELUM upgrade dijalankan.
Tes ini harus tetap hijau setelah setiap tahap upgrade.
"""

import pytest

from cryptolab import (
    base64_decode,
    base64_encode,
    binary_decode,
    binary_encode,
    caesar_decrypt,
    caesar_encrypt,
    hash_compute,
    hex_decode,
    hex_encode,
    vigenere_decrypt,
    vigenere_encrypt,
)
from cryptolab.core.exceptions import DecodingError, InvalidInputError


# ============================================================
# Encoding - Binary
# ============================================================
def test_binary_encode_default_spasi():
    """Default lama: pemisah spasi."""
    assert binary_encode("Hi") == "01001000 01101001"
    assert binary_encode("Halo Dunia") == (
        "01001000 01100001 01101100 01101111 00100000 "
        "01000100 01110101 01101110 01101001 01100001"
    )


def test_binary_encode_delimiter_param():
    assert binary_encode("Hi", delimiter="") == "0100100001101001"
    assert binary_encode("Hi", delimiter=",") == "01001000,01101001"


def test_binary_decode_lama():
    assert binary_decode("01001000 01101001") == "Hi"
    assert binary_decode("0100100001101001") == "Hi"


def test_binary_decode_error_messages_tetap():
    """Pesan error decode lama (input salah) tidak berubah."""
    with pytest.raises(DecodingError) as exc:
        binary_decode("01001000 011010")
    assert "Token ke-2" in str(exc.value)

    with pytest.raises(DecodingError) as exc:
        binary_decode("0100100001101")
    assert "bukan kelipatan 8" in str(exc.value)

    with pytest.raises(InvalidInputError):
        binary_decode("")


# ============================================================
# Encoding - Hex
# ============================================================
def test_hex_encode_default_spasi():
    assert hex_encode("Hi") == "48 69"
    assert hex_encode("Halo Dunia") == "48 61 6c 6f 20 44 75 6e 69 61"


def test_hex_encode_delimiter_param():
    assert hex_encode("Hi", delimiter="") == "4869"
    assert hex_encode("Hi", delimiter=":") == "48:69"


def test_hex_decode_lama():
    """Mendukung spasi, titik dua, strip, prefix 0x di awal (perilaku lama)."""
    assert hex_decode("4869") == "Hi"
    assert hex_decode("48 69") == "Hi"
    assert hex_decode("48:69") == "Hi"
    assert hex_decode("48-69") == "Hi"
    assert hex_decode("0x4869") == "Hi"
    # '0x' hanya didukung di awal string (perilaku lama, jangan berubah)
    with pytest.raises(DecodingError):
        hex_decode("0x48 0x69")


def test_hex_decode_error_messages_tetap():
    with pytest.raises(DecodingError) as exc:
        hex_decode("486")
    assert "ganjil" in str(exc.value)

    with pytest.raises(InvalidInputError):
        hex_decode("")


# ============================================================
# Klasik - Caesar & Vigenere
# ============================================================
def test_caesar_tetap():
    assert caesar_encrypt("HELLO", 3) == "KHOOR"
    assert caesar_decrypt("KHOOR", 3) == "HELLO"
    assert caesar_encrypt("Halo Dunia", 5) == "Mfqt Izsnf"


def test_vigenere_tetap():
    assert vigenere_encrypt("Hello World", "key") == "Rijvs Uyvjn"
    assert vigenere_decrypt("Rijvs Uyvjn", "key") == "Hello World"
    assert vigenere_encrypt("Halo Dunia", "RAHASIA") == "Yaso Vcnza"


# ============================================================
# Encoding - Base64
# ============================================================
def test_base64_tetap():
    assert base64_encode("Hello") == "SGVsbG8="
    assert base64_decode("SGVsbG8=") == "Hello"
    assert base64_encode("Halo Dunia") == "SGFsbyBEdW5pYQ=="


# ============================================================
# Hashing
# ============================================================
def test_hash_sha256_tetap():
    result = hash_compute("abc", "SHA256")
    assert result.output_hash == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_hash_md5_tetap():
    result = hash_compute("abc", "MD5")
    assert result.output_hash == "900150983cd24fb0d6963f7d28e17f72"


# ============================================================
# Roundtrip simetris/asimetris (deterministic via roundtrip)
# ============================================================
def test_aes_roundtrip_tetap():
    from cryptolab import aes_decrypt, aes_encrypt

    key = "kunci16byte-rahasia"[:16]
    iv = "0123456789abcdef"
    enc = aes_encrypt("Halo Dunia", key, mode="CBC", iv=iv)
    dec = aes_decrypt(enc.output_text, key, mode="CBC", iv=iv)
    assert dec.output_text == "Halo Dunia"


def test_des_roundtrip_tetap():
    from cryptolab import des_decrypt, des_encrypt

    key = "kunci123"
    iv = "01234567"
    enc = des_encrypt("Halo Dunia", key, mode="CBC", iv=iv)
    dec = des_decrypt(enc.output_text, key, mode="CBC", iv=iv)
    assert dec.output_text == "Halo Dunia"
