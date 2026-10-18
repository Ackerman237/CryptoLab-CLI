"""Unit tests for Vigenere Cipher."""

import pytest
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.exceptions import InvalidInputError, InvalidKeyError


class TestVigenereCipher:
    """Test suite for Vigenere Cipher."""

    def test_basic_encryption_and_decryption(self):
        plaintext = "ATTACKATDAWN"
        key = "LEMON"
        ciphertext = vigenere_encrypt(plaintext, key)
        assert ciphertext == "LXFOPVEFRNHR"
        assert vigenere_decrypt(ciphertext, key) == plaintext

    def test_round_trip_with_spaces_and_casing(self):
        sample = "Praktikum Keamanan Informasi: Lab 2026! Belajar Kriptografi."
        key = "KUNCI"
        encrypted = vigenere_encrypt(sample, key)
        decrypted = vigenere_decrypt(encrypted, key)
        assert decrypted == sample

    def test_key_advances_only_on_alphabet_letters(self):
        # Plaintext with spaces and punctuation:
        # P (0) r (1) a (2) k (3) t (4) i (0) k (1) u (2) m (3) ...
        # Non-alphabets (space, :) do not advance key index
        sample = "A B C"
        key = "BA"  # B shifts by 1, A shifts by 0
        # A -> B (key B), ' ' -> ' ', B -> B (key A), ' ' -> ' ', C -> D (key B)
        encrypted = vigenere_encrypt(sample, key)
        assert encrypted == "B B D"
        assert vigenere_decrypt(encrypted, key) == sample

    def test_case_insensitive_key(self):
        sample = "SecretMessage"
        upper_enc = vigenere_encrypt(sample, "KEY")
        lower_enc = vigenere_encrypt(sample, "key")
        mixed_enc = vigenere_encrypt(sample, "kEy")
        assert upper_enc == lower_enc == mixed_enc

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            vigenere_encrypt("", "KEY")
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            vigenere_decrypt("", "KEY")

    def test_empty_key_raises_invalid_key_error(self):
        with pytest.raises(InvalidKeyError, match="Kunci tidak boleh kosong"):
            vigenere_encrypt("Hello", "")
        with pytest.raises(InvalidKeyError, match="Kunci tidak boleh kosong"):
            vigenere_decrypt("Hello", "")

    def test_invalid_key_characters_raises_error(self):
        with pytest.raises(InvalidKeyError, match="hanya boleh berisi huruf alfabet"):
            vigenere_encrypt("Hello", "KEY123")
        with pytest.raises(InvalidKeyError, match="hanya boleh berisi huruf alfabet"):
            vigenere_encrypt("Hello", "SECRET KEY")
        with pytest.raises(InvalidKeyError, match="hanya boleh berisi huruf alfabet"):
            vigenere_encrypt("Hello", "KEY!")

    def test_invalid_type_raises_error(self):
        with pytest.raises(InvalidInputError, match="harus berupa string"):
            vigenere_encrypt(None, "KEY")  # type: ignore
        with pytest.raises(InvalidKeyError, match="harus berupa string"):
            vigenere_encrypt("Hello", 123)  # type: ignore
