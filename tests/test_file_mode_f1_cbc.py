"""F1c — file-mode wiring for AES-CBC (`aes` command).

Step F1c of docs/Prompt/mode-file-spec.md (F1 split into F1a/F1b/F1c). F1b wired
AES-GCM; this file covers the AES-CBC (`aes`) file path added in F1c.

Key facts (recon F1, spec §3.1):
  * core `aes_encrypt` returns the ciphertext HEX only (``output_text``); the IV
    is NOT part of it, so ``cli/input.py`` assembles ``iv_hex:ct_hex``.
  * decryption reads the IV back from the payload and passes it as raw bytes
    (core encodes string IVs as UTF-8).
"""

import hashlib
import os
import re
import subprocess
import sys

import pytest


CRYPTOLAB_CMD = [sys.executable, "-m", "cryptolab"]
KEY = "kunci-enambelas!"  # 16 bytes
IV = "iv-enam-belas-by"  # 16 bytes


def _child_env():
    env = dict(os.environ)
    env["COLUMNS"] = "80"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_cli(*args, cwd=None):
    result = subprocess.run(
        CRYPTOLAB_CMD + list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_child_env(),
        timeout=60,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


CASES = [
    (b"", "kosong"),
    (b"A", "satu-byte"),
    (b"A" * 15, "lima-belas"),
    (b"A" * 16, "enam-belas"),
    (b"A" * 17, "tujuh-belas"),
    (bytes(range(256)) * 256, "64kb-acak"),
    (b"baris1\r\nbaris2\n", "crlf-lf"),
]


class TestF1cCbcRoundTrip:
    @pytest.mark.parametrize("fmt", ["hex", "base64", "raw"])
    @pytest.mark.parametrize("data,label", CASES, ids=[c[1] for c in CASES])
    def test_cbc_roundtrip_semua_format(self, tmp_path, fmt, data, label):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(data)
        enc = tmp_path / f"enc.{fmt}"
        out = tmp_path / "back.bin"

        code, _, err = run_cli(
            "aes", "encrypt", "-f", str(pt), "-k", KEY, "--iv", IV,
            "--format", fmt, "-o", str(enc),
        )
        assert code == 0, f"encrypt failed: {err!r}"

        code, _, err = run_cli(
            "aes", "decrypt", "-f", str(enc), "-k", KEY,
            "--format", fmt, "-o", str(out), "--force",
        )
        assert code == 0, f"decrypt failed: {err!r}"
        assert hashlib.sha256(out.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()

    def test_cbc_hex_payload_mengandung_iv(self, tmp_path):
        """The hex payload must be ``iv_hex:ct_hex`` (IV assembled by cli/input)."""
        pt = tmp_path / "pt.txt"
        pt.write_bytes(b"halo")
        enc = tmp_path / "ct.hex"
        code, _, err = run_cli(
            "aes", "encrypt", "-f", str(pt), "-k", KEY, "--iv", IV, "-o", str(enc)
        )
        assert code == 0, err
        payload = enc.read_text(encoding="ascii").strip()
        iv_hex, _, ct_hex = payload.partition(":")
        assert iv_hex == IV.encode("utf-8").hex()
        assert len(bytes.fromhex(ct_hex)) % 16 == 0

    def test_cbc_encrypt_tanpa_iv_ditolak(self, tmp_path):
        pt = tmp_path / "pt.txt"
        pt.write_bytes(b"halo")
        code, _, err = run_cli("aes", "encrypt", "-f", str(pt), "-k", KEY, "-o", str(tmp_path / "o"))
        assert code == 1
        assert "IV" in err or "iv" in err

    def test_cbc_out_tanpa_file_ditolak(self, tmp_path):
        code, _, err = run_cli("aes", "encrypt", "-t", "halo", "-k", KEY, "--out", str(tmp_path / "o"))
        assert code == 1
        assert "--out hanya berlaku bersama --file" in err


class TestF1cCbcRantaiTeksFile:
    def test_enkripsi_file_hex_lalu_dekripsi_lewat_text(self, tmp_path):
        """Encrypt --file to hex, then decrypt that ciphertext via --text + same IV.

        The text path is UNCHANGED by F1: it takes the ciphertext hex as ``-t``
        and the IV as ``--iv`` (a 16-char string). Only ``ct_hex`` from the file
        payload is passed to ``-t``.
        """
        pt = tmp_path / "pt.txt"
        pt.write_bytes(b"halo dunia")
        enc = tmp_path / "ct.hex"

        code, _, err = run_cli(
            "aes", "encrypt", "-f", str(pt), "-k", KEY, "--iv", IV, "-o", str(enc)
        )
        assert code == 0, err
        payload = enc.read_text(encoding="ascii").strip()
        _, _, ct_hex = payload.partition(":")

        code, out, err = run_cli("aes", "decrypt", "-t", ct_hex, "-k", KEY, "--iv", IV)
        assert code == 0, err
        assert "halo dunia" in out
