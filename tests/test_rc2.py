"""Tests for legacy RC2/ARC2 support."""

import pytest

from cryptolab import create_parser, handle_cli_args
from cryptolab import InvalidInputError, InvalidKeyError
from cryptolab import rc2_decrypt, rc2_encrypt


CHALLENGE_CIPHERTEXT = "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8"


def test_rc2_challenge_vector():
    result = rc2_decrypt(
        CHALLENGE_CIPHERTEXT,
        key="12345678",
        mode="CBC",
        iv="qwertyui",
        padding="PKCS7",
    )
    assert result.output_text == "laboratorium_keamanan_3d"
    assert result.raw_bytes.hex() == "6c61626f7261746f7269756d5f6b65616d616e616e5f3364"


def test_rc2_cbc_round_trip_pkcs7():
    encrypted = rc2_encrypt("RC2 legacy lab", "12345678", "CBC", "qwertyui")
    decrypted = rc2_decrypt(encrypted.output_text, "12345678", "CBC", "qwertyui")
    assert decrypted.output_text == "RC2 legacy lab"


def test_rc2_validates_key_and_iv():
    with pytest.raises(InvalidKeyError):
        rc2_encrypt("data", "1234", "CBC", "qwertyui")
    with pytest.raises(InvalidInputError):
        rc2_encrypt("data", "12345678", "CBC", "short")


def test_rc2_cli_decrypt(capsys):
    parser = create_parser()
    args = parser.parse_args([
        "--no-history", "rc2", "decrypt", "-t", CHALLENGE_CIPHERTEXT,
        "-k", "12345678", "--iv", "qwertyui", "-m", "CBC",
    ])
    assert handle_cli_args(args) == 0
    assert "laboratorium_keamanan_3d" in capsys.readouterr().out