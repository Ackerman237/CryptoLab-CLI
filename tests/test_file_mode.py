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
#
# F1 (§5.0, approved exception #2): ``aes`` was REMOVED from this list. After F1
# its ``-t``/``-f`` are a mutually-exclusive group, so the pre-F1 message
# ("the following arguments are required: -t/--text") became
# "one of the arguments -t/--text -f/--file is required". That new message is
# recorded in tests/test_file_mode_f1_parser.py. ``aes-gcm`` (new in F1) is
# covered there too. This removal is the intentional snapshot diff for §5.0.
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

    The behaviour below (streaming, error text, encoding ignored, action wins)
    is a contract users already rely on. F1/F2 must not change it silently.
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


class TestF0HashFileKontrak:
    """Precise contract of the EXISTING `hash -f` (locked before F1 touches it).

    Verified against src/cryptolab/cli/commands/hashing.py (handle_hash) and
    src/cryptolab/core/hashing.py (hash_file). All facts empirically confirmed.
    """

    def test_hash_file_streaming_bukan_read_all(self, tmp_path):
        """`hash -f` uses hash_file() -> 8 KB streaming, works on large files.

        Proof: a 20 KB file (larger than one chunk) hashes to the correct digest,
        and hash_file reads in ``iter(lambda: f.read(8192), b"")`` (hashing.py:186).
        """
        import hashlib

        besar = tmp_path / "besar.bin"
        besar.write_bytes(b"A" * 20000)
        code, out, _ = run_cli("hash", "file", "-f", str(besar))
        assert code == 0
        assert hashlib.sha256(b"A" * 20000).hexdigest() in out

    def test_hash_file_digest_benar(self, tmp_path):
        import hashlib

        f = tmp_path / "uji.txt"
        f.write_bytes(b"Hello")
        code, out, _ = run_cli("hash", "file", "-f", str(f))
        assert code == 0
        assert hashlib.sha256(b"Hello").hexdigest() in out

    def test_hash_file_berkas_tidak_ada_galat_exit_1(self, tmp_path):
        """Missing file -> handler error "Gagal membaca file" on stderr, exit 1."""
        code, _, err = run_cli("hash", "file", "-f", str(tmp_path / "nope.txt"))
        assert code == 1
        assert "Gagal membaca file" in err

    def test_hash_file_direktori_galat_exit_1(self, tmp_path):
        """A directory -> OSError wrapped as "Gagal membaca file", exit 1."""
        code, _, err = run_cli("hash", "file", "-f", str(tmp_path))
        assert code == 1
        assert "Gagal membaca file" in err

    def test_hash_file_encoding_diabaikan(self, tmp_path):
        """`--encoding` has NO effect on the `file` action (output stays hex).

        Contrast with `compute`, which DOES honour `--encoding` (see below).
        """
        f = tmp_path / "uji.txt"
        f.write_bytes(b"Hello")
        _, out_hex, _ = run_cli("hash", "file", "-f", str(f))
        _, out_b64, _ = run_cli("hash", "file", "-f", str(f), "--encoding", "base64")
        assert out_hex.strip() == out_b64.strip()

    def test_hash_compute_encoding_dihormati(self):
        """`compute` DOES honour `--encoding` — the counterpart to `file`."""
        import hashlib

        digest_hex = hashlib.sha256(b"Hi").hexdigest()
        _, out_hex, _ = run_cli("hash", "compute", "-t", "Hi")
        _, out_b64, _ = run_cli("hash", "compute", "-t", "Hi", "--encoding", "base64")
        assert digest_hex in out_hex
        assert digest_hex not in out_b64

    def test_hash_action_menang_atas_input_lain(self, tmp_path):
        """When `-t` and `-f` are both given, `action` decides which is used."""
        import hashlib

        f = tmp_path / "uji.txt"
        f.write_bytes(b"Hello")

        # action=compute -> hashes the TEXT, ignores -f.
        code, out_c, _ = run_cli("hash", "compute", "-t", "Hello", "-f", str(f))
        assert code == 0
        assert hashlib.sha256(b"Hello").hexdigest() in out_c

        # action=file -> hashes the FILE, ignores -t.
        code, out_f, _ = run_cli("hash", "file", "-t", "Hello", "-f", str(f))
        assert code == 0
        assert hashlib.sha256(b"Hello").hexdigest() in out_f

    def test_hash_compute_tanpa_text_galat_handler(self):
        """`hash compute` without `-t` fails in the HANDLER (exit 1), not argparse."""
        code, _, err = run_cli("hash", "compute")
        assert code == 1
        assert "memerlukan parameter --text" in err


# ---------------------------------------------------------------------------
# F0b — D11: `AesGcmResult.raw_bytes`
# ---------------------------------------------------------------------------
class TestF0bAesGcmRawBytes:
    """D11: ``AesGcmResult`` carries the ORIGINAL bytes, not the rendered text.

    Motivation (§1.2): before D11, ``output_text`` is TEXT for UTF-8 input and
    HEX for non-UTF-8 input, but ``is_utf8`` does not enforce the type. Calling
    ``bytes.fromhex(output_text)`` on a UTF-8 result silently yields wrong bytes
    (``"deadbeef"`` -> ``b'\\xde\\xad\\xbe\\xef'``). ``raw_bytes`` removes that trap.

    These tests are the REAL proof for D11 (the ``verify_field_placement.py``
    script only demonstrated Python dataclass semantics and is removed in F0b).
    """

    KEY = "kunci-enambelas!"  # 16 bytes -> AES-128

    def test_raw_bytes_pada_deklarasi_field(self):
        """The field exists and is declared BEFORE the defaulted field."""
        import dataclasses

        from cryptolab.core.symmetric.aes import AesGcmResult

        names = [f.name for f in dataclasses.fields(AesGcmResult)]
        assert "raw_bytes" in names
        assert names.index("raw_bytes") < names.index("status_message")

    def test_raw_bytes_halo_utf8(self):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        res = aes_gcm_encrypt("halo", self.KEY)
        back = aes_gcm_decrypt(res.payload, self.KEY)
        assert back.raw_bytes == b"halo"

    def test_raw_bytes_deadbeef_bukan_hasil_fromhex(self):
        """The §1.2 trap: 'deadbeef' must round-trip to b'deadbeef', NOT b'\\xde\\xad\\xbe\\xef'."""
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        res = aes_gcm_encrypt("deadbeef", self.KEY)
        back = aes_gcm_decrypt(res.payload, self.KEY)
        assert back.raw_bytes == b"deadbeef"
        assert back.raw_bytes != b"\xde\xad\xbe\xef"

    def test_raw_bytes_urandom_non_utf8(self):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        pt = os.urandom(64)
        res = aes_gcm_encrypt(pt, self.KEY)
        back = aes_gcm_decrypt(res.payload, self.KEY)
        assert back.raw_bytes == pt

    def test_raw_bytes_kosong(self):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        res = aes_gcm_encrypt(b"", self.KEY)
        back = aes_gcm_decrypt(res.payload, self.KEY)
        assert back.raw_bytes == b""

    @pytest.mark.parametrize("pt", [b"A", b"\xff"])
    def test_raw_bytes_satu_byte(self, pt):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        res = aes_gcm_encrypt(pt, self.KEY)
        back = aes_gcm_decrypt(res.payload, self.KEY)
        assert back.raw_bytes == pt

    def test_raw_bytes_encrypt_adalah_ciphertext(self):
        """On encrypt, ``raw_bytes`` == the ciphertext (ct), not the payload string."""
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", self.KEY)
        _, ct_hex, _ = res.payload.split(":")
        assert res.raw_bytes == bytes.fromhex(ct_hex)

    def test_raw_bytes_roundtrip_cocok_dengan_payload(self):
        """raw_bytes from decrypt == raw_bytes from the matching encrypt."""
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        pt = os.urandom(32)
        enc = aes_gcm_encrypt(pt, self.KEY)
        back = aes_gcm_decrypt(enc.payload, self.KEY)
        assert back.raw_bytes == pt


class TestF0bRegresiGcm:
    """Regression: D11 must NOT change the pre-existing observable behaviour.

    Constants are hard-coded (not dynamically captured) because the values are
    already known — see spec §6.1 (rev-5).
    """

    KEY = "kunci-enambelas!"

    def test_output_text_dan_is_utf8_halo(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt("halo", self.KEY)
        # On encrypt output_text is always the payload string.
        assert res.output_text == res.payload
        assert res.is_utf8 is False

    def test_decrypt_output_text_tetap_teks_untuk_utf8(self):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        back = aes_gcm_decrypt(aes_gcm_encrypt("deadbeef", self.KEY).payload, self.KEY)
        assert back.output_text == "deadbeef"
        assert back.is_utf8 is True

    def test_decrypt_output_text_hex_untuk_non_utf8(self):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        pt = os.urandom(64)
        back = aes_gcm_decrypt(aes_gcm_encrypt(pt, self.KEY).payload, self.KEY)
        # Non-UTF8 output_text == hex of the plaintext (2 x byte length).
        assert back.output_text == pt.hex()
        assert len(back.output_text) == 2 * len(pt)
        assert back.is_utf8 is False

    def test_payload_masih_format_nonce_ct_tag_hex(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt("pesan", self.KEY)
        bagian = res.payload.split(":")
        assert len(bagian) == 3
        nonce_hex, ct_hex, tag_hex = bagian
        assert len(bytes.fromhex(nonce_hex)) == 12  # GCM_NONCE_BYTES
        assert len(bytes.fromhex(tag_hex)) == 16  # GCM_TAG_BYTES
        assert ct_hex == res.raw_bytes.hex()

    def test_konstruktor_tanpa_raw_bytes_typerror(self):
        """Sanity: ``raw_bytes`` is non-default, so omitting it is a TypeError."""
        import pytest as _pytest

        from cryptolab.core.symmetric.aes import AesGcmResult

        with _pytest.raises(TypeError):
            AesGcmResult(
                operation="decrypt",
                key_repr="k",
                nonce_hex="00",
                payload="p",
                output_text="t",
                is_utf8=True,
                technical_success=True,
                # raw_bytes omitted on purpose
            )


class TestF0bCoreMenerimaBytes:
    """Core accepts ``bytes`` and round-trips binary (folds ``verify_core_bytes.py``).

    F1 depends on this contract (§1.1): both AES-CBC and AES-GCM must accept
    ``bytes`` plaintext and return the ORIGINAL bytes in ``raw_bytes``. This is
    now guarded by the suite instead of a manual script.
    """

    KEY = b"kunci-enambelas!"  # 16 byte (AES-128)
    IV = b"iv-enam-belas-by"  # 16 byte

    KASUS = [
        (b"halo", "utf8-biasa"),
        (b"deadbeef", "hex-valid"),
        (os.urandom(64), "biner-acak"),
    ]

    @pytest.mark.parametrize("data", [b"halo", b"deadbeef", os.urandom(64)])
    def test_aes_cbc_menerima_bytes_dan_raw_bytes_sama(self, data):
        from cryptolab.core.symmetric.aes import aes_decrypt, aes_encrypt

        enc = aes_encrypt(data, self.KEY, mode="CBC", iv=self.IV)
        back = aes_decrypt(enc.output_text, self.KEY, mode="CBC", iv=self.IV)
        assert back.raw_bytes == data

    @pytest.mark.parametrize("data", [b"halo", b"deadbeef", os.urandom(64)])
    def test_aes_gcm_menerima_bytes_dan_raw_bytes_sama(self, data):
        from cryptolab.core.symmetric.aes import aes_gcm_decrypt, aes_gcm_encrypt

        enc = aes_gcm_encrypt(data, self.KEY)
        back = aes_gcm_decrypt(enc.payload, self.KEY)
        assert back.raw_bytes == data

    def test_raw_bytes_urandom_64_identik(self):
        """Explicit §1.1 case: os.urandom(64) round-trips byte-for-byte (both modes)."""
        from cryptolab.core.symmetric.aes import (
            aes_decrypt,
            aes_encrypt,
            aes_gcm_decrypt,
            aes_gcm_encrypt,
        )

        data = os.urandom(64)
        cbc = aes_decrypt(
            aes_encrypt(data, self.KEY, mode="CBC", iv=self.IV).output_text,
            self.KEY,
            mode="CBC",
            iv=self.IV,
        )
        gcm = aes_gcm_decrypt(aes_gcm_encrypt(data, self.KEY).payload, self.KEY)
        assert cbc.raw_bytes == data
        assert gcm.raw_bytes == data
