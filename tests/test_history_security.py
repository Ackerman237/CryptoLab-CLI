"""Characterization tests for history log format and secrets filtering.

These tests ensure history logging works correctly and sensitive data
(key, IV, password, etc.) is properly redacted.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from cryptolab import (
    log_history,
    read_history,
    clear_history,
    get_history_file,
    _sanitize_params,
    SENSITIVE_PARAM_KEYS,
    SAFE_PARAM_KEYS,
)


class TestHistorySanitization:
    """Test parameter sanitization for history logs."""

    def test_sanitize_params_redacts_sensitive_keys(self):
        """Sensitive keys should be redacted by default."""
        params = {
            "key": "secret123",
            "iv": "abcdefgh",
            "password": "mypassword",
            "mode": "CBC",
            "padding": "PKCS7",
        }
        sanitized = _sanitize_params(params)
        assert sanitized["key"] == "[REDACTED]"
        assert sanitized["iv"] == "[REDACTED]"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["mode"] == "CBC"
        assert sanitized["padding"] == "PKCS7"

    def test_sanitize_params_keeps_safe_keys(self):
        """Safe keys should not be redacted."""
        params = {
            "mode": "CBC",
            "padding": "PKCS7",
            "algorithm": "AES",
            "iterations": 100000,
            "rounds": 12,
        }
        sanitized = _sanitize_params(params)
        assert sanitized == params

    def test_sanitize_params_include_secrets_true(self):
        """With include_secrets=True, sensitive keys should be kept."""
        params = {
            "key": "secret123",
            "iv": "abcdefgh",
            "mode": "CBC",
        }
        sanitized = _sanitize_params(params, include_secrets=True)
        assert sanitized["key"] == "secret123"
        assert sanitized["iv"] == "abcdefgh"
        assert sanitized["mode"] == "CBC"

    def test_sanitize_params_case_insensitive(self):
        """Key matching should be case-insensitive."""
        params = {
            "KEY": "secret123",
            "IV": "abcdefgh",
            "Password": "mypassword",
            "MODE": "CBC",
        }
        sanitized = _sanitize_params(params)
        assert sanitized["KEY"] == "[REDACTED]"
        assert sanitized["IV"] == "[REDACTED]"
        assert sanitized["Password"] == "[REDACTED]"
        assert sanitized["MODE"] == "CBC"

    def test_sanitize_params_unknown_keys_kept(self):
        """Unknown keys not in sensitive list should be kept."""
        params = {
            "custom_param": "value",
            "another_field": "data",
            "mode": "CBC",
        }
        sanitized = _sanitize_params(params)
        assert sanitized["custom_param"] == "value"
        assert sanitized["another_field"] == "data"
        assert sanitized["mode"] == "CBC"

    def test_sanitize_params_none_input(self):
        """None input should return empty dict."""
        assert _sanitize_params(None) == {}

    def test_sensitive_keys_comprehensive(self):
        """Check all expected sensitive keys are defined."""
        expected_sensitive = {
            "key", "iv", "password", "secret", "salt", "private_key",
            "privatekey", "shared_secret", "sharedsecret", "passphrase",
            "pass", "pwd", "decrypted", "plaintext", "ciphertext",
            "signature", "hmac",
        }
        assert expected_sensitive.issubset(SENSITIVE_PARAM_KEYS)

    def test_safe_keys_comprehensive(self):
        """Check all expected safe keys are defined."""
        expected_safe = {
            "mode", "padding", "algorithm", "encoding", "iterations",
            "rounds", "dklen", "effective_keylen", "key_length",
            "shift", "rails", "matrix_size", "score", "status",
            "match", "file", "filepath", "operation", "encoding",
            "algo", "method", "category",
        }
        assert expected_safe.issubset(SAFE_PARAM_KEYS)


class TestHistoryLogging:
    """Test history logging functionality."""

    @pytest.fixture(autouse=True)
    def setup_history(self):
        """Use temp directory for history."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        yield

        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_history_basic(self):
        """Basic history logging works."""
        result = log_history("Test Operation", "input", "output", {"mode": "CBC"})
        assert result is True

        records = read_history()
        assert len(records) == 1
        record = records[0]
        assert record["operation"] == "Test Operation"
        assert record["input"] == "input"
        assert record["output"] == "output"
        assert record["params"]["mode"] == "CBC"

    def test_log_history_redacts_secrets(self):
        """Secrets should be redacted in history by default."""
        log_history("DES Encrypt", "plaintext", "ciphertext",
                    {"key": "secret123", "iv": "abcdefgh", "mode": "CBC"})

        records = read_history()
        record = records[0]
        assert record["params"]["key"] == "[REDACTED]"
        assert record["params"]["iv"] == "[REDACTED]"
        assert record["params"]["mode"] == "CBC"

    def test_log_history_include_secrets_true(self):
        """With include_secrets=True, secrets should be logged."""
        log_history("AES Encrypt", "plaintext", "ciphertext",
                    {"key": "aeskey123456789", "mode": "ECB"},
                    include_secrets=True)

        records = read_history()
        record = records[0]
        assert record["params"]["key"] == "aeskey123456789"
        assert record["params"]["mode"] == "ECB"

    def test_log_history_disabled(self):
        """History logging can be disabled."""
        result = log_history("Test", "input", "output", enabled=False)
        assert result is False

        records = read_history()
        assert len(records) == 0

    def test_log_history_truncates_long_input(self):
        """Long input/output should be truncated."""
        long_input = "A" * 1000
        log_history("Test", long_input, "output")

        records = read_history()
        record = records[0]
        assert len(record["input"]) <= 500
        assert record["input"].endswith("...")

    def test_log_history_truncates_long_output(self):
        """Long output should be truncated."""
        long_output = "B" * 1000
        log_history("Test", "input", long_output)

        records = read_history()
        record = records[0]
        assert len(record["output"]) <= 500
        assert record["output"].endswith("...")

    def test_log_history_preserves_timestamp(self):
        """Records should have timestamp."""
        log_history("Test", "input", "output")
        records = read_history()
        record = records[0]
        assert "timestamp" in record
        # Should be valid ISO format
        import datetime
        datetime.datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))

    def test_read_history_limit(self):
        """Read history respects limit parameter."""
        for i in range(25):
            log_history(f"Test {i}", f"input{i}", f"output{i}")

        records = read_history(limit=10)
        assert len(records) == 10
        # Returns last 10 in chronological order (Test 15-24)
        assert records[0]["operation"] == "Test 15"
        assert records[9]["operation"] == "Test 24"

    def test_clear_history(self):
        """Clear history removes all records."""
        log_history("Test 1", "in", "out")
        log_history("Test 2", "in", "out")

        clear_history()
        records = read_history()
        assert len(records) == 0

    def test_clear_history_nonexistent(self):
        """Clear history on nonexistent file should succeed."""
        # Don't create history first
        result = clear_history()
        assert result is True


class TestHistorySecurityIntegration:
    """Integration tests for history security with real operations."""

    @pytest.fixture(autouse=True)
    def setup_history(self):
        """Use temp directory for history."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        yield

        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_des_encrypt_history_no_key(self):
        """DES encrypt history should not contain key."""
        from cryptolab import des_encrypt
        from cryptolab import log_history, read_history, clear_history

        clear_history()
        plaintext = "Hello World"
        key = "secret12"  # 8 bytes
        iv = "abcdefgh"

        res = des_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7")

        # Simulate what the handler does
        log_history("DES Encrypt", plaintext, res.output_text,
                    {"mode": "CBC", "padding": "PKCS7", "key": key, "iv": iv})

        records = read_history()
        record = records[0]
        assert record["params"]["key"] == "[REDACTED]"
        assert record["params"]["iv"] == "[REDACTED]"
        assert record["params"]["mode"] == "CBC"

    def test_aes_encrypt_history_no_key(self):
        """AES encrypt history should not contain key."""
        from cryptolab import aes_encrypt
        from cryptolab import log_history, read_history, clear_history

        clear_history()
        plaintext = "Hello World"
        key = "1234567890123456"
        iv = "abcdefghijklmnop"

        res = aes_encrypt(plaintext, key=key, mode="CBC", iv=iv, padding="PKCS7")

        log_history("AES Encrypt", plaintext, res.output_text,
                    {"mode": "CBC", "padding": "PKCS7", "key": key, "iv": iv})

        records = read_history()
        record = records[0]
        assert record["params"]["key"] == "[REDACTED]"
        assert record["params"]["iv"] == "[REDACTED]"
        assert record["params"]["mode"] == "CBC"

    def test_rsa_encrypt_history_no_private_key(self):
        """RSA encrypt history should not contain private key."""
        from cryptolab import rsa_generate_keypair, rsa_encrypt
        from cryptolab import log_history, read_history, clear_history

        clear_history()
        keypair = rsa_generate_keypair(2048)
        plaintext = "Secret message"

        res = rsa_encrypt(plaintext, keypair.public_key_pem, padding="OAEP")

        # Simulate logging (handler should not log private key)
        log_history("RSA Encrypt", plaintext, res.output_text,
                    {"algorithm": "RSA-OAEP-SHA256", "public_key": keypair.public_key_pem[:50]})

        records = read_history()
        record = records[0]
        assert "private" not in str(record).lower()
        assert "PRIVATE KEY" not in record["params"].get("public_key", "")

    def test_pbkdf2_history_no_password(self):
        """PBKDF2 history should not contain password."""
        from cryptolab import pbkdf2_hash
        from cryptolab import log_history, read_history, clear_history

        clear_history()
        password = "my_secure_password"
        res = pbkdf2_hash(password, iterations=100000)

        log_history("PBKDF2 Hash", "********", res.hash_value,
                    {"algorithm": "PBKDF2-SHA256", "iterations": 100000, "password": password})

        records = read_history()
        record = records[0]
        assert record["params"]["password"] == "[REDACTED]"
        assert record["params"]["iterations"] == 100000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])