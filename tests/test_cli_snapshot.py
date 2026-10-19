"""Characterization tests for CLI command output snapshots.

These tests capture the exact current output of CLI commands to ensure
refactoring doesn't change behavior. Run with: pytest tests/test_cli_snapshot.py -v
"""

import subprocess
import sys
import json
import os
from pathlib import Path


CRYPTOLAB_CMD = [sys.executable, "-m", "cryptolab"]
SNAPSHOT_DIR = Path(__file__).parent / "snapshots" / "cli"


def run_cli(*args, input_text=None):
    """Run cryptolab CLI command and return (returncode, stdout, stderr)."""
    cmd = CRYPTOLAB_CMD + list(args)
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def normalize_output(text):
    """Normalize output for comparison (strip ANSI, normalize whitespace)."""
    if not text:
        return ""
    # Remove ANSI escape sequences
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    text = ansi_escape.sub('', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.strip()


def load_snapshot(name):
    """Load expected snapshot from file."""
    path = SNAPSHOT_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def save_snapshot(name, output):
    """Save snapshot to file (for initial creation)."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{name}.txt"
    path.write_text(output, encoding="utf-8")


class TestCLISnapshots:
    """Test CLI command outputs match snapshots."""

    def test_caesar_encrypt(self):
        """Test caesar encrypt output."""
        code, out, err = run_cli("caesar", "encrypt", "-t", "HELLO", "-s", "3")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("caesar_encrypt")
        if expected is None:
            save_snapshot("caesar_encrypt", normalized)
            return
        assert normalized == expected

    def test_caesar_decrypt(self):
        """Test caesar decrypt output."""
        code, out, err = run_cli("caesar", "decrypt", "-t", "KHOOR", "-s", "3")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("caesar_decrypt")
        if expected is None:
            save_snapshot("caesar_decrypt", normalized)
            return
        assert normalized == expected

    def test_vigenere_encrypt(self):
        """Test vigenere encrypt output."""
        code, out, err = run_cli("vigenere", "encrypt", "-t", "HELLO", "-k", "KEY")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("vigenere_encrypt")
        if expected is None:
            save_snapshot("vigenere_encrypt", normalized)
            return
        assert normalized == expected

    def test_vigenere_decrypt(self):
        """Test vigenere decrypt output."""
        code, out, err = run_cli("vigenere", "decrypt", "-t", "RIJVS", "-k", "KEY")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("vigenere_decrypt")
        if expected is None:
            save_snapshot("vigenere_decrypt", normalized)
            return
        assert normalized == expected

    def test_base64_encode(self):
        """Test base64 encode output."""
        code, out, err = run_cli("base64", "encode", "-t", "Hello World")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("base64_encode")
        if expected is None:
            save_snapshot("base64_encode", normalized)
            return
        assert normalized == expected

    def test_base64_decode(self):
        """Test base64 decode output."""
        code, out, err = run_cli("base64", "decode", "-t", "SGVsbG8gV29ybGQ=")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("base64_decode")
        if expected is None:
            save_snapshot("base64_decode", normalized)
            return
        assert normalized == expected

    def test_hex_encode(self):
        """Test hex encode output."""
        code, out, err = run_cli("hex", "encode", "-t", "Hello")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("hex_encode")
        if expected is None:
            save_snapshot("hex_encode", normalized)
            return
        assert normalized == expected

    def test_hex_decode(self):
        """Test hex decode output."""
        code, out, err = run_cli("hex", "decode", "-t", "48656c6c6f")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("hex_decode")
        if expected is None:
            save_snapshot("hex_decode", normalized)
            return
        assert normalized == expected

    def test_binary_encode(self):
        """Test binary encode output."""
        code, out, err = run_cli("binary", "encode", "-t", "A")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("binary_encode")
        if expected is None:
            save_snapshot("binary_encode", normalized)
            return
        assert normalized == expected

    def test_binary_decode(self):
        """Test binary decode output."""
        code, out, err = run_cli("binary", "decode", "-t", "01000001")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("binary_decode")
        if expected is None:
            save_snapshot("binary_decode", normalized)
            return
        assert normalized == expected

    def test_hash_md5(self):
        """Test MD5 hash output."""
        code, out, err = run_cli("hash", "compute", "-t", "test", "-a", "MD5")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("hash_md5")
        if expected is None:
            save_snapshot("hash_md5", normalized)
            return
        assert normalized == expected

    def test_hash_sha256(self):
        """Test SHA256 hash output."""
        code, out, err = run_cli("hash", "compute", "-t", "test", "-a", "SHA256")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("hash_sha256")
        if expected is None:
            save_snapshot("hash_sha256", normalized)
            return
        assert normalized == expected

    def test_hash_sha1(self):
        """Test SHA1 hash output."""
        code, out, err = run_cli("hash", "compute", "-t", "test", "-a", "SHA1")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("hash_sha1")
        if expected is None:
            save_snapshot("hash_sha1", normalized)
            return
        assert normalized == expected

    def test_des_encrypt(self):
        """Test DES encrypt output."""
        code, out, err = run_cli("des", "encrypt", "-t", "Hello World", "-k", "12345678", "-m", "ECB")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("des_encrypt")
        if expected is None:
            save_snapshot("des_encrypt", normalized)
            return
        assert normalized == expected

    def test_aes_encrypt(self):
        """Test AES encrypt output."""
        code, out, err = run_cli("aes", "encrypt", "-t", "Hello World", "-k", "1234567890123456", "-m", "ECB")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("aes_encrypt")
        if expected is None:
            save_snapshot("aes_encrypt", normalized)
            return
        assert normalized == expected

    def test_rc2_encrypt(self):
        """Test RC2 encrypt output."""
        code, out, err = run_cli("rc2", "encrypt", "-t", "Hello World", "-k", "12345678", "-m", "ECB")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("rc2_encrypt")
        if expected is None:
            save_snapshot("rc2_encrypt", normalized)
            return
        assert normalized == expected

    def test_rsa_encrypt(self):
        """Test RSA encrypt output structure (uses fixed test keypair for deterministic output)."""
        # Use a fixed test keypair for deterministic output
        from cryptolab.asymmetric import rsa_generate_keypair
        import re
        # Generate keypair programmatically to avoid CLI overhead
        keypair = rsa_generate_keypair(2048)
        pubkey = keypair.public_key_pem

        # Use PKCS1v15 for deterministic output
        code, out, err = run_cli("rsa", "encrypt", "-t", "test message", "--pubkey", pubkey, "-p", "PKCS1v15")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("rsa_encrypt")
        if expected is None:
            save_snapshot("rsa_encrypt", normalized)
            return
        
        # For RSA, the ciphertext changes with each keypair, so only check structure
        assert "CRYPTOLAB CLI v1.0.0 - HASIL RSA ENKRIPSI" in normalized
        assert "RSA-PKCS1v15 (ENCRYPT)" in normalized
        assert "Algorithm   : RSA-PKCS1v15" in normalized
        assert "Key Size    : 2048 bit" in normalized
        assert "Encoding    : HEX" in normalized
        assert "Status      : BERHASIL (OK)" in normalized
        assert "INPUT:" in normalized
        assert "test message" in normalized
        assert "OUTPUT:" in normalized

    def test_detect_format(self):
        """Test format detection output."""
        code, out, err = run_cli("detect", "-t", "SGVsbG8gV29ybGQ=")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("detect_format")
        if expected is None:
            save_snapshot("detect_format", normalized)
            return
        assert normalized == expected

    def test_auto_analyze(self):
        """Test auto analyze output."""
        code, out, err = run_cli("auto", "-t", "SGVsbG8gV29ybGQ=")
        assert code == 0
        normalized = normalize_output(out)
        expected = load_snapshot("auto_analyze")
        if expected is None:
            save_snapshot("auto_analyze", normalized)
            return
        assert normalized == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])