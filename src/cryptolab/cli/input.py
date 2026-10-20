"""File-mode I/O, format conversion, and size limits.

Step F1a of docs/Prompt/mode-file-spec.md: the pure helpers used by the
``--file`` / ``--out`` / ``--format`` options. NO parser wiring here — this
module is self-contained and unit-tested on its own.

Design notes (spec §5.1-§5.5):
  * All helpers raise ``InvalidInputError`` for user-facing problems, so the
    CLI handlers can map them to a friendly box + exit 1 (no traceback).
  * ``LIMIT_PLAINTEXT_BYTES`` is a module constant so tests can monkeypatch it
    to a small value and stay fast.
  * Decryption never uses ``result.output_text``; core results expose the
    original bytes via ``raw_bytes`` (D11).
"""

import base64
import os
import tempfile
from typing import Optional

from cryptolab.core.exceptions import InvalidInputError

# --- Limits (spec §5.3) -----------------------------------------------------

# Max PLAINTEXT size for encryption / max decrypted size. Monkeypatchable.
LIMIT_PLAINTEXT_BYTES = 10 * 1024 * 1024  # 10 MiB

# Overhead of the binary payload layouts (bytes).
GCM_OVERHEAD = 12 + 16  # nonce (12) + tag (16)
CBC_OVERHEAD = 16  # IV (16)

VALID_FORMATS = ("hex", "base64", "raw")

# BOM signatures (spec §3.2 decode_ciphertext).
_UTF8_BOM = b"\xef\xbb\xbf"
_UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")

_MIB = 1024 * 1024


def _fmt_mb(n_bytes: int) -> str:
    """Format a byte count in MB with one decimal (for error messages)."""
    return f"{n_bytes / _MIB:.1f}"


# --- Reading input (spec §5.1) ---------------------------------------------


def read_file_bytes(path: str, limit: int) -> bytes:
    """Read a file fully, rejecting anything longer than ``limit`` bytes.

    Reads ``limit + 1`` bytes so a file that grew after any earlier check is
    still rejected (no TOCTOU reliance on ``stat()``).
    """
    if not os.path.exists(path):
        raise InvalidInputError(f"Berkas tidak ditemukan: {path}")
    if not os.path.isfile(path):
        raise InvalidInputError(f"{path} bukan berkas biasa.")

    try:
        with open(path, "rb") as f:
            data = f.read(limit + 1)
    except PermissionError:
        raise InvalidInputError(f"Tidak bisa membaca berkas: izin ditolak ({path})")
    except OSError as e:
        raise InvalidInputError(f"Tidak bisa membaca berkas: {e}")

    if len(data) > limit:
        raise InvalidInputError(
            f"Berkas {_fmt_mb(len(data))} MB melebihi batas {_fmt_mb(limit)} MB. "
            f"Gunakan berkas lebih kecil."
        )
    return data


# --- Size limits for decryption (spec §5.3) --------------------------------


def max_binary_len(algo: str, limit: int = LIMIT_PLAINTEXT_BYTES) -> int:
    """Max binary payload length for a decrypted plaintext of ``limit`` bytes."""
    overhead = GCM_OVERHEAD if algo.upper() == "GCM" else CBC_OVERHEAD
    return limit + overhead


def max_encoded_len(fmt: str, algo: str, limit: int = LIMIT_PLAINTEXT_BYTES) -> int:
    """Max file-input length (in bytes) that can still decode to a valid ciphertext."""
    binary = max_binary_len(algo, limit)
    fmt = fmt.lower()
    if fmt == "raw":
        return binary
    if fmt == "hex":
        # 2 chars per byte + up to 2 separator chars (":") for GCM/CBC.
        return binary * 2 + 8
    if fmt == "base64":
        # 4 chars per 3 bytes, rounded up, plus a small slack.
        return 4 * ((binary + 2) // 3) + 8
    raise InvalidInputError(f"Format tidak dikenal: {fmt}")


def read_decrypt_bytes(path: str, fmt: str, algo: str,
                       limit: int = LIMIT_PLAINTEXT_BYTES) -> bytes:
    """Read a ciphertext file for decryption with a whitespace-tolerant cap."""
    max_kode = max_encoded_len(fmt, algo, limit)
    cap = max_kode + max_kode // 32 + 1024
    data = read_file_bytes(path, cap)
    # Whitespace is stripped inside decode_ciphertext; enforce the strict cap there.
    return data


# --- Format conversion: encrypt (spec §5.2) ---------------------------------


def encode_ciphertext(payload_str: str, fmt: str, algo: str) -> bytes:
    """Convert a core payload string to the chosen output format.

    ``payload_str``:
      * GCM -> "nonce_hex:ct_hex:tag_hex"
      * CBC -> "ct_hex" (caller must prepend IV for hex/base64/raw)
    """
    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        raise InvalidInputError(f"Format tidak dikenal: {fmt}")

    if algo.upper() == "GCM":
        parts = payload_str.strip().split(":")
        if len(parts) != 3:
            raise InvalidInputError("Payload AES-GCM tidak valid (harus nonce:ciphertext:tag).")
        nonce_hex, ct_hex, tag_hex = parts
        binary = bytes.fromhex(nonce_hex) + bytes.fromhex(ct_hex) + bytes.fromhex(tag_hex)
    else:
        parts = payload_str.strip().split(":")
        if len(parts) != 2:
            raise InvalidInputError(
                "Payload AES-CBC tidak valid (harus iv_hex:ciphertext_hex)."
            )
        iv_hex, ct_hex = parts
        binary = bytes.fromhex(iv_hex) + bytes.fromhex(ct_hex)

    if fmt == "hex":
        return (payload_str.strip()).encode("ascii")
    if fmt == "base64":
        return base64.b64encode(binary)
    return binary  # raw


def build_cbc_payload(iv_hex: str, ct_hex: str) -> str:
    """Assemble the CBC hex payload ``iv_hex:ciphertext_hex`` (core returns ct only)."""
    return f"{iv_hex}:{ct_hex}"


# --- Format conversion: decrypt (spec §5.2, §5.5) ---------------------------


def _strip_all_whitespace(s: str) -> str:
    return "".join(ch for ch in s if not ch.isspace())


def decode_ciphertext(data: bytes, fmt: str, algo: str) -> dict:
    """Decode ciphertext bytes back into core-ready fields.

    Returns a dict:
      * GCM -> {"nonce_hex", "ct_hex", "tag_hex"}
      * CBC -> {"iv_hex", "ct_hex"}

    Raises ``InvalidInputError`` with a friendly message on any problem.
    """
    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        raise InvalidInputError(f"Format tidak dikenal: {fmt}")

    # --- BOM handling (spec §3.2) ---
    if data.startswith(_UTF16_BOMS) or (len(data) >= 2 and data[:2] in _UTF16_BOMS):
        raise InvalidInputError(
            "Berkas tampak UTF-16 (mis. hasil '>' di Windows PowerShell). "
            "Buat ulang berkas dengan --out, atau simpan sebagai UTF-8."
        )
    if data.startswith(_UTF8_BOM):
        data = data[len(_UTF8_BOM):]

    if fmt == "raw":
        return _decode_raw(data, algo)

    if fmt == "hex":
        text = _strip_all_whitespace(data.decode("utf-8", errors="replace"))
        # Split on ':' FIRST: separators make the total length odd for CBC.
        return _parse_hex_payload(text, algo)

    # base64
    text = _strip_all_whitespace(data.decode("utf-8", errors="replace"))
    try:
        binary = base64.b64decode(text, validate=False)
    except Exception:
        raise InvalidInputError("Ciphertext base64 tidak valid.")
    return _parse_binary_payload(binary, algo)


def _check_hex(s: str, nama: str) -> bytes:
    if len(s) % 2 != 0:
        raise InvalidInputError(f"{nama} hex memiliki jumlah karakter ganjil (data terpotong?).")
    try:
        return bytes.fromhex(s)
    except ValueError:
        raise InvalidInputError(f"{nama} bukan heksadesimal yang valid.")


def _parse_hex_payload(text: str, algo: str) -> dict:
    if algo.upper() == "GCM":
        parts = text.split(":")
        if len(parts) != 3:
            raise InvalidInputError(
                "Payload hex AES-GCM tidak valid (harus nonce:ciphertext:tag)."
            )
        nonce_hex, ct_hex, tag_hex = parts
        nonce = _check_hex(nonce_hex, "Nonce")
        _check_hex(ct_hex, "Ciphertext")
        tag = _check_hex(tag_hex, "Tag")
        if len(nonce) != 12:
            raise InvalidInputError("Nonce AES-GCM harus 12 byte (24 karakter hex).")
        if len(tag) != 16:
            raise InvalidInputError("Tag AES-GCM harus 16 byte (32 karakter hex).")
        return {"nonce_hex": nonce_hex, "ct_hex": ct_hex, "tag_hex": tag_hex}

    parts = text.split(":")
    if len(parts) != 2:
        raise InvalidInputError(
            "Payload hex AES-CBC tidak valid (harus iv:ciphertext)."
        )
    iv_hex, ct_hex = parts
    iv = _check_hex(iv_hex, "IV")
    ct = _check_hex(ct_hex, "Ciphertext")
    if len(iv) != 16:
        raise InvalidInputError("IV AES-CBC harus 16 byte (32 karakter hex).")
    if len(ct) == 0 or len(ct) % 16 != 0:
        raise InvalidInputError(
            "Ciphertext AES-CBC harus kelipatan 16 byte (data rusak atau terpotong)."
        )
    return {"iv_hex": iv_hex, "ct_hex": ct_hex}


def _decode_raw(data: bytes, algo: str) -> dict:
    if algo.upper() == "GCM":
        if len(data) < GCM_OVERHEAD + 1:
            raise InvalidInputError("Berkas raw terpotong (lebih pendek dari nonce+tag).")
        nonce = data[:12]
        tag = data[-16:]
        ct = data[12:-16]
        return {"nonce_hex": nonce.hex(), "ct_hex": ct.hex(), "tag_hex": tag.hex()}

    if len(data) < CBC_OVERHEAD + 16 or (len(data) - CBC_OVERHEAD) % 16 != 0:
        raise InvalidInputError("Berkas raw AES-CBC terpotong atau tidak selaras blok.")
    iv = data[:16]
    ct = data[16:]
    return {"iv_hex": iv.hex(), "ct_hex": ct.hex()}


def _parse_binary_payload(data: bytes, algo: str) -> dict:
    if algo.upper() == "GCM":
        if len(data) < GCM_OVERHEAD + 1:
            raise InvalidInputError("Ciphertext GCM terlalu pendek (data terpotong?).")
        nonce = data[:12]
        tag = data[-16:]
        ct = data[12:-16]
        return {"nonce_hex": nonce.hex(), "ct_hex": ct.hex(), "tag_hex": tag.hex()}

    if len(data) < CBC_OVERHEAD + 16 or (len(data) - CBC_OVERHEAD) % 16 != 0:
        raise InvalidInputError("Ciphertext CBC tidak selaras blok (data rusak?).")
    iv = data[:16]
    ct = data[16:]
    return {"iv_hex": iv.hex(), "ct_hex": ct.hex()}


# --- Writing output (spec §5.4) ---------------------------------------------


def _resolve(path: str) -> str:
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def write_output(path: str, data: bytes, force: bool = False,
                 source_path: Optional[str] = None) -> None:
    """Write ``data`` to ``path`` safely.

    * Refuses ``path == source_path`` (resolved, case-insensitive).
    * Without ``force``: create-exclusive (``xb``); existing file -> error.
    * With ``force``: atomic replace via a unique temp file in the same dir.
    * Never leaves a partial file behind on failure.
    """
    if source_path is not None and _resolve(path) == _resolve(source_path):
        raise InvalidInputError("--out tidak boleh sama dengan --file.")

    parent = os.path.dirname(os.path.abspath(path))
    if os.path.isdir(path):
        raise InvalidInputError(f"{path} adalah direktori, bukan berkas keluaran.")
    if not os.path.isdir(parent):
        raise InvalidInputError(f"Direktori tujuan tidak ada: {parent}")

    if not force:
        try:
            with open(path, "xb") as f:
                f.write(data)
        except FileExistsError:
            raise InvalidInputError(
                f"Berkas {path} sudah ada. Pakai --force untuk menimpa."
            )
        except PermissionError:
            raise InvalidInputError(f"Tidak bisa menulis berkas: izin ditolak ({path})")
        except OSError as e:
            raise InvalidInputError(f"Tidak bisa menulis berkas: {e}")
        return

    # force: write to a unique temp file in the same directory, then os.replace.
    fd = None
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=parent, prefix=".cryptolab-", suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            fd = None  # fdopen took ownership
            f.write(data)
        os.replace(tmp_path, path)
        tmp_path = None
    except PermissionError:
        raise InvalidInputError(
            f"Tidak bisa menimpa berkas (mungkin sedang dibuka proses lain): {path}"
        )
    except OSError as e:
        raise InvalidInputError(f"Gagal menulis berkas keluaran: {e}")
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
