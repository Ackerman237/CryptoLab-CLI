"""Unit tests for Asymmetric Cryptography module."""

import pytest
from cryptolab import (
    rsa_generate_keypair,
    rsa_load_private_key,
    rsa_load_public_key,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_generate_parameters,
    dh_key_exchange,
    dh_derive_key,
    RSAKeyPair,
    RSAResult,
    DHKeyExchangeResult,
)
from cryptolab import InvalidInputError, DecodingError


class TestRSAKeyGeneration:
    """Test RSA key pair generation."""

    def test_generate_2048(self):
        kp = rsa_generate_keypair(2048)
        assert isinstance(kp, RSAKeyPair)
        assert kp.key_size == 2048
        assert kp.technical_success
        assert "PRIVATE KEY" in kp.private_key_pem
        assert "PUBLIC KEY" in kp.public_key_pem

    def test_generate_1024(self):
        kp = rsa_generate_keypair(1024)
        assert kp.key_size == 1024

    def test_generate_3072(self):
        kp = rsa_generate_keypair(3072)
        assert kp.key_size == 3072

    def test_generate_4096(self):
        kp = rsa_generate_keypair(4096)
        assert kp.key_size == 4096

    def test_invalid_key_size(self):
        with pytest.raises(InvalidInputError):
            rsa_generate_keypair(512)
        with pytest.raises(InvalidInputError):
            rsa_generate_keypair(1536)


class TestRSAKeyLoading:
    """Test RSA key loading."""

    def test_load_private_key(self):
        kp = rsa_generate_keypair(2048)
        private_key = rsa_load_private_key(kp.private_key_pem)
        assert private_key.size_in_bits() == 2048
        assert private_key.has_private()

    def test_load_public_key(self):
        kp = rsa_generate_keypair(2048)
        public_key = rsa_load_public_key(kp.public_key_pem)
        assert public_key.size_in_bits() == 2048
        assert not public_key.has_private()

    def test_invalid_private_key(self):
        with pytest.raises(InvalidInputError):
            rsa_load_private_key("invalid key data")

    def test_invalid_public_key(self):
        with pytest.raises(InvalidInputError):
            rsa_load_public_key("invalid key data")


class TestRSAEncryption:
    """Test RSA encryption and decryption."""

    def test_encrypt_decrypt_oaep_sha256(self):
        kp = rsa_generate_keypair(2048)
        plaintext = "Hello RSA-OAEP!"

        enc = rsa_encrypt(plaintext, kp.public_key_pem, padding="OAEP", hash_algo="SHA256")
        assert enc.technical_success
        assert enc.algorithm == "RSA-OAEP-SHA256"

        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, padding="OAEP", hash_algo="SHA256")
        assert dec.technical_success
        assert dec.output_text == plaintext

    def test_encrypt_decrypt_oaep_sha512(self):
        kp = rsa_generate_keypair(2048)
        plaintext = "Hello RSA-OAEP-SHA512!"

        enc = rsa_encrypt(plaintext, kp.public_key_pem, padding="OAEP", hash_algo="SHA512")
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, padding="OAEP", hash_algo="SHA512")
        assert dec.output_text == plaintext

    def test_encrypt_decrypt_pkcs1v15(self):
        kp = rsa_generate_keypair(2048)
        plaintext = "Hello PKCS1v15!"

        enc = rsa_encrypt(plaintext, kp.public_key_pem, padding="PKCS1v15")
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, padding="PKCS1v15")
        assert dec.output_text == plaintext

    def test_encrypt_base64(self):
        kp = rsa_generate_keypair(2048)
        enc = rsa_encrypt("test", kp.public_key_pem, encoding="base64")
        assert not enc.is_hex

    def test_decrypt_base64(self):
        kp = rsa_generate_keypair(2048)
        enc = rsa_encrypt("test", kp.public_key_pem, encoding="base64")
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, encoding="base64")
        assert dec.output_text == "test"

    def test_wrong_key_decrypt(self):
        kp1 = rsa_generate_keypair(2048)
        kp2 = rsa_generate_keypair(2048)
        enc = rsa_encrypt("secret", kp1.public_key_pem)
        with pytest.raises(DecodingError):
            rsa_decrypt(enc.output_text, kp2.private_key_pem)

    def test_wrong_padding_decrypt(self):
        kp = rsa_generate_keypair(2048)
        enc = rsa_encrypt("secret", kp.public_key_pem, padding="OAEP")
        with pytest.raises(DecodingError):
            rsa_decrypt(enc.output_text, kp.private_key_pem, padding="PKCS1v15")


class TestRSALengthLimits:
    """Test RSA message length limits."""

    def test_oaep_max_length(self):
        # 2048-bit key, OAEP-SHA256: max ~190 bytes
        kp = rsa_generate_keypair(2048)
        max_data = 2048 // 8 - 2 * 32 - 2  # 190 bytes
        data = "A" * max_data
        enc = rsa_encrypt(data, kp.public_key_pem, padding="OAEP", hash_algo="SHA256")
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, padding="OAEP", hash_algo="SHA256")
        assert dec.output_text == data

    def test_oaep_over_max_length(self):
        kp = rsa_generate_keypair(2048)
        # 191 bytes should fail for OAEP-SHA256
        data = "A" * 191
        with pytest.raises(InvalidInputError):
            rsa_encrypt(data, kp.public_key_pem, padding="OAEP", hash_algo="SHA256")

    def test_pkcs1v15_max_length(self):
        # 2048-bit key, PKCS1v15: max 245 bytes
        kp = rsa_generate_keypair(2048)
        max_data = 2048 // 8 - 11  # 245 bytes
        data = "A" * max_data
        enc = rsa_encrypt(data, kp.public_key_pem, padding="PKCS1v15")
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem, padding="PKCS1v15")
        assert dec.output_text == data


class TestRSASignature:
    """Test RSA signing and verification."""

    def test_sign_verify_pss_sha256(self):
        kp = rsa_generate_keypair(2048)
        message = "Sign this message"

        sig = rsa_sign(message, kp.private_key_pem, padding="PSS", hash_algo="SHA256")
        assert sig.technical_success
        assert sig.algorithm == "RSA-PSS-SHA256"

        verify = rsa_verify(message, sig.output_text, kp.public_key_pem, padding="PSS", hash_algo="SHA256")
        assert verify.technical_success
        assert verify.output_text == "VALID (Tanda tangan SAH)"

    def test_sign_verify_pss_sha512(self):
        kp = rsa_generate_keypair(2048)
        sig = rsa_sign("test", kp.private_key_pem, padding="PSS", hash_algo="SHA512")
        verify = rsa_verify("test", sig.output_text, kp.public_key_pem, padding="PSS", hash_algo="SHA512")
        assert verify.output_text == "VALID (Tanda tangan SAH)"

    def test_sign_verify_pkcs1v15(self):
        kp = rsa_generate_keypair(2048)
        sig = rsa_sign("test", kp.private_key_pem, padding="PKCS1v15")
        verify = rsa_verify("test", sig.output_text, kp.public_key_pem, padding="PKCS1v15")
        assert verify.output_text == "VALID (Tanda tangan SAH)"

    def test_verify_wrong_message(self):
        kp = rsa_generate_keypair(2048)
        sig = rsa_sign("original", kp.private_key_pem)
        verify = rsa_verify("tampered", sig.output_text, kp.public_key_pem)
        assert verify.output_text == "INVALID (Tanda tangan TIDAK SAH)"

    def test_verify_wrong_key(self):
        kp1 = rsa_generate_keypair(2048)
        kp2 = rsa_generate_keypair(2048)
        sig = rsa_sign("message", kp1.private_key_pem)
        verify = rsa_verify("message", sig.output_text, kp2.public_key_pem)
        assert verify.output_text == "INVALID (Tanda tangan TIDAK SAH)"

    def test_signature_base64(self):
        kp = rsa_generate_keypair(2048)
        sig = rsa_sign("test", kp.private_key_pem, encoding="base64")
        assert not sig.is_hex


class TestDHKeyExchange:
    """Test Diffie-Hellman Key Exchange."""

    def test_dh_2048(self):
        result = dh_key_exchange(2048)
        assert isinstance(result, DHKeyExchangeResult)
        assert result.technical_success
        assert result.generator == 2
        assert len(result.prime_hex) > 0
        assert result.alice_shared == result.bob_shared
        # Shared secret should match
        assert result.alice_shared == result.bob_shared

    def test_dh_3072(self):
        result = dh_key_exchange(3072)
        assert result.technical_success

    def test_dh_4096(self):
        result = dh_key_exchange(4096)
        assert result.technical_success

    def test_dh_custom_private_keys(self):
        # Test with known private keys
        result = dh_key_exchange(2048, alice_private=12345, bob_private=67890)
        # Note: even-length hex padding may add leading zero
        assert result.alice_private_hex in ("3039", "03039")  # 12345 in hex
        assert result.bob_private_hex in ("10932", "010932")  # 67890 in hex
        assert result.alice_shared == result.bob_shared

    def test_dh_shared_secret_matches(self):
        result = dh_key_exchange(2048)
        # Both parties should compute the same shared secret
        assert result.alice_shared == result.bob_shared

    def test_dh_derive_key(self):
        result = dh_key_exchange(2048)
        derived = dh_derive_key(result.shared_secret_hex, key_length=32, hash_algo="SHA256")
        assert len(derived) == 64  # 32 bytes = 64 hex chars

    def test_dh_derive_key_sha512(self):
        result = dh_key_exchange(2048)
        derived = dh_derive_key(result.shared_secret_hex, key_length=32, hash_algo="SHA512")
        assert len(derived) == 64

    def test_dh_derive_different_keys(self):
        result = dh_key_exchange(2048)
        key1 = dh_derive_key(result.shared_secret_hex, key_length=16)
        key2 = dh_derive_key(result.shared_secret_hex, key_length=32)
        assert len(key1) == 32  # 16 bytes
        assert len(key2) == 64  # 32 bytes
        assert key1 != key2


class TestDHIntegration:
    """Integration test for DHKE + AES."""

    def test_dh_aes_integration(self):
        # Perform DHKE
        dh_result = dh_key_exchange(2048)
        # Derive AES key from shared secret
        aes_key = dh_derive_key(dh_result.shared_secret_hex, key_length=16, hash_algo="SHA256")
        # Use AES key to encrypt
        from cryptolab import aes_encrypt, aes_decrypt
        plaintext = "Secret message from DHKE"
        enc = aes_encrypt(plaintext, key=aes_key, mode="CBC", iv="0" * 16, padding="PKCS7")
        dec = aes_decrypt(enc.output_text, key=aes_key, mode="CBC", iv="0" * 16, padding="PKCS7")
        assert dec.output_text == plaintext


class TestRSAIntegration:
    """Integration tests for RSA."""

    def test_rsa_sign_then_verify(self):
        kp = rsa_generate_keypair(2048)
        message = "Important document"

        sig = rsa_sign(message, kp.private_key_pem)
        verify = rsa_verify(message, sig.output_text, kp.public_key_pem)
        assert verify.output_text == "VALID (Tanda tangan SAH)"

    def test_rsa_encrypt_then_decrypt(self):
        kp = rsa_generate_keypair(2048)
        message = "Secret message"

        enc = rsa_encrypt(message, kp.public_key_pem)
        dec = rsa_decrypt(enc.output_text, kp.private_key_pem)
        assert dec.output_text == message