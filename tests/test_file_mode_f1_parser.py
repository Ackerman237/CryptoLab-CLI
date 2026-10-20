"""F1b — parser wiring for the file mode (AES-CBC `aes` + new `aes-gcm`).

Step F1b of docs/Prompt/mode-file-spec.md. This file records the DELIBERATE
parser changes approved in spec §5.0 (exception #2):

  * ``aes`` (AES-CBC): ``-t``/``-f`` now form a ``required=True`` mutually
    exclusive group, so the "no input" message changed from
    "the following arguments are required: -t/--text" to
    "one of the arguments -t/--text -f/--file is required"; the usage line
    changed from ``-t TEXT`` to ``(-t TEXT | -f FILE)``.
  * ``aes-gcm`` is a NEW sub-command (was menu-only before F1).
  * No other sub-command's parser changed (``hash``/``rsa`` untouched).

The three snapshot items required by §5.0 are asserted here for BOTH commands:
  1. the "no input" argparse error text,
  2. the ``--help`` usage line,
  3. the ``-t`` + ``-f`` together error text.
"""

import os
import re
import subprocess
import sys

import pytest


CRYPTOLAB_CMD = [sys.executable, "-m", "cryptolab"]
_ANSI = re.compile(r"\x1b\[[0-9;]*m")

# The two commands F1 is allowed to touch.
PERINTAH_F1 = ["aes", "aes-gcm"]

# A valid key/IV so a run actually reaches the handler.
KEY = "kunci-enambelas!"  # 16 bytes


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


def flat(text):
    """Normalise whitespace/ANSI so wrapped usage lines can be matched."""
    text = _ANSI.sub("", text or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# 1. "no input" -> new mutually-exclusive message (exit 2)
# ---------------------------------------------------------------------------
class TestF1TanpaInput:
    @pytest.mark.parametrize("cmd", PERINTAH_F1)
    def test_pesan_baru_satu_dari_argumen(self, cmd):
        code, out, err = run_cli(cmd, "encrypt")
        assert code == 2
        assert "one of the arguments -t/--text -f/--file is required" in err
        # The OLD message must be gone (that is the whole point of the diff).
        assert "the following arguments are required" not in err
        assert out.strip() == ""

    @pytest.mark.parametrize("cmd", PERINTAH_F1)
    def test_usage_menampilkan_grup_eksklusif(self, cmd):
        _, _, err = run_cli(cmd, "encrypt")
        usage = flat(err)
        assert f"usage: cryptolab {cmd}" in usage
        assert "(-t TEXT | -f FILE)" in usage


# ---------------------------------------------------------------------------
# 2. ``--help`` usage line (exit 0, stdout)
# ---------------------------------------------------------------------------
class TestF1Help:
    @pytest.mark.parametrize("cmd", PERINTAH_F1)
    def test_help_usage_grup_baru(self, cmd):
        code, out, err = run_cli(cmd, "--help")
        assert code == 0
        assert err.strip() == ""
        usage = flat(out)
        assert "(-t TEXT | -f FILE)" in usage


# ---------------------------------------------------------------------------
# 3. ``-t`` + ``-f`` together -> mutually exclusive error (exit 2)
# ---------------------------------------------------------------------------
class TestF1TextDanFileEksklusif:
    @pytest.mark.parametrize("cmd", PERINTAH_F1)
    def test_text_dan_file_bersama_ditolak(self, cmd):
        code, _, err = run_cli(cmd, "encrypt", "-t", "Hi", "-f", "x.txt")
        assert code == 2
        assert "not allowed with argument" in err


# ---------------------------------------------------------------------------
# ``hash`` / ``rsa`` must NOT change (spec §5.0, rev-9)
# ---------------------------------------------------------------------------
class TestF1HashRsaTidakDisentuh:
    def test_hash_masih_terima_text_dan_file_bersama(self):
        """`hash` keeps its pre-F1 behaviour: no mutual exclusion (exit != 2)."""
        code, _, err = run_cli("hash", "file", "-t", "Hi", "-f", "tidak-ada.txt")
        assert "not allowed with argument" not in err
        assert code in (0, 1)

    def test_hash_butuh_action_bukan_text(self):
        code, _, err = run_cli("hash")
        assert code == 2
        assert "the following arguments are required: action" in err

    def test_rsa_butuh_action_bukan_text(self):
        code, _, err = run_cli("rsa")
        assert code == 2
        assert "the following arguments are required: action" in err


# ---------------------------------------------------------------------------
# Runtime validation of --format / --out (spec §3.5)
# ---------------------------------------------------------------------------
class TestF1ValidasiRuntime:
    def test_format_raw_tanpa_out_ditolak(self, tmp_path):
        f = tmp_path / "p.txt"
        f.write_bytes(b"halo")
        code, _, err = run_cli("aes-gcm", "encrypt", "-f", str(f), "-k", KEY, "--format", "raw")
        assert code == 1
        assert "raw butuh --out" in err


# ---------------------------------------------------------------------------
# File-mode round-trip through the CLI (state on disk, sha256 on bytes)
# ---------------------------------------------------------------------------
class TestF1RoundTripCli:
    CASES = [
        (b"", "kosong"),
        (b"A", "satu-byte"),
        (b"A" * 15, "lima-belas"),
        (b"A" * 16, "enam-belas"),
        (b"A" * 17, "tujuh-belas"),
        (bytes(range(256)) * 256, "64kb-acak"),
        (b"baris1\r\nbaris2\n", "crlf-lf"),
    ]

    @pytest.mark.parametrize("fmt", ["hex", "base64", "raw"])
    @pytest.mark.parametrize("data,label", CASES, ids=[c[1] for c in CASES])
    def test_gcm_roundtrip(self, tmp_path, fmt, data, label):
        _assert_roundtrip(tmp_path, "aes-gcm", fmt, data, extra_enc=[])


def _assert_roundtrip(tmp_path, cmd, fmt, data, extra_enc):
    import hashlib

    pt = tmp_path / "pt.bin"
    pt.write_bytes(data)
    enc = tmp_path / f"enc.{fmt}"
    out = tmp_path / "back.bin"

    code, _, err = run_cli(
        cmd, "encrypt", "-f", str(pt), "-k", KEY, "--format", fmt,
        "-o", str(enc), *extra_enc,
    )
    assert code == 0, f"encrypt failed: {err!r}"

    code, _, err = run_cli(
        cmd, "decrypt", "-f", str(enc), "-k", KEY, "--format", fmt,
        "-o", str(out), "--force",
    )
    assert code == 0, f"decrypt failed: {err!r}"
    assert hashlib.sha256(out.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Text <-> file chain (spec §6.1)
# ---------------------------------------------------------------------------
class TestF1RantaiTeksFile:
    def test_enkripsi_file_lalu_dekripsi_lewat_text(self, tmp_path):
        payload_file = tmp_path / "ct.hex"
        pt = tmp_path / "pt.txt"
        pt.write_bytes(b"halo dunia")

        code, _, err = run_cli(
            "aes-gcm", "encrypt", "-f", str(pt), "-k", KEY, "-o", str(payload_file)
        )
        assert code == 0, err
        payload = payload_file.read_text(encoding="ascii").strip()

        code, out, err = run_cli("aes-gcm", "decrypt", "-t", payload, "-k", KEY)
        assert code == 0, err
        assert "halo dunia" in out

    def test_enkripsi_text_lalu_dekripsi_mirip_file(self, tmp_path):
        """Encode via --text, then decrypt the SAME payload through --file."""
        code, out, err = run_cli("aes-gcm", "encrypt", "-t", "halo dunia", "-k", KEY)
        assert code == 0, err
        # Extract the payload (long hex line) from the box.
        payload = ""
        for line in out.splitlines():
            stripped = line.strip()
            if re.fullmatch(r"[0-9a-f]{24}:[0-9a-f]*:[0-9a-f]{32}", stripped):
                payload = stripped
        assert payload, f"payload not found in output: {out!r}"

        ct = tmp_path / "ct.hex"
        ct.write_text(payload, encoding="ascii")
        back = tmp_path / "back.txt"
        code, _, err = run_cli(
            "aes-gcm", "decrypt", "-f", str(ct), "-k", KEY, "-o", str(back), "--force"
        )
        assert code == 0, err
        assert back.read_bytes() == b"halo dunia"
