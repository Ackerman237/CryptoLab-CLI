"""F0 — Characterization tests for the "Mode File" refactor.

Step F0 of docs/Prompt/mode-file-spec.md: record the CURRENT behaviour of the
CLI parser on the code that has NOT been changed yet, so that F1's intentional
parser changes produce a reviewable diff.

Scope of F0 (spec §6.3, rev-7):
  (a) sub-command without ``-t``          -> argparse "required" error
  (b) ``--help``                           -> usage block
  (c) ``-t`` given alone (valid)           -> command runs

The ``-t`` + ``-f`` case is NOT recorded here: the ``-f/--file`` option does
not exist yet, so today it yields ``unrecognized arguments``. That case is
added in F1 together with the snapshot updates (spec §5.0, §6.3 butir 3).

Robustness (spec §6.3 butir 2): argparse message text varies across Python
versions (e.g. ``options:`` vs ``optional arguments:``). We therefore:
  * pin ``COLUMNS=80`` in the child env so usage wrapping is deterministic;
  * assert on STABLE SUBSTRINGS for error messages, not the whole block;
  * normalise whitespace / line endings / ANSI before comparing usage.

Run with: pytest tests/test_file_mode.py -v
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


CRYPTOLAB_CMD = [sys.executable, "-m", "cryptolab"]

# Sub-commands whose ``-t/--text`` is REQUIRED (17 of 24).
# Verified by introspecting create_parser(): the ``-t`` action has required=True.
# NOT in this list: ``hash`` and ``rsa`` (their ``-t`` is optional; ``action``
# is the required argument) — see TestF0TextOpsional below.
SUBPERINTAH_WAJIB_TEXT = [
    "caesar",
    "brute",
    "vigenere",
    "playfair",
    "hill",
    "affine",
    "railfence",
    "base64",
    "hex",
    "binary",
    "analyze",
    "detect",
    "auto",
    "des",
    "aes",
    "rc2",
    "hmac",
]

# (sub-command tokens) used for case (a): missing ``-t`` -> argparse error.
# Kept explicit (not generated) so a parser change shows up as a diff here too.
KASUS_A_TANPA_TEXT = [
    ("caesar", "encrypt"),
    ("brute",),
    ("vigenere", "encrypt"),
    ("playfair", "encrypt"),
    ("hill", "encrypt"),
    ("affine", "encrypt"),
    ("railfence", "encrypt"),
    ("base64", "encode"),
    ("hex", "encode"),
    ("binary", "encode"),
    ("analyze",),
    ("detect",),
    ("auto",),
    ("des", "encrypt"),
    ("aes", "encrypt"),
    ("rc2", "encrypt"),
    ("hmac",),
]

# (sub-command tokens, extra args) used for case (c): valid run with ``-t``.
KASUS_C_DENGAN_TEXT = [
    (("caesar", "encrypt"), ["-t", "HELLO", "-s", "3"]),
    (("brute",), ["-t", "KHOOR"]),
    (("vigenere", "encrypt"), ["-t", "HELLO", "-k", "KEY"]),
    (("playfair", "encrypt"), ["-t", "HELLO", "-k", "MONARCHY"]),
    (("hill", "encrypt"), ["-t", "HELLO", "-k", "3 3 2 5"]),
    (("affine", "encrypt"), ["-t", "HELLO", "-a", "5", "-b", "8"]),
    (("railfence", "encrypt"), ["-t", "HELLO", "-r", "3"]),
    (("base64", "encode"), ["-t", "Hello World"]),
    (("hex", "encode"), ["-t", "Hi"]),
    (("binary", "encode"), ["-t", "Hi"]),
    (("analyze",), ["-t", "HELLO WORLD"]),
    (("detect",), ["-t", "KHOOR"]),
    (("auto",), ["-t", "KHOOR"]),
    (("hash", "compute"), ["-t", "Hello"]),
]

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def _child_env():
    """Environment with a pinned COLUMNS so argparse usage wrapping is stable."""
    env = dict(os.environ)
    env["COLUMNS"] = "80"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_cli(*args):
    """Run ``cryptolab <args>`` and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        CRYPTOLAB_CMD + list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_child_env(),
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


def normalize_teks(text):
    """Normalize output for comparison (strip ANSI, unify line endings/whitespace)."""
    if not text:
        return ""
    text = _ANSI_ESCAPE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of spaces/tabs (argparse wraps usage with alignment spaces).
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


# ---------------------------------------------------------------------------
# (a) Sub-command without ``-t`` -> argparse "required" error (exit 2)
# ---------------------------------------------------------------------------
class TestF0TanpaText:
    """Case (a): each sub-command rejects a missing ``-t/--text``."""

    @pytest.mark.parametrize("tokens", KASUS_A_TANPA_TEXT, ids=lambda t: "_".join(t))
    def test_tanpa_text_galat_required(self, tokens):
        code, out, err = run_cli(*tokens)
        assert code == 2, f"expected exit 2, got {code}; stderr={err!r}"
        # Stable substrings only (not the full block).
        assert "the following arguments are required" in err
        assert "-t/--text" in err
        # argparse prints the error to stderr, not stdout.
        assert out.strip() == ""

    def test_usage_menyebut_text_wajib(self):
        """The usage line advertises ``-t TEXT`` as mandatory (no brackets)."""
        _, _, err = run_cli("caesar", "encrypt")
        usage_line = err.splitlines()[0]
        assert usage_line.startswith("usage: cryptolab caesar")
        assert "-t TEXT" in usage_line
        assert "[-t TEXT]" not in usage_line

    def test_prefix_error_menyebut_prog(self):
        """Error prefix names the offending sub-command."""
        _, _, err = run_cli("aes", "encrypt")
        assert "cryptolab aes: error:" in err


# ---------------------------------------------------------------------------
# (b) ``--help`` -> usage block (exit 0, stdout)
# ---------------------------------------------------------------------------
class TestF0Help:
    """Case (b): ``--help`` shows a usage block with a stable shape."""

    @pytest.mark.parametrize("nama", SUBPERINTAH_WAJIB_TEXT)
    def test_help_exit_nol_dan_usage(self, nama):
        code, out, err = run_cli(nama, "--help")
        assert code == 0
        assert err.strip() == ""
        normalized = normalize_teks(out)
        assert normalized.startswith(f"usage: cryptolab {nama}")
        # At COLUMNS=80 argparse may wrap, so whitespace is collapsed first.
        assert "-t TEXT" in normalized.replace("\n", " ")

    def test_help_caesar_menampilkan_opsinya(self):
        """A concrete help block: usage + positional choices + options."""
        code, out, _ = run_cli("caesar", "--help")
        assert code == 0
        normalized = normalize_teks(out)
        # Collapse line wraps before matching: argparse wraps usage at COLUMNS=80.
        flat = normalized.replace("\n", " ")
        flat = re.sub(r" +", " ", flat)
        assert (
            "usage: cryptolab caesar [-h] -t TEXT [-s SHIFT] [-b] "
            "{encrypt,decrypt,brute-force,brute}" in flat
        )
        # Stable option strings must survive the F1 refactor.
        assert "--text" in normalized
        assert "--shift" in normalized
        assert "--best" in normalized

    def test_help_heading_stabil(self):
        """Heading may be ``options:`` or ``optional arguments:`` across versions."""
        _, out, _ = run_cli("caesar", "--help")
        normalized = normalize_teks(out)
        assert "options:" in normalized or "optional arguments:" in normalized


# ---------------------------------------------------------------------------
# (c) ``-t`` given alone -> the command runs (exit 0)
# ---------------------------------------------------------------------------
class TestF0DenganText:
    """Case (c): valid runs keep working; behaviour must not change in F1."""

    @pytest.mark.parametrize(
        "tokens,extra", KASUS_C_DENGAN_TEXT, ids=lambda v: "_".join(v) if isinstance(v, tuple) else str(v)
    )
    def test_dengan_text_berhasil(self, tokens, extra):
        code, out, err = run_cli(*tokens, *extra)
        assert code == 0, f"exit {code}; stderr={err!r}"
        assert out.strip() != ""

    def test_caesar_text_hasil_benar(self):
        """Round-trip: the plaintext/ciphertext really is processed."""
        code, out, _ = run_cli("caesar", "encrypt", "-t", "HELLO", "-s", "3")
        assert code == 0
        assert "KHOOR" in out

        code, out, _ = run_cli("caesar", "decrypt", "-t", "KHOOR", "-s", "3")
        assert code == 0
        assert "HELLO" in out

    def test_base64_text_hasil_benar(self):
        code, out, _ = run_cli("base64", "encode", "-t", "Hello World")
        assert code == 0
        assert "SGVsbG8gV29ybGQ=" in out

    def test_text_panjang_spasi_tetap_utuh(self):
        """Regression guard for the PR #3 multi-line/space handling on ``--text``."""
        code, out, _ = run_cli("base64", "encode", "-t", "Hello World")
        assert code == 0
        assert "SGVsbG8gV29ybGQ=" in out

    def test_galat_argparse_tanpa_text_tetap_exit_dua(self):
        """Explicit contract: missing ``-t`` is a usage error (exit 2), not a crash."""
        code, _, err = run_cli("caesar", "encrypt")
        assert code == 2
        assert "Traceback" not in err


# ---------------------------------------------------------------------------
# Extra: ``hash``/``rsa`` have OPTIONAL ``-t`` (characterization finding)
# ---------------------------------------------------------------------------
class TestF0TextOpsional:
    """``hash`` and ``rsa`` do NOT require ``-t`` — they require ``action``.

    This is a real characterization finding (F0): the naive assumption "every
    text command requires ``-t``" is false. It matters for F1 because the
    mutual-exclusion group must be added per-command after checking each
    command's actual required arguments.
    """

    def test_hash_butuh_action_bukan_text(self):
        code, _, err = run_cli("hash")
        assert code == 2
        assert "the following arguments are required: action" in err
        assert "-t/--text" not in err

    def test_hash_usage_text_dan_file_opsional(self):
        """`hash` usage advertises BOTH ``-t`` and ``-f`` as optional.

        F0 finding: ``-f/--file`` ALREADY EXISTS on `hash` (parser.py:359), as
        does ``--encoding``. This differs from the spec's assumption that ``-f``
        is introduced in F1 — see the F0 report.
        """
        _, _, err = run_cli("hash")
        usage_line = err.splitlines()[0]
        assert "[-t TEXT]" in usage_line
        assert "[-f FILE]" in usage_line

    def test_rsa_butuh_action_bukan_text(self):
        code, _, err = run_cli("rsa")
        assert code == 2
        assert "the following arguments are required: action" in err
        assert "-t/--text" not in err

    def test_rsa_encrypt_tanpa_text_galat_dari_handler(self):
        """``rsa encrypt`` without ``-t`` fails in the HANDLER (exit 1), not argparse.

        Documented so F1 does not accidentally assume exit-2/argparse behaviour.
        """
        code, out, err = run_cli("rsa", "encrypt")
        assert code == 1
        assert "Encrypt memerlukan --text" in (out + err)


# ---------------------------------------------------------------------------
# Extra: the exact pre-F1 state of ``-f/--file`` (F0 finding)
# ---------------------------------------------------------------------------
class TestF0FileState:
    """`-f/--file` already exists on `hash` only; it does not exist elsewhere.

    F0 finding (corrects the spec's assumption): `hash` has ``-f/--file``
    (parser.py:359) and ``--encoding`` already. It is NOT mutually exclusive
    with ``-t`` yet, and other sub-commands have no ``-f`` at all. F1 must
    account for this existing, partially-wired option instead of assuming a
    clean slate.
    """

    def test_hash_file_sudah_ada(self):
        code, out, err = run_cli("hash", "file", "-f", "tidak-ada.txt")
        # The option is accepted by the parser (no "unrecognized arguments"),
        # then fails in the handler because the file does not exist.
        assert "unrecognized arguments" not in err
        assert code in (0, 1)

    def test_hash_text_dan_file_belum_saling_eksklusif(self):
        """No mutual-exclusion group on `hash` yet (would be exit 2)."""
        code, _, err = run_cli("hash", "compute", "-t", "Hi", "-f", "x.txt")
        assert "not allowed with argument" not in err

    @pytest.mark.parametrize("nama", ["caesar", "aes", "base64"])
    def test_perintah_lain_belum_ada_file(self, nama):
        code, _, err = run_cli(nama, "--help")
        normalized = normalize_teks(err)
        assert code == 0
        assert "--file" not in normalized
        assert "-f FILE" not in normalized

    def test_caesar_file_unrecognized_sebelum_f1(self):
        code, _, err = run_cli("caesar", "encrypt", "-t", "HI", "-f", "x.txt")
        assert code == 2
        assert "unrecognized arguments" in err
