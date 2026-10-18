"""DES (Data Encryption Standard) implementation for educational and lab challenges.

WARNING:
    DES is an obsolete 56-bit block cipher provided strictly for learning,
    practical laboratory assignments, and CTF challenges. Do NOT use DES
    for modern security systems.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Union

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

from cryptolab.exceptions import (
    CryptoLabError,
    InvalidInputError,
    InvalidKeyError,
    DecodingError,
)
from cryptolab.analysis.scoring import calculate_text_score, ScoreResult


@dataclass
class DesResult:
    """Result of a DES cryptographic operation."""

    mode: str  # "CBC" or "ECB"
    padding: str  # "PKCS7" or "None"
    key_repr: str
    iv_repr: Optional[str]
    input_hex: str
    output_text: str
    raw_bytes: bytes
    is_utf8: bool
    technical_success: bool
    readable_success: bool
    score: float = 0.0
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


def _to_bytes(data: Union[str, bytes], name: str) -> bytes:
    """Safely convert a string or bytes input to bytes."""
    if data is None:
        raise InvalidInputError(f"{name} tidak boleh None.")
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    raise InvalidInputError(f"{name} harus berupa string atau bytes.")


def _clean_hex(hex_str: str) -> str:
    """Clean and validate hexadecimal string."""
    if hex_str is None or not isinstance(hex_str, str):
        raise InvalidInputError("Ciphertext harus berupa string heksadesimal.")

    cleaned = hex_str.strip()
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    cleaned = re.sub(r"[\s:\-]+", "", cleaned)

    if len(cleaned) == 0:
        raise InvalidInputError("Ciphertext heksadesimal tidak boleh kosong.")

    if not re.fullmatch(r"[0-9a-fA-F]+", cleaned):
        invalid_chars = set(re.findall(r"[^0-9a-fA-F]", cleaned))
        raise DecodingError(
            f"Ciphertext mengandung karakter bukan heksadesimal: {', '.join(sorted(invalid_chars))}"
        )

    if len(cleaned) % 2 != 0:
        raise DecodingError(
            f"Panjang ciphertext heksadesimal ganjil ({len(cleaned)} karakter). Harus berupa pasangan byte genap."
        )

    return cleaned


def des_encrypt(
    plaintext: Union[str, bytes],
    key: Union[str, bytes],
    mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None,
    padding: str = "PKCS7",
) -> DesResult:
    """Encrypt plaintext using DES (CBC or ECB mode).

    Args:
        plaintext: String or bytes to encrypt.
        key: 8-byte key (ASCII string or bytes).
        mode: Cipher mode, either "CBC" or "ECB" (default: "CBC").
        iv: 8-byte IV required for CBC mode; not used for ECB.
        padding: Padding scheme: "PKCS7" (default) or "None".

    Returns:
        DesResult containing ciphertext hex, status, and metadata.

    Raises:
        InvalidKeyError: If key is not exactly 8 bytes.
        InvalidInputError: If IV is missing/invalid for CBC or mode is unknown.
    """
    key_bytes = _to_bytes(key, "Key DES")
    if len(key_bytes) != 8:
        raise InvalidKeyError(
            f"Panjang key DES harus tepat 8 byte (64 bit). Ditemukan: {len(key_bytes)} byte."
        )

    norm_mode = mode.upper().strip()
    norm_padding = padding.upper().strip()

    if norm_mode not in ("CBC", "ECB"):
        raise InvalidInputError(
            f"Mode DES tidak didukung: '{mode}'. Gunakan 'CBC' atau 'ECB'."
        )
    if norm_padding not in ("PKCS7", "NONE"):
        raise InvalidInputError(
            f"Skema padding tidak didukung: '{padding}'. Gunakan 'PKCS7' atau 'None'."
        )

    pt_bytes = _to_bytes(plaintext, "Plaintext")

    if norm_padding == "PKCS7":
        padded_pt = pad(pt_bytes, 8)
    else:
        if len(pt_bytes) % 8 != 0:
            raise InvalidInputError(
                f"Plaintext tanpa padding harus berupa kelipatan 8 byte. Ditemukan: {len(pt_bytes)} byte."
            )
        padded_pt = pt_bytes

    iv_bytes: Optional[bytes] = None
    if norm_mode == "CBC":
        if iv is None:
            raise InvalidInputError(
                "Mode DES CBC memerlukan IV (Initialization Vector) sepanjang 8 byte."
            )
        iv_bytes = _to_bytes(iv, "IV DES")
        if len(iv_bytes) != 8:
            raise InvalidInputError(
                f"Panjang IV DES CBC harus tepat 8 byte. Ditemukan: {len(iv_bytes)} byte."
            )
        cipher = DES.new(key_bytes, DES.MODE_CBC, iv=iv_bytes)
    else:
        cipher = DES.new(key_bytes, DES.MODE_ECB)

    ct_bytes = cipher.encrypt(padded_pt)
    ct_hex = ct_bytes.hex()

    return DesResult(
        mode=norm_mode,
        padding=norm_padding,
        key_repr=key_bytes.decode("utf-8", errors="replace"),
        iv_repr=iv_bytes.decode("utf-8", errors="replace") if iv_bytes else None,
        input_hex=pt_bytes.hex(),
        output_text=ct_hex,
        raw_bytes=ct_bytes,
        is_utf8=True,
        technical_success=True,
        readable_success=True,
        score=100.0,
        status_message="Enkripsi DES berhasil diselesaikan.",
        reasons=["Enkripsi selesai tanpa kesalahan"],
    )


def des_decrypt(
    ciphertext_hex: str,
    key: Union[str, bytes],
    mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None,
    padding: str = "PKCS7",
) -> DesResult:
    """Decrypt a hexadecimal ciphertext using DES (CBC or ECB mode).

    Args:
        ciphertext_hex: Hexadecimal string representing ciphertext.
        key: 8-byte key.
        mode: "CBC" or "ECB" (default: "CBC").
        iv: 8-byte IV (mandatory for CBC, omitted for ECB).
        padding: "PKCS7" (default) or "None".

    Returns:
        DesResult with decoded text, hex fallback if non-UTF8, and readability score.

    Raises:
        InvalidKeyError: If key is not 8 bytes.
        InvalidInputError: If IV is invalid or ciphertext length is not a multiple of 8 bytes.
        DecodingError: If padding PKCS7 is corrupted.
    """
    clean_hex = _clean_hex(ciphertext_hex)
    ct_bytes = bytes.fromhex(clean_hex)

    if len(ct_bytes) % 8 != 0:
        raise InvalidInputError(
            f"Panjang ciphertext DES harus kelipatan 8 byte (16 karakter hex). Ditemukan: {len(ct_bytes)} byte ({len(clean_hex)} hex)."
        )

    key_bytes = _to_bytes(key, "Key DES")
    if len(key_bytes) != 8:
        raise InvalidKeyError(
            f"Panjang key DES harus tepat 8 byte (64 bit). Ditemukan: {len(key_bytes)} byte."
        )

    norm_mode = mode.upper().strip()
    norm_padding = padding.upper().strip()

    if norm_mode not in ("CBC", "ECB"):
        raise InvalidInputError(
            f"Mode DES tidak didukung: '{mode}'. Gunakan 'CBC' atau 'ECB'."
        )
    if norm_padding not in ("PKCS7", "NONE"):
        raise InvalidInputError(
            f"Skema padding tidak didukung: '{padding}'. Gunakan 'PKCS7' atau 'None'."
        )

    iv_bytes: Optional[bytes] = None
    if norm_mode == "CBC":
        if iv is None:
            raise InvalidInputError(
                "Mode DES CBC memerlukan IV (Initialization Vector) sepanjang 8 byte."
            )
        iv_bytes = _to_bytes(iv, "IV DES")
        if len(iv_bytes) != 8:
            raise InvalidInputError(
                f"Panjang IV DES CBC harus tepat 8 byte. Ditemukan: {len(iv_bytes)} byte."
            )
        cipher = DES.new(key_bytes, DES.MODE_CBC, iv=iv_bytes)
    else:
        cipher = DES.new(key_bytes, DES.MODE_ECB)

    raw_decrypted = cipher.decrypt(ct_bytes)

    if norm_padding == "PKCS7":
        try:
            pt_bytes = unpad(raw_decrypted, 8)
        except ValueError as err:
            raise DecodingError(
                f"Padding PKCS#7 tidak valid ({err}). Kemungkinan key/IV salah atau data menggunakan mode/padding 'None'."
            )
    else:
        pt_bytes = raw_decrypted

    # Attempt UTF-8 decoding
    try:
        output_text = pt_bytes.decode("utf-8")
        is_utf8 = True
        score_info = calculate_text_score(output_text)
        readable_success = score_info.score >= 50.0
        status_msg = (
            f"Dekripsi berhasil (Teks UTF-8 terbaca, Skor: {score_info.score:.1f}/100)"
            if readable_success
            else f"Dekripsi berhasil secara teknis, namun skor keterbacaan rendah ({score_info.score:.1f}/100)"
        )
        reasons = score_info.reasons
        score = score_info.score
    except UnicodeDecodeError:
        # Preserve bytes as Hex if not valid UTF-8
        output_text = pt_bytes.hex()
        is_utf8 = False
        readable_success = False
        score = 10.0
        status_msg = "Dekripsi berhasil secara teknis, namun hasil bukan teks UTF-8 valid (ditampilkan dalam format Hex)."
        reasons = ["Byte hasil dekripsi di luar rentang UTF-8 yang valid"]

    return DesResult(
        mode=norm_mode,
        padding=norm_padding,
        key_repr=key_bytes.decode("utf-8", errors="replace"),
        iv_repr=iv_bytes.decode("utf-8", errors="replace") if iv_bytes else None,
        input_hex=clean_hex,
        output_text=output_text,
        raw_bytes=pt_bytes,
        is_utf8=is_utf8,
        technical_success=True,
        readable_success=readable_success,
        score=score,
        status_message=status_msg,
        reasons=reasons,
    )


def des_auto_analyze(
    ciphertext_hex: str,
    key: Optional[Union[str, bytes]] = None,
    iv: Optional[Union[str, bytes]] = None,
) -> List[DesResult]:
    """Test candidate DES configurations (CBC vs ECB, PKCS7 vs None).

    Args:
        ciphertext_hex: Hex string to analyze.
        key: 8-byte key, if available.
        iv: 8-byte IV, if available.

    Returns:
        List of candidate DesResult objects ranked by score.
    """
    clean_hex = _clean_hex(ciphertext_hex)
    candidates: List[DesResult] = []

    if key is None:
        return []

    try:
        key_bytes = _to_bytes(key, "Key DES")
        if len(key_bytes) != 8:
            return []
    except Exception:
        return []

    # 1. Test ECB Mode (does not need IV)
    for pad_opt in ("PKCS7", "None"):
        try:
            res = des_decrypt(
                clean_hex, key=key_bytes, mode="ECB", padding=pad_opt
            )
            candidates.append(res)
        except (CryptoLabError, Exception):
            pass

    # 2. Test CBC Mode (only if IV provided)
    if iv is not None:
        try:
            iv_bytes = _to_bytes(iv, "IV DES")
            if len(iv_bytes) == 8:
                for pad_opt in ("PKCS7", "None"):
                    try:
                        res = des_decrypt(
                            clean_hex,
                            key=key_bytes,
                            mode="CBC",
                            iv=iv_bytes,
                            padding=pad_opt,
                        )
                        candidates.append(res)
                    except (CryptoLabError, Exception):
                        pass
        except Exception:
            pass

    # Rank candidates by score and whether it's valid UTF-8
    candidates.sort(
        key=lambda r: (r.readable_success, r.is_utf8, r.score), reverse=True
    )
    return candidates
