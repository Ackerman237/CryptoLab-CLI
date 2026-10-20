"""Tahap 1 - Pemisah Binary & Hex (upgrade-spec.md).

Decode membuang semua karakter non-data (aman karena pemisah kustom
dilarang memuat karakter data). Output encode lama tetap identik
(diverifikasi lewat tests/test_upgrade_baseline.py).
"""

import pytest

from cryptolab import binary_decode, binary_encode, hex_decode, hex_encode
from cryptolab.core.exceptions import DecodingError


# ============================================================
# Decode dengan pemisah non-spasi (baru di Tahap 1)
# ============================================================
def test_binary_decode_pemisah_umum():
    assert binary_decode("01001000,01101001") == "Hi"
    assert binary_decode("01001000, 01101001") == "Hi"
    assert binary_decode("01001000-01101001") == "Hi"
    assert binary_decode("01001000.01101001") == "Hi"


def test_binary_decode_pemisah_kustom():
    # Pemisah kustom maks 3 karakter tanpa '0'/'1' -> dibuang saat decode.
    encoded = binary_encode("Halo", delimiter="##")
    assert binary_decode(encoded) == "Halo"


def test_binary_decode_pemisah_error_jelas():
    # Pemisah bukan spasi: validasi kelipatan-8 tetap jelas (tanpa crash).
    with pytest.raises(DecodingError) as exc:
        binary_decode("01001000,011010")
    assert "kelipatan 8" in str(exc.value)

    # Tidak ada bit sama sekali -> karakter tidak valid (pesan lama).
    with pytest.raises(DecodingError) as exc:
        binary_decode("hello")
    assert "tidak valid" in str(exc.value)


def test_hex_decode_pemisah_umum():
    assert hex_decode("48,69") == "Hi"
    assert hex_decode("48.69") == "Hi"
    assert hex_decode("48_69") == "Hi"


def test_hex_decode_pemisah_kustom():
    encoded = hex_encode("Halo", delimiter="##")
    assert hex_decode(encoded) == "Halo"


def test_hex_decode_prefix_0x_di_awal_tetap():
    assert hex_decode("0x48 69") == "Hi"
    # '0x' di tengah string tetap ditolak (perilaku lama, dibekukan baseline).
    with pytest.raises(DecodingError):
        hex_decode("0x48 0x69")


# ============================================================
# Encode: parameter delimiter default tidak berubah
# ============================================================
def test_encode_default_tetap_spasi():
    assert binary_encode("Hi") == "01001000 01101001"
    assert hex_encode("Hi") == "48 69"
