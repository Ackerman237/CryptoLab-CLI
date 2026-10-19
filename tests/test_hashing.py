"""Unit tests for Hashing module."""

import pytest
from cryptolab import (
    hash_compute,
    hash_file,
    hmac_compute,
    hmac_verify,
    pbkdf2_hash,
    pbkdf2_verify,
    bcrypt_hash,
    bcrypt_verify,
    hash_verify_integrity,
    generate_random_bytes,
    BCRYPT_AVAILABLE,
    SUPPORTED_HASH_ALGOS,
    SUPPORTED_HMAC_ALGOS,
    SUPPORTED_PBKDF2_ALGOS,
    SUPPORTED_PASSWORD_ALGOS,
)
from cryptolab import InvalidInputError, DecodingError
import tempfile
import os
import base64


class TestHashCompute:
    """Test standard hash functions."""

    def test_md5_hash(self):
        res = hash_compute("hello world", "MD5")
        assert res.algorithm == "MD5"
        assert res.technical_success
        assert len(res.output_hash) == 32  # 128-bit = 32 hex chars
        assert res.is_hex

    def test_sha1_hash(self):
        res = hash_compute("hello world", "SHA1")
        assert res.algorithm == "SHA1"
        assert len(res.output_hash) == 40  # 160-bit = 40 hex chars

    def test_sha256_hash(self):
        res = hash_compute("hello world", "SHA256")
        assert res.algorithm == "SHA256"
        assert len(res.output_hash) == 64  # 256-bit = 64 hex chars

    def test_sha512_hash(self):
        res = hash_compute("hello world", "SHA512")
        assert res.algorithm == "SHA512"
        assert len(res.output_hash) == 128  # 512-bit = 128 hex chars

    def test_hash_case_insensitive(self):
        res1 = hash_compute("test", "sha256")
        res2 = hash_compute("test", "SHA256")
        assert res1.output_hash == res2.output_hash

    def test_hash_base64_encoding(self):
        res = hash_compute("test", "SHA256", encoding="base64")
        assert not res.is_hex
        assert len(res.output_hash) > 0

    def test_hash_invalid_algorithm(self):
        with pytest.raises(InvalidInputError):
            hash_compute("test", "INVALID")

    def test_hash_bytes_input(self):
        res = hash_compute(b"binary data", "SHA256")
        assert res.technical_success

    def test_hash_empty_string(self):
        res = hash_compute("", "SHA256")
        assert res.technical_success
        # SHA256 of empty string
        assert res.output_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_hash_deterministic(self):
        res1 = hash_compute("same input", "SHA256")
        res2 = hash_compute("same input", "SHA256")
        assert res1.output_hash == res2.output_hash


class TestHashFile:
    """Test file hashing."""

    def test_hash_file_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"file content for hashing")
            fname = f.name
        try:
            res = hash_file(fname, "SHA256")
            assert res.technical_success
            assert len(res.output_hash) == 64
            assert "[FILE]" in res.input_text
        finally:
            os.unlink(fname)

    def test_hash_file_md5(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"md5 test")
            fname = f.name
        try:
            res = hash_file(fname, "MD5")
            assert res.algorithm == "MD5"
            assert len(res.output_hash) == 32
        finally:
            os.unlink(fname)

    def test_hash_file_not_found(self):
        with pytest.raises(InvalidInputError):
            hash_file("/nonexistent/file.txt", "SHA256")


class TestHMAC:
    """Test HMAC computation and verification."""

    def test_hmac_sha256(self):
        res = hmac_compute("message", "secret_key", "SHA256")
        assert res.algorithm == "HMAC-SHA256"
        assert res.technical_success
        assert len(res.output_hmac) == 64  # SHA256 = 64 hex chars

    def test_hmac_all_algorithms(self):
        for algo in ["MD5", "SHA1", "SHA256", "SHA512"]:
            res = hmac_compute("msg", "key", algo)
            assert res.technical_success

    def test_hmac_base64(self):
        res = hmac_compute("msg", "key", "SHA256", encoding="base64")
        assert not res.is_hex

    def test_hmac_verify_valid(self):
        hmac_val = hmac_compute("message", "secret", "SHA256").output_hmac
        assert hmac_verify("message", "secret", hmac_val, "SHA256") is True

    def test_hmac_verify_invalid(self):
        hmac_val = hmac_compute("message", "secret", "SHA256").output_hmac
        assert hmac_verify("message", "wrong_secret", hmac_val, "SHA256") is False

    def test_hmac_verify_tampered_message(self):
        hmac_val = hmac_compute("original", "secret", "SHA256").output_hmac
        assert hmac_verify("tampered", "secret", hmac_val, "SHA256") is False


class TestPBKDF2:
    """Test PBKDF2 password hashing."""

    def test_pbkdf2_sha256(self):
        res = pbkdf2_hash("password123", iterations=100000)
        assert res.algorithm == "PBKDF2-SHA256"
        assert res.technical_success
        assert res.iterations == 100000
        assert len(res.salt) == 32  # 16 bytes = 32 hex chars
        assert len(res.hash_value) == 64  # 32 bytes = 64 hex chars

    def test_pbkdf2_sha512(self):
        res = pbkdf2_hash("password123", algorithm="SHA512", iterations=100000)
        assert res.algorithm == "PBKDF2-SHA512"
        assert len(res.hash_value) == 64  # dklen=32 default

    def test_pbkdf2_custom_salt(self):
        # Provide salt as hex string
        salt_hex = "637573746f6d73616c74313233343536"  # "customsalt123456" in hex
        res = pbkdf2_hash("pwd", salt=salt_hex, iterations=100000)
        assert res.salt == salt_hex

    def test_pbkdf2_custom_dklen(self):
        res = pbkdf2_hash("pwd", iterations=100000, dklen=16)
        assert len(res.hash_value) == 32  # 16 bytes = 32 hex chars

    def test_pbkdf2_verify_valid(self):
        hash_res = pbkdf2_hash("mypassword", iterations=100000)
        # Salt is stored as hex, pass it directly
        verify = pbkdf2_verify("mypassword", hash_res.salt, hash_res.hash_value, iterations=100000)
        assert verify.match is True

    def test_pbkdf2_verify_invalid(self):
        hash_res = pbkdf2_hash("mypassword", iterations=100000)
        verify = pbkdf2_verify("wrongpassword", hash_res.salt, hash_res.hash_value, iterations=100000)
        assert verify.match is False

    def test_pbkdf2_verify_wrong_iterations(self):
        # Test that using iterations below minimum raises error
        hash_res = pbkdf2_hash("mypassword", iterations=100000)
        try:
            pbkdf2_verify("mypassword", hash_res.salt, hash_res.hash_value, iterations=50000)
            assert False, "Should have raised InvalidInputError for iterations < 100000"
        except InvalidInputError as e:
            assert "Iterations minimal 100,000" in str(e)

    def test_pbkdf2_verify_wrong_algorithm(self):
        hash_res = pbkdf2_hash("mypassword", algorithm="SHA256", iterations=100000)
        verify = pbkdf2_verify("mypassword", hash_res.salt, hash_res.hash_value, algorithm="SHA512", iterations=100000)
        assert verify.match is False

    def test_pbkdf2_invalid_iterations(self):
        with pytest.raises(InvalidInputError):
            pbkdf2_hash("pwd", iterations=100)

    def test_pbkdf2_invalid_salt(self):
        with pytest.raises(InvalidInputError):
            pbkdf2_hash("pwd", salt="short", iterations=100000)

    def test_pbkdf2_base64_encoding(self):
        res = pbkdf2_hash("pwd", iterations=100000, encoding="base64")
        assert not res.hash_value.islower()  # base64 has mixed case


class TestBcrypt:
    """Test bcrypt password hashing (if available)."""

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not installed")
    def test_bcrypt_hash(self):
        res = bcrypt_hash("password123", rounds=4)
        assert res.algorithm == "BCRYPT"
        assert res.technical_success
        assert res.iterations == 4
        assert res.hash_value.startswith("$2b$")

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not installed")
    def test_bcrypt_verify_valid(self):
        res = bcrypt_hash("password123", rounds=4)
        verify = bcrypt_verify("password123", res.hash_value)
        assert verify.match is True

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not installed")
    def test_bcrypt_verify_invalid(self):
        res = bcrypt_hash("password123", rounds=4)
        verify = bcrypt_verify("wrongpassword", res.hash_value)
        assert verify.match is False

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not installed")
    def test_bcrypt_invalid_rounds(self):
        with pytest.raises(InvalidInputError):
            bcrypt_hash("pwd", rounds=3)
        with pytest.raises(InvalidInputError):
            bcrypt_hash("pwd", rounds=32)


class TestIntegrityVerification:
    """Test hash-based integrity verification."""

    def test_verify_integrity_valid(self):
        data = "important data"
        expected = hash_compute(data, "SHA256").output_hash
        res = hash_verify_integrity(data, expected, "SHA256")
        assert res.match is True
        assert "TERVERIFIKASI" in res.status_message

    def test_verify_integrity_invalid(self):
        data = "original"
        expected = hash_compute("tampered", "SHA256").output_hash
        res = hash_verify_integrity(data, expected, "SHA256")
        assert res.match is False
        assert "GAGAL" in res.status_message


class TestRandomBytes:
    """Test secure random generation."""

    def test_generate_hex(self):
        out = generate_random_bytes(32, "hex")
        assert len(out) == 64  # 32 bytes = 64 hex chars
        assert all(c in "0123456789abcdef" for c in out)

    def test_generate_base64(self):
        out = generate_random_bytes(32, "base64")
        assert len(out) > 0
        # base64 length = ceil(n*4/3)
        import base64
        base64.b64decode(out)  # should not raise

    def test_generate_different_each_call(self):
        out1 = generate_random_bytes(32)
        out2 = generate_random_bytes(32)
        assert out1 != out2  # extremely unlikely to be equal

    def test_generate_invalid_length(self):
        with pytest.raises(InvalidInputError):
            generate_random_bytes(0)
        with pytest.raises(InvalidInputError):
            generate_random_bytes(2000)


class TestConstants:
    """Test exported constants."""

    def test_supported_hash_algos(self):
        assert "MD5" in SUPPORTED_HASH_ALGOS
        assert "SHA256" in SUPPORTED_HASH_ALGOS
        assert "SHA512" in SUPPORTED_HASH_ALGOS

    def test_supported_hmac_algos(self):
        assert "HMAC-SHA256" in SUPPORTED_HMAC_ALGOS
        assert "HMAC-SHA512" in SUPPORTED_HMAC_ALGOS

    def test_supported_pbkdf2_algos(self):
        assert "PBKDF2-SHA256" in SUPPORTED_PBKDF2_ALGOS

    def test_supported_password_algos(self):
        assert "PBKDF2-SHA256" in SUPPORTED_PASSWORD_ALGOS
        if BCRYPT_AVAILABLE:
            assert "BCRYPT" in SUPPORTED_PASSWORD_ALGOS