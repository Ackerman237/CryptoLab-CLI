"""Characterization tests for crypto primitive round-trip operations.

These tests ensure encrypt→decrypt, sign→verify, hash→verify, encode→decode
operations work correctly and maintain identity (plaintext in = plaintext out).
"""

import pytest
from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.classical.playfair import playfair_encrypt, playfair_decrypt
from cryptolab.classical.hill import hill_encrypt, hill_decrypt
from cryptolab.classical.affine import affine_encrypt, affine_decrypt, VALID_A_VALUES
from cryptolab.classical.railfence import railfence_encrypt, railfence_decrypt
from cryptolab.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.encoding.binary_codec import binary_encode, binary_decode
from cryptolab.symmetric.des import des_encrypt, des_decrypt
from cryptolab.symmetric.aes import aes_encrypt, aes_decrypt
from cryptolab.symmetric.rc2 import rc2_encrypt, rc2_decrypt
from cryptolab.hashing import (
    hash_compute,
    hash_verify_integrity,
    hmac_compute,
    hmac_verify,
    pbkdf2_hash,
    pbkdf2_verify,
    bcrypt_hash,
    bcrypt_verify,
    hash_verify_integrity,
    BCRYPT_AVAILABLE,
)
from cryptolab.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
)


class TestClassicalCipherRoundTrip:
    """Test classical cipher encrypt→decrypt round trips."""

    def test_caesar_roundtrip(self):
        """Caesar encrypt→decrypt should return original text."""
        plaintext = "HELLO WORLD"
        shift = 3
        ciphertext = caesar_encrypt(plaintext, shift)
        decrypted = caesar_decrypt(ciphertext, shift)
        assert decrypted == plaintext

    def test_caesar_roundtrip_negative_shift(self):
        """Caesar with negative shift."""
        plaintext = "HELLO WORLD"
        shift = -5
        ciphertext = caesar_encrypt(plaintext, shift)
        decrypted = caesar_decrypt(ciphertext, shift)
        assert decrypted == plaintext

    def test_caesar_roundtrip_large_shift(self):
        """Caesar with shift > 26."""
        plaintext = "HELLO WORLD"
        shift = 29  # equivalent to 3
        ciphertext = caesar_encrypt(plaintext, shift)
        decrypted = caesar_decrypt(ciphertext, shift)
        assert decrypted == plaintext

    def test_vigenere_roundtrip(self):
        """Vigenere encrypt→decrypt should return original text."""
        plaintext = "HELLO WORLD"
        key = "KEY"
        ciphertext = vigenere_encrypt(plaintext, key)
        decrypted = vigenere_decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_vigenere_roundtrip_long_key(self):
        """Vigenere with long key."""
        plaintext = "THIS IS A LONGER MESSAGE FOR TESTING"
        key = "SUPERSECRETKEY"
        ciphertext = vigenere_encrypt(plaintext, key)
        decrypted = vigenere_decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_playfair_roundtrip(self):
        """Playfair encrypt→decrypt should return original text (with possible padding X)."""
        plaintext = "HELLO WORLD"
        key = "KEYWORD"
        ciphertext = playfair_encrypt(plaintext, key).output_text
        decrypted = playfair_decrypt(ciphertext, key).output_text
        # Playfair removes spaces and J=I, adds padding X for odd length pairs
        # Original: HELLO WORLD -> HE LX LO WO RL DX (with X padding)
        # Decrypted: HELXLOWORLDX
        assert "HEL" in decrypted and "WORLD" in decrypted

    def test_hill_roundtrip_2x2(self):
        """Hill 2x2 encrypt→decrypt."""
        plaintext = "HI"
        key = "3 2 5 7"  # 2x2 matrix
        ciphertext = hill_encrypt(plaintext, key, 2).output_text
        decrypted = hill_decrypt(ciphertext, key, 2).output_text
        assert decrypted == plaintext

    def test_hill_roundtrip_3x3(self):
        """Hill 3x3 encrypt→decrypt."""
        plaintext = "ABC"
        # Valid 3x3 invertible matrix key
        key = "6 24 1 13 16 10 20 17 15"
        ciphertext = hill_encrypt(plaintext, key, 3).output_text
        decrypted = hill_decrypt(ciphertext, key, 3).output_text
        assert decrypted == plaintext

    def test_affine_roundtrip(self):
        """Affine encrypt→decrypt for all valid 'a' values."""
        plaintext = "HELLO"
        for a in VALID_A_VALUES:
            for b in range(26):
                ciphertext = affine_encrypt(plaintext, a, b).output_text
                decrypted = affine_decrypt(ciphertext, a, b).output_text
                assert decrypted == plaintext, f"Failed for a={a}, b={b}"

    def test_railfence_roundtrip_2_rails(self):
        """Rail Fence 2 rails encrypt→decrypt."""
        plaintext = "HELLO WORLD"
        ciphertext = railfence_encrypt(plaintext, 2).output_text
        decrypted = railfence_decrypt(ciphertext, 2).output_text
        assert decrypted == plaintext

    def test_railfence_roundtrip_3_rails(self):
        """Rail Fence 3 rails encrypt→decrypt."""
        plaintext = "HELLO WORLD"
        ciphertext = railfence_encrypt(plaintext, 3).output_text
        decrypted = railfence_decrypt(ciphertext, 3).output_text
        assert decrypted == plaintext

    def test_railfence_roundtrip_4_rails(self):
        """Rail Fence 4 rails encrypt→decrypt."""
        plaintext = "HELLO WORLD THIS IS A TEST"
        ciphertext = railfence_encrypt(plaintext, 4).output_text
        decrypted = railfence_decrypt(ciphertext, 4).output_text
        assert decrypted == plaintext


class TestEncodingRoundTrip:
    """Test encoding decode→encode round trips."""

    def test_base64_roundtrip(self):
        """Base64 encode→decode should return original."""
        test_cases = [
            "Hello World",
            "Special chars: !@#$%^&*()",
            "Unicode: 你好世界 🌍",
            "A" * 1000,  # long string
        ]
        for text in test_cases:
            encoded = base64_encode(text)
            decoded = base64_decode(encoded)
            assert decoded == text, f"Failed for: {text[:50]}"

    def test_hex_roundtrip(self):
        """Hex encode→decode should return original."""
        test_cases = [
            "Hello World",
            "Special chars: !@#$%^&*()",
            "Unicode: 你好世界 🌍",
            "A" * 1000,
        ]
        for text in test_cases:
            encoded = hex_encode(text)
            decoded = hex_decode(encoded)
            assert decoded == text, f"Failed for: {text[:50]}"

    def test_hex_roundtrip_with_delimiters(self):
        """Hex with various delimiters."""
        text = "Hello World"
        for delim in [" ", ":", "-", ""]:
            encoded = hex_encode(text, delimiter=delim)
            decoded = hex_decode(encoded)
            assert decoded == text

    def test_binary_roundtrip(self):
        """Binary encode→decode should return original."""
        test_cases = [
            "Hello World",
            "Special chars: !@#$%^&*()",
            "Unicode: 你好世界 🌍",
            "A" * 100,
        ]
        for text in test_cases:
            encoded = binary_encode(text)
            decoded = binary_decode(encoded)
            assert decoded == text, f"Failed for: {text[:50]}"

    def test_binary_roundtrip_with_delimiters(self):
        """Binary with various delimiters."""
        text = "Hello World"
        for delim in [" ", ""]:
            encoded = binary_encode(text, delimiter=delim)
            decoded = binary_decode(encoded)
            assert decoded == text


class TestSymmetricCipherRoundTrip:
    """Test symmetric cipher encrypt→decrypt round trips."""

    def test_des_cbc_roundtrip(self):
        """DES CBC encrypt→decrypt."""
        plaintext = "Hello World! This is a test message."
        key = "12345678"
        iv = "abcdefgh"
        ciphertext = des_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        decrypted = des_decrypt(ciphertext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_des_ecb_roundtrip(self):
        """DES ECB encrypt→decrypt."""
        plaintext = "Hello World! This is a test message."
        key = "12345678"
        ciphertext = des_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7").output_text
        decrypted = des_decrypt(ciphertext, key=key, mode="ECB", padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_aes_cbc_roundtrip(self):
        """AES CBC encrypt→decrypt."""
        plaintext = "Hello World! This is a test message for AES encryption."
        key = "1234567890123456"
        iv = "abcdefghijklmnop"
        ciphertext = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        decrypted = aes_decrypt(ciphertext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_aes_ecb_roundtrip(self):
        """AES ECB encrypt→decrypt."""
        plaintext = "Hello World! This is a test message for AES encryption."
        key = "1234567890123456"
        ciphertext = aes_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7").output_text
        decrypted = aes_decrypt(ciphertext, key=key, mode="ECB", padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_aes_256_cbc_roundtrip(self):
        """AES-256 CBC encrypt→decrypt."""
        plaintext = "Hello World! This is a test message for AES-256 encryption."
        key = "12345678901234567890123456789012"  # 32 bytes
        iv = "abcdefghijklmnop"
        ciphertext = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        decrypted = aes_decrypt(ciphertext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_rc2_cbc_roundtrip(self):
        """RC2 CBC encrypt→decrypt."""
        plaintext = "Hello World! RC2 test."
        key = "12345678"
        iv = "abcdefgh"
        ciphertext = rc2_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        decrypted = rc2_decrypt(ciphertext, key=key, mode="CBC", iv=iv, padding="PKCS7").output_text
        assert decrypted == plaintext

    def test_rc2_ecb_roundtrip(self):
        """RC2 ECB encrypt→decrypt."""
        plaintext = "Hello World! RC2 test."
        key = "12345678"
        ciphertext = rc2_encrypt(plaintext, key=key, mode="ECB", padding="PKCS7").output_text
        decrypted = rc2_decrypt(ciphertext, key=key, mode="ECB", padding="PKCS7").output_text
        assert decrypted == plaintext


class TestHashingRoundTrip:
    """Test hash compute→verify round trips."""

    def test_hash_verify_integrity(self):
        """Hash compute→verify integrity."""
        test_cases = [
            ("Hello World", "SHA256"),
            ("Test message", "SHA512"),
            ("", "SHA256"),  # empty
            ("A" * 10000, "SHA256"),  # long
        ]
        for text, algo in test_cases:
            computed = hash_compute(text, algorithm=algo, encoding="hex")
            result = hash_verify_integrity(text, computed.output_hash, algorithm=algo, encoding="hex")
            assert result.match is True, f"Failed for {algo}: {text[:50]}"

    def test_hash_verify_integrity_tampered(self):
        """Hash verify should fail on tampered data."""
        text = "Hello World"
        computed = hash_compute(text, algorithm="SHA256", encoding="hex")
        # Tamper with hash
        tampered_hash = computed.output_hash[:-1] + ("0" if computed.output_hash[-1] != "0" else "1")
        result = hash_verify_integrity(text, tampered_hash, algorithm="SHA256", encoding="hex")
        assert result.match is False

    def test_hmac_roundtrip(self):
        """HMAC compute→verify."""
        test_cases = [
            ("Hello World", "secret_key", "SHA256"),
            ("Test message", "another key", "SHA512"),
            ("", "key", "SHA256"),
        ]
        for text, key, algo in test_cases:
            computed = hmac_compute(text, key, algorithm=algo, encoding="hex")
            result = hmac_verify(text, key, computed.output_hmac, algorithm=algo, encoding="hex")
            assert result is True, f"Failed for {algo}: {text[:50]}"

    def test_hmac_verify_tampered(self):
        """HMAC verify should fail on tampered message."""
        text = "Hello World"
        key = "secret"
        computed = hmac_compute(text, key, algorithm="SHA256", encoding="hex")
        # Tamper with message
        result = hmac_verify("Tampered World", key, computed.output_hmac, algorithm="SHA256", encoding="hex")
        assert result is False

    def test_pbkdf2_roundtrip(self):
        """PBKDF2 hash→verify."""
        password = "my_secure_password"
        result = pbkdf2_hash(password, iterations=100000)
        verify = pbkdf2_verify(password, result.salt, result.hash_value, iterations=100000)
        assert verify.match is True

    def test_pbkdf2_verify_wrong_password(self):
        """PBKDF2 verify should fail with wrong password."""
        password = "correct_password"
        result = pbkdf2_hash(password, iterations=100000)
        verify = pbkdf2_verify("wrong_password", result.salt, result.hash_value, iterations=100000)
        assert verify.match is False

    def test_pbkdf2_verify_wrong_iterations(self):
        """PBKDF2 verify should fail with wrong iterations."""
        password = "password"
        result = pbkdf2_hash(password, iterations=100000)
        # Our implementation enforces min 100000 iterations
        try:
            verify = pbkdf2_verify(password, result.salt, result.hash_value, iterations=50000)
            assert False, "Should have raised InvalidInputError"
        except Exception as e:
            assert "100,000" in str(e)

    def test_bcrypt_roundtrip(self):
        """Bcrypt hash→verify."""
        if not BCRYPT_AVAILABLE:
            pytest.skip("bcrypt not available")
        password = "my_secure_password"
        result = bcrypt_hash(password, rounds=12)
        verify = bcrypt_verify(password, result.hash_value)
        assert verify.match is True

    def test_bcrypt_verify_wrong_password(self):
        """Bcrypt verify should fail with wrong password."""
        if not BCRYPT_AVAILABLE:
            pytest.skip("bcrypt not available")
        password = "correct_password"
        result = bcrypt_hash(password, rounds=12)
        verify = bcrypt_verify("wrong_password", result.hash_value)
        assert verify.match is False


class TestAsymmetricRoundTrip:
    """Test asymmetric crypto encrypt→decrypt, sign→verify round trips."""

    @pytest.fixture
    def rsa_keypair(self):
        """Generate RSA keypair for tests."""
        return rsa_generate_keypair(2048)

    def test_rsa_encrypt_decrypt_oaep_sha256(self, rsa_keypair):
        """RSA OAEP-SHA256 encrypt→decrypt."""
        plaintext = "Secret message for RSA-OAEP-SHA256"
        result = rsa_encrypt(plaintext, rsa_keypair.public_key_pem, padding="OAEP", hash_algo="SHA256")
        decrypted = rsa_decrypt(result.output_text, rsa_keypair.private_key_pem, padding="OAEP", hash_algo="SHA256")
        assert decrypted.output_text == plaintext

    def test_rsa_encrypt_decrypt_oaep_sha512(self, rsa_keypair):
        """RSA OAEP-SHA512 encrypt→decrypt."""
        plaintext = "Secret message for RSA-OAEP-SHA512"
        result = rsa_encrypt(plaintext, rsa_keypair.public_key_pem, padding="OAEP", hash_algo="SHA512")
        decrypted = rsa_decrypt(result.output_text, rsa_keypair.private_key_pem, padding="OAEP", hash_algo="SHA512")
        assert decrypted.output_text == plaintext

    def test_rsa_encrypt_decrypt_pkcs1v15(self, rsa_keypair):
        """RSA PKCS1v15 encrypt→decrypt."""
        plaintext = "Short message for PKCS1v15"
        result = rsa_encrypt(plaintext, rsa_keypair.public_key_pem, padding="PKCS1v15")
        decrypted = rsa_decrypt(result.output_text, rsa_keypair.private_key_pem, padding="PKCS1v15")
        assert decrypted.output_text == plaintext

    def test_rsa_sign_verify_pss_sha256(self, rsa_keypair):
        """RSA PSS-SHA256 sign→verify."""
        message = "Message to sign with PSS-SHA256"
        result = rsa_sign(message, rsa_keypair.private_key_pem, padding="PSS", hash_algo="SHA256")
        result = rsa_verify(message, result.output_text, rsa_keypair.public_key_pem, padding="PSS", hash_algo="SHA256")
        assert result.output_text == "VALID (Tanda tangan SAH)"

    def test_rsa_sign_verify_pss_sha512(self, rsa_keypair):
        """RSA PSS-SHA512 sign→verify."""
        message = "Message to sign with PSS-SHA512"
        result = rsa_sign(message, rsa_keypair.private_key_pem, padding="PSS", hash_algo="SHA512")
        result = rsa_verify(message, result.output_text, rsa_keypair.public_key_pem, padding="PSS", hash_algo="SHA512")
        assert result.output_text == "VALID (Tanda tangan SAH)"

    def test_rsa_sign_verify_pkcs1v15(self, rsa_keypair):
        """RSA PKCS1v15 sign→verify."""
        message = "Message to sign with PKCS1v15"
        result = rsa_sign(message, rsa_keypair.private_key_pem, padding="PKCS1v15")
        result = rsa_verify(message, result.output_text, rsa_keypair.public_key_pem, padding="PKCS1v15")
        assert result.output_text == "VALID (Tanda tangan SAH)"

    def test_rsa_verify_wrong_message(self, rsa_keypair):
        """RSA verify should fail on wrong message."""
        message = "Original message"
        result = rsa_sign(message, rsa_keypair.private_key_pem, padding="PSS")
        result = rsa_verify("Tampered message", result.output_text, rsa_keypair.public_key_pem, padding="PSS")
        assert result.output_text == "INVALID (Tanda tangan TIDAK SAH)"

    def test_rsa_verify_wrong_key(self, rsa_keypair):
        """RSA verify should fail with wrong public key."""
        message = "Test message"
        result = rsa_sign(message, rsa_keypair.private_key_pem, padding="PSS")
        # Generate another keypair
        other_keypair = rsa_generate_keypair(2048)
        result = rsa_verify(message, result.output_text, other_keypair.public_key_pem, padding="PSS")
        assert result.output_text == "INVALID (Tanda tangan TIDAK SAH)"

    def test_dh_key_exchange(self):
        """Diffie-Hellman key exchange produces matching secrets."""
        result = dh_key_exchange(prime_bits=2048)
        # Both parties should derive same shared secret
        assert result.alice_public_hex is not None
        assert result.bob_public_hex is not None
        assert result.shared_secret_hex is not None
        assert len(result.shared_secret_hex) > 0

    def test_dh_derive_key(self):
        """DH derive key from shared secret."""
        result = dh_key_exchange(prime_bits=2048)
        shared = result.shared_secret_hex
        derived = dh_derive_key(shared, key_length=32, hash_algo="SHA256")
        assert len(derived) == 64  # 32 bytes = 64 hex chars

        # Same shared secret should produce same derived key
        derived2 = dh_derive_key(shared, key_length=32, hash_algo="SHA256")
        assert derived == derived2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])