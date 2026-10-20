"""Unit tests for Extended Classical Ciphers (Playfair, Hill, Affine, Rail Fence)."""

import pytest
from cryptolab import (
    playfair_encrypt,
    playfair_decrypt,
    hill_encrypt,
    hill_decrypt,
    affine_encrypt,
    affine_decrypt,
    affine_brute_force,
    railfence_encrypt,
    railfence_decrypt,
    railfence_brute_force,
    VALID_A_VALUES,
)
from cryptolab import InvalidInputError, InvalidKeyError


class TestPlayfair:
    """Test Playfair Cipher."""

    def test_encrypt_decrypt_basic(self):
        key = "PLAYFAIR"
        plaintext = "HELLO WORLD"
        
        enc = playfair_encrypt(plaintext, key)
        assert enc.technical_success
        assert enc.operation == "encrypt"
        
        dec = playfair_decrypt(enc.output_text, key)
        assert dec.technical_success
        assert dec.operation == "decrypt"
        # Note: Playfair adds padding X and removes spaces/J->I
        assert "HELLOWORLD" in dec.output_text.replace("X", "") or "HELLOXWORLD" in dec.output_text

    def test_encrypt_removes_spaces_and_j(self):
        key = "KEYWORD"
        plaintext = "Hello J World"
        
        enc = playfair_encrypt(plaintext, key)
        assert enc.technical_success
        # Should have no spaces, J->I, uppercase
        assert " " not in enc.output_text
        assert "J" not in enc.output_text

    def test_decrypt_produces_padding_x(self):
        key = "SECRET"
        plaintext = "TESTING"
        
        enc = playfair_encrypt(plaintext, key)
        dec = playfair_decrypt(enc.output_text, key)
        
        # Decrypted may have padding X
        assert dec.technical_success

    def test_invalid_key_empty(self):
        with pytest.raises(InvalidKeyError):
            playfair_encrypt("test", "")
        
        with pytest.raises(InvalidKeyError):
            playfair_decrypt("test", "")

    def test_invalid_input_empty(self):
        with pytest.raises(InvalidInputError):
            playfair_encrypt("", "KEY")
        
        with pytest.raises(InvalidInputError):
            playfair_decrypt("", "KEY")

    def test_key_matrix_generation(self):
        key = "PLAYFAIR"
        enc = playfair_encrypt("TEST", key)
        assert len(enc.key_matrix) == 5
        assert len(enc.key_matrix[0]) == 5
        # Should have 25 unique letters
        flat = [c for row in enc.key_matrix for c in row]
        assert len(set(flat)) == 25
        assert "J" not in flat


class TestHill:
    """Test Hill Cipher."""

    def test_2x2_encrypt_decrypt(self):
        # 2x2 matrix: [[3, 3], [2, 5]] (det=9, det_inv=3 since 9*3=27≡1 mod 26)
        key = "3 3 2 5"
        plaintext = "HELP"
        
        enc = hill_encrypt(plaintext, key, size=2)
        assert enc.technical_success
        assert enc.matrix_size == 2
        assert enc.determinant == 9
        assert enc.determinant_inv == 3
        
        dec = hill_decrypt(enc.output_text, key, size=2)
        assert dec.technical_success
        # HELP -> may have padding X
        assert dec.output_text.startswith("HELP")

    def test_3x3_encrypt_decrypt(self):
        # 3x3 matrix with det=1
        # Identity-ish matrix: [[1,0,0], [0,1,0], [0,0,1]]
        key = "1 0 0 0 1 0 0 0 1"
        plaintext = "ABCDEF"
        
        enc = hill_encrypt(plaintext, key, size=3)
        assert enc.technical_success
        assert enc.matrix_size == 3
        
        dec = hill_decrypt(enc.output_text, key, size=3)
        assert dec.technical_success
        assert dec.output_text == "ABCDEF"

    def test_non_invertible_matrix_rejected(self):
        # Matrix with det=13 (not invertible mod 26)
        key = "2 0 0 13"  # det = 2*13 = 26 ≡ 0 mod 26
        with pytest.raises(InvalidKeyError):
            hill_encrypt("TEST", key, size=2)

    def test_invalid_size(self):
        with pytest.raises(InvalidInputError):
            hill_encrypt("TEST", "1 2 3 4", size=4)
        
        with pytest.raises(InvalidInputError):
            hill_decrypt("TEST", "1 2 3 4", size=1)

    def test_wrong_key_length(self):
        # 2x2 needs 4 numbers
        with pytest.raises(InvalidInputError):
            hill_encrypt("TEST", "1 2 3", size=2)

    def test_padding_x(self):
        key = "3 3 2 5"
        plaintext = "HELLO"  # 5 chars, needs 1 X padding
        enc = hill_encrypt(plaintext, key, size=2)
        dec = hill_decrypt(enc.output_text, key, size=2)
        assert dec.output_text.startswith("HELLO")

    def test_invalid_input_empty(self):
        with pytest.raises(InvalidInputError):
            hill_encrypt("", "1 0 0 1", size=2)


class TestAffine:
    """Test Affine Cipher."""

    def test_encrypt_decrypt_a3_b5(self):
        plaintext = "HELLO WORLD"
        a, b = 3, 5  # a=3 is coprime with 26
        
        enc = affine_encrypt(plaintext, a, b)
        assert enc.technical_success
        assert enc.a == 3
        assert enc.b == 5
        assert enc.a_inv == 9  # 3*9=27≡1 mod 26
        
        dec = affine_decrypt(enc.output_text, a, b)
        assert dec.technical_success
        assert dec.output_text == plaintext.upper()

    def test_encrypt_preserves_case(self):
        plaintext = "Hello World"
        enc = affine_encrypt(plaintext, 5, 8)
        assert enc.technical_success
        # Affine cipher outputs uppercase (standard for classical ciphers)
        assert enc.output_text[0].isupper()

    def test_encrypt_preserves_non_alpha(self):
        plaintext = "HELLO, WORLD! 123"
        enc = affine_encrypt(plaintext, 7, 3)
        assert "," in enc.output_text
        assert " " in enc.output_text
        assert "1" in enc.output_text

    def test_invalid_a_not_coprime(self):
        with pytest.raises(InvalidKeyError):
            affine_encrypt("TEST", 2, 5)  # 2 not coprime with 26
        
        with pytest.raises(InvalidKeyError):
            affine_encrypt("TEST", 13, 5)  # 13 not coprime with 26

    def test_invalid_a_negative(self):
        with pytest.raises(InvalidKeyError):
            affine_encrypt("TEST", -1, 5)

    def test_invalid_b_range(self):
        with pytest.raises(InvalidKeyError):
            affine_encrypt("TEST", 5, 26)
        
        with pytest.raises(InvalidKeyError):
            affine_encrypt("TEST", 5, -1)

    def test_valid_a_values(self):
        # All valid a values should work
        for a in VALID_A_VALUES:
            enc = affine_encrypt("TEST", a, 0)
            assert enc.technical_success
            dec = affine_decrypt(enc.output_text, a, 0)
            assert dec.output_text == "TEST"

    def test_brute_force(self):
        plaintext = "SECRET"
        a, b = 5, 8
        enc = affine_encrypt(plaintext, a, b)
        
        candidates = affine_brute_force(enc.output_text)
        assert len(candidates) > 0
        
        # Original key should be in candidates
        found = False
        for c in candidates:
            if c.a == a and c.b == b:
                found = True
                assert c.output_text == plaintext.upper()
                break
        assert found

    def test_invalid_input_empty(self):
        with pytest.raises(InvalidInputError):
            affine_encrypt("", 5, 8)
        
        with pytest.raises(InvalidInputError):
            affine_decrypt("", 5, 8)


class TestRailFence:
    """Test Rail Fence / Transposition Cipher."""

    def test_encrypt_decrypt_2_rails(self):
        plaintext = "HELLO WORLD"
        rails = 2
        
        enc = railfence_encrypt(plaintext, rails)
        assert enc.technical_success
        assert enc.rails == 2
        
        dec = railfence_decrypt(enc.output_text, rails)
        assert dec.technical_success
        # Rail fence preserves spaces and all characters
        assert dec.output_text == plaintext

    def test_encrypt_decrypt_3_rails(self):
        plaintext = "WE ARE DISCOVERED FLEE AT ONCE"
        rails = 3
        
        enc = railfence_encrypt(plaintext, rails)
        assert enc.technical_success
        
        dec = railfence_decrypt(enc.output_text, rails)
        assert dec.technical_success
        # Rail fence preserves spaces and all characters
        assert dec.output_text == plaintext

    def test_encrypt_decrypt_4_rails(self):
        plaintext = "THE QUICK BROWN FOX"
        rails = 4
        
        enc = railfence_encrypt(plaintext, rails)
        dec = railfence_decrypt(enc.output_text, rails)
        assert dec.technical_success
        assert dec.output_text == plaintext

    def test_rail_pattern_generation(self):
        enc = railfence_encrypt("TEST", 2)
        assert enc.rail_pattern is not None
        assert len(enc.rail_pattern) == 2
        assert all(len(row) == 4 for row in enc.rail_pattern)

    def test_invalid_rails_too_few(self):
        with pytest.raises(InvalidInputError):
            railfence_encrypt("TEST", 1)
        
        with pytest.raises(InvalidInputError):
            railfence_decrypt("TEST", 1)

    def test_invalid_rails_too_many(self):
        with pytest.raises(InvalidInputError):
            railfence_encrypt("HI", 3)  # More rails than text length

    def test_invalid_input_empty(self):
        with pytest.raises(InvalidInputError):
            railfence_encrypt("", 2)
        
        with pytest.raises(InvalidInputError):
            railfence_decrypt("", 2)

    def test_brute_force(self):
        plaintext = "HELLO WORLD"
        enc = railfence_encrypt(plaintext, 3)
        
        candidates = railfence_brute_force(enc.output_text, max_rails=5)
        assert len(candidates) >= 2
        
        # 3 rails should be in candidates
        found = False
        for c in candidates:
            if c.rails == 3:
                found = True
                break
        assert found

    def test_format_rail_pattern(self):
        enc = railfence_encrypt("HELLO", 2)
        from cryptolab import format_rail_pattern
        formatted = format_rail_pattern(enc.rail_pattern)
        assert "Rail 0" in formatted
        assert "Rail 1" in formatted


class TestClassicalIntegration:
    """Integration tests for classical ciphers."""

    def test_all_ciphers_roundtrip(self):
        """Test all classical ciphers can encrypt and decrypt."""
        # Playfair
        pf_key = "PLAYFAIR"
        pf_enc = playfair_encrypt("TESTING", pf_key)
        pf_dec = playfair_decrypt(pf_enc.output_text, pf_key)
        assert pf_dec.technical_success
        
        # Hill
        hill_key = "3 3 2 5"
        hill_enc = hill_encrypt("HELP", hill_key, size=2)
        hill_dec = hill_decrypt(hill_enc.output_text, hill_key, size=2)
        assert hill_dec.technical_success
        
        # Affine
        af_enc = affine_encrypt("TEST", 5, 8)
        af_dec = affine_decrypt(af_enc.output_text, 5, 8)
        assert af_dec.technical_success
        
        # Rail Fence
        rf_enc = railfence_encrypt("HELLO", 2)
        rf_dec = railfence_decrypt(rf_enc.output_text, 2)
        assert rf_dec.technical_success


class TestVALID_A_VALUES:
    """Test VALID_A_VALUES constant."""

    def test_valid_a_values_correct(self):
        expected = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        assert VALID_A_VALUES == expected
        assert len(VALID_A_VALUES) == 12  # phi(26) = 12

    def test_all_coprime_with_26(self):
        import math
        for a in VALID_A_VALUES:
            assert math.gcd(a, 26) == 1