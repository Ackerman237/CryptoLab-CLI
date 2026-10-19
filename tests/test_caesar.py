"""Unit tests for Caesar Cipher."""

import pytest
from cryptolab import caesar_encrypt, caesar_decrypt
from cryptolab import InvalidInputError


class TestCaesarCipher:
    """Test suite for Caesar Cipher encryption, decryption, and edge cases."""

    def test_basic_encryption_and_decryption(self):
        plaintext = "Hello, World!"
        shift = 3
        ciphertext = caesar_encrypt(plaintext, shift)
        assert ciphertext == "Khoor, Zruog!"
        assert caesar_decrypt(ciphertext, shift) == plaintext

    def test_round_trip(self):
        sample = "The Quick Brown Fox Jumps Over 13 Lazy Dogs! #Crypto2026"
        for shift in [0, 1, 13, 25, 26, 27, 52, 100, -1, -25, -29]:
            encrypted = caesar_encrypt(sample, shift)
            decrypted = caesar_decrypt(encrypted, shift)
            assert decrypted == sample

    def test_zero_shift(self):
        text = "No change here! 12345"
        assert caesar_encrypt(text, 0) == text
        assert caesar_decrypt(text, 0) == text

    def test_shift_greater_than_26(self):
        text = "CyberSecurity"
        # Shift 29 is equivalent to shift 3 (29 % 26 = 3)
        assert caesar_encrypt(text, 29) == caesar_encrypt(text, 3)
        assert caesar_decrypt(caesar_encrypt(text, 29), 29) == text

    def test_preserves_case_spaces_and_punctuation(self):
        text = "Flag{C43s4r_Is_C00l!}"
        encrypted = caesar_encrypt(text, 7)
        assert encrypted == "Mshn{J43z4y_Pz_J00s!}"
        assert caesar_decrypt(encrypted, 7) == text

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            caesar_encrypt("", 3)
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            caesar_decrypt("", 3)

    def test_invalid_type_input_raises_error(self):
        with pytest.raises(InvalidInputError, match="harus berupa string"):
            caesar_encrypt(None, 3)  # type: ignore
        with pytest.raises(InvalidInputError, match="harus berupa bilangan bulat"):
            caesar_encrypt("Hello", "three")  # type: ignore
        with pytest.raises(InvalidInputError, match="harus berupa bilangan bulat"):
            caesar_encrypt("Hello", 3.14)  # type: ignore
