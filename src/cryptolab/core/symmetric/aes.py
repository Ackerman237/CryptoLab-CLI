"""AES (Advanced Encryption Standard) implementation for modern symmetric crypto lab exercises.

Supports AES-128 (128-bit key / 16 bytes) in CBC and ECB modes with PKCS#7 or None padding.
Designed for educational clarity, CTF challenges, and industry-standard symmetric cryptography.
"""

import re
import secrets
from dataclasses import dataclass, field
from typing import List, Optional, Union

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..exceptions import (
    CryptoLabError,
    InvalidInputError,
    InvalidKeyError,
    DecodingError,
)
from ..analysis.scoring import calculate_text_score, ScoreResult


@dataclass
class AesResult:
    """Result of an AES cryptographic operation."""

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


def aes_encrypt(
    plaintext: Union[str, bytes],
    key: Union[str, bytes],
    mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None,
    padding: str = "PKCS7",
) -> AesResult:
    """Encrypt plaintext using AES (CBC or ECB mode).

    Args:
        plaintext: String or bytes to encrypt.
        key: 16-byte key for AES-128 (also accepts 24 or 32 bytes for AES-192/256).
        mode: Cipher mode, either "CBC" or "ECB" (default: "CBC").
        iv: 16-byte IV required for CBC mode; omitted for ECB.
        padding: Padding scheme: "PKCS7" (default) or "None".

    Returns:
        AesResult containing ciphertext hex, status, and metadata.

    Raises:
        InvalidKeyError: If key length is not 16, 24, or 32 bytes.
        InvalidInputError: If IV is missing/invalid for CBC or mode is unknown.
    """
    key_bytes = _to_bytes(key, "Key AES")
    if len(key_bytes) not in (16, 24, 32):
        raise InvalidKeyError(
            f"Panjang key AES harus 16 byte (AES-128), 24 byte (AES-192), atau 32 byte (AES-256). "
            f"Ditemukan: {len(key_bytes)} byte."
        )

    norm_mode = mode.upper().strip()
    norm_padding = padding.upper().strip()

    if norm_mode not in ("CBC", "ECB"):
        raise InvalidInputError(
            f"Mode AES tidak didukung: '{mode}'. Gunakan 'CBC' atau 'ECB'."
        )
    if norm_padding not in ("PKCS7", "NONE"):
        raise InvalidInputError(
            f"Skema padding tidak didukung: '{padding}'. Gunakan 'PKCS7' atau 'None'."
        )

    pt_bytes = _to_bytes(plaintext, "Plaintext")

    if norm_padding == "PKCS7":
        padded_pt = pad(pt_bytes, 16)
    else:
        if len(pt_bytes) % 16 != 0:
            raise InvalidInputError(
                f"Plaintext tanpa padding harus berupa kelipatan blok 16 byte (128 bit). Ditemukan: {len(pt_bytes)} byte."
            )
        padded_pt = pt_bytes

    iv_bytes: Optional[bytes] = None
    if norm_mode == "CBC":
        if iv is None:
            raise InvalidInputError(
                "Mode AES CBC memerlukan IV (Initialization Vector) sepanjang 16 byte."
            )
        iv_bytes = _to_bytes(iv, "IV AES")
        if len(iv_bytes) != 16:
            raise InvalidInputError(
                f"Panjang IV AES CBC harus tepat 16 byte (128 bit). Ditemukan: {len(iv_bytes)} byte."
            )
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv_bytes)
    else:
        cipher = AES.new(key_bytes, AES.MODE_ECB)

    ct_bytes = cipher.encrypt(padded_pt)
    ct_hex = ct_bytes.hex()

    return AesResult(
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
        status_message=f"Enkripsi AES-{len(key_bytes)*8} ({norm_mode}) berhasil diselesaikan.",
        reasons=["Enkripsi selesai tanpa kesalahan"],
    )


def aes_decrypt(
    ciphertext_hex: str,
    key: Union[str, bytes],
    mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None,
    padding: str = "PKCS7",
) -> AesResult:
    """Decrypt a hexadecimal ciphertext using AES (CBC or ECB mode).

    Args:
        ciphertext_hex: Hexadecimal string representing ciphertext.
        key: 16-byte key for AES-128 (or 24/32 bytes for AES-192/256).
        mode: "CBC" or "ECB" (default: "CBC").
        iv: 16-byte IV (mandatory for CBC, omitted for ECB).
        padding: "PKCS7" (default) or "None".

    Returns:
        AesResult with decoded text, hex fallback if non-UTF8, and readability score.

    Raises:
        InvalidKeyError: If key is not 16, 24, or 32 bytes.
        InvalidInputError: If IV is invalid or ciphertext length is not a multiple of 16 bytes.
        DecodingError: If padding PKCS7 is corrupted.
    """
    clean_hex = _clean_hex(ciphertext_hex)
    ct_bytes = bytes.fromhex(clean_hex)

    if len(ct_bytes) % 16 != 0:
        raise InvalidInputError(
            f"Panjang ciphertext AES harus kelipatan blok 16 byte (32 karakter hex). "
            f"Ditemukan: {len(ct_bytes)} byte ({len(clean_hex)} hex)."
        )

    key_bytes = _to_bytes(key, "Key AES")
    if len(key_bytes) not in (16, 24, 32):
        raise InvalidKeyError(
            f"Panjang key AES harus 16 byte (AES-128), 24 byte (AES-192), atau 32 byte (AES-256). "
            f"Ditemukan: {len(key_bytes)} byte."
        )

    norm_mode = mode.upper().strip()
    norm_padding = padding.upper().strip()

    if norm_mode not in ("CBC", "ECB"):
        raise InvalidInputError(
            f"Mode AES tidak didukung: '{mode}'. Gunakan 'CBC' atau 'ECB'."
        )
    if norm_padding not in ("PKCS7", "NONE"):
        raise InvalidInputError(
            f"Skema padding tidak didukung: '{padding}'. Gunakan 'PKCS7' atau 'None'."
        )

    iv_bytes: Optional[bytes] = None
    if norm_mode == "CBC":
        if iv is None:
            raise InvalidInputError(
                "Mode AES CBC memerlukan IV (Initialization Vector) sepanjang 16 byte."
            )
        iv_bytes = _to_bytes(iv, "IV AES")
        if len(iv_bytes) != 16:
            raise InvalidInputError(
                f"Panjang IV AES CBC harus tepat 16 byte (128 bit). Ditemukan: {len(iv_bytes)} byte."
            )
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv_bytes)
    else:
        cipher = AES.new(key_bytes, AES.MODE_ECB)

    raw_decrypted = cipher.decrypt(ct_bytes)

    if norm_padding == "PKCS7":
        try:
            pt_bytes = unpad(raw_decrypted, 16)
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

    return AesResult(
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


def aes_auto_analyze(
    ciphertext_hex: str,
    key: Optional[Union[str, bytes]] = None,
    iv: Optional[Union[str, bytes]] = None,
) -> List[AesResult]:
    """Test candidate AES configurations (CBC vs ECB, PKCS7 vs None).

    Args:
        ciphertext_hex: Hex string to analyze (multiple of 32 hex chars / 16 bytes).
        key: 16-byte key (AES-128), if available.
        iv: 16-byte IV, if available.

    Returns:
        List of candidate AesResult objects ranked by score.
    """
    clean_hex = _clean_hex(ciphertext_hex)
    candidates: List[AesResult] = []

    if key is None:
        return []

    try:
        key_bytes = _to_bytes(key, "Key AES")
        if len(key_bytes) not in (16, 24, 32):
            return []
    except Exception:
        return []

    # 1. Test ECB Mode (does not need IV)
    for pad_opt in ("PKCS7", "None"):
        try:
            res = aes_decrypt(
                clean_hex, key=key_bytes, mode="ECB", padding=pad_opt
            )
            candidates.append(res)
        except (CryptoLabError, Exception):
            pass

    # 2. Test CBC Mode (only if IV provided)
    if iv is not None:
        try:
            iv_bytes = _to_bytes(iv, "IV AES")
            if len(iv_bytes) == 16:
                for pad_opt in ("PKCS7", "None"):
                    try:
                        res = aes_decrypt(
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

    # Rank candidates by readability score and valid UTF-8
    candidates.sort(
        key=lambda r: (r.readable_success, r.is_utf8, r.score), reverse=True
    )
    return candidates


# ---------- AES-GCM (Tahap 3 upgrade) ----------

GCM_NONCE_BYTES = 12   # 96-bit nonce sesuai rekomendasi NIST SP 800-38D
GCM_TAG_BYTES = 16     # 128-bit authentication tag


@dataclass
class AesGcmResult:
    """Result of an AES-GCM authenticated encryption/decryption."""

    operation: str  # "encrypt" or "decrypt"
    key_repr: str
    nonce_hex: str
    payload: str  # "nonce_hex:ciphertext_hex:tag_hex" (siap disimpan/dikirim)
    output_text: str
    is_utf8: bool
    technical_success: bool
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


def _validate_aes_key(key: Union[str, bytes]) -> bytes:
    key_bytes = _to_bytes(key, "Key AES")
    if len(key_bytes) not in (16, 24, 32):
        raise InvalidKeyError(
            f"Panjang key AES harus 16 byte (AES-128), 24 byte (AES-192), atau 32 byte (AES-256). "
            f"Ditemukan: {len(key_bytes)} byte."
        )
    return key_bytes


def aes_gcm_encrypt(plaintext: Union[str, bytes], key: Union[str, bytes]) -> AesGcmResult:
    """Encrypt using AES-GCM (AEAD) with a fresh random 96-bit nonce.

    Args:
        plaintext: String or bytes to encrypt.
        key: 16, 24, or 32 byte key.

    Returns:
        AesGcmResult with nonce, ciphertext, tag, dan payload gabungan.

    Raises:
        InvalidKeyError: If key length is not 16, 24, or 32 bytes.
    """
    key_bytes = _validate_aes_key(key)
    pt_bytes = _to_bytes(plaintext, "Plaintext")

    nonce = secrets.token_bytes(GCM_NONCE_BYTES)
    cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce, mac_len=GCM_TAG_BYTES)
    ct_bytes = cipher.encrypt(pt_bytes)
    tag = cipher.digest()

    nonce_hex = nonce.hex()
    payload = f"{nonce_hex}:{ct_bytes.hex()}:{tag.hex()}"

    return AesGcmResult(
        operation="encrypt",
        key_repr=key_bytes.decode("utf-8", errors="replace"),
        nonce_hex=nonce_hex,
        payload=payload,
        output_text=payload,
        is_utf8=False,
        technical_success=True,
        status_message=f"Enkripsi AES-GCM-{len(key_bytes) * 8} berhasil (tag 128-bit).",
        reasons=[f"Nonce acak {GCM_NONCE_BYTES} byte dari secrets.token_bytes"],
    )


def aes_gcm_decrypt(payload: str, key: Union[str, bytes]) -> AesGcmResult:
    """Decrypt an AES-GCM payload "nonce_hex:ciphertext_hex:tag_hex".

    Args:
        payload: String gabungan dari ``aes_gcm_encrypt``.
        key: 16, 24, or 32 byte key.

    Returns:
        AesGcmResult berisi plaintext (UTF-8 atau hex bila bukan teks).

    Raises:
        InvalidInputError: If the payload format is invalid.
        InvalidKeyError: If key length is not 16, 24, or 32 bytes.
        DecodingError: If authentication tag verification fails.
    """
    key_bytes = _validate_aes_key(key)

    if not isinstance(payload, str):
        raise InvalidInputError("Payload AES-GCM harus berupa string 'nonce:ciphertext:tag'.")
    parts = payload.strip().split(":")
    if len(parts) != 3:
        raise InvalidInputError(
            "Format payload AES-GCM tidak valid. Harus 'nonce:ciphertext:tag' dalam hex."
        )

    nonce_hex, ct_hex, tag_hex = (p.strip().lower() for p in parts)
    if not (re.fullmatch(r"[0-9a-f]+", nonce_hex or "") and
            re.fullmatch(r"[0-9a-f]*", ct_hex) and
            re.fullmatch(r"[0-9a-f]+", tag_hex or "")):
        raise InvalidInputError(
            "Payload AES-GCM mengandung karakter bukan heksadesimal. Harus 'nonce:ciphertext:tag' dalam hex."
        )

    nonce = bytes.fromhex(nonce_hex)
    if len(nonce) != GCM_NONCE_BYTES:
        raise InvalidInputError(
            f"Nonce AES-GCM harus {GCM_NONCE_BYTES} byte ({GCM_NONCE_BYTES * 2} karakter hex). "
            f"Ditemukan: {len(nonce)} byte."
        )
    tag = bytes.fromhex(tag_hex)
    if len(tag) != GCM_TAG_BYTES:
        raise InvalidInputError(
            f"Tag AES-GCM harus {GCM_TAG_BYTES} byte ({GCM_TAG_BYTES * 2} karakter hex). "
            f"Ditemukan: {len(tag)} byte."
        )
    ct_bytes = bytes.fromhex(ct_hex)

    cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce, mac_len=GCM_TAG_BYTES)
    try:
        pt_bytes = cipher.decrypt_and_verify(ct_bytes, tag)
    except ValueError:
        # Pesan generik: tidak membocorkan detail padding/tag mana yang salah.
        raise DecodingError(
            "Tag autentikasi AES-GCM tidak valid: data rusak, atau kunci/nonce tidak sesuai."
        )

    try:
        output_text = pt_bytes.decode("utf-8")
        is_utf8 = True
        status_msg = "Dekripsi AES-GCM berhasil dan tag autentikasi valid."
    except UnicodeDecodeError:
        output_text = pt_bytes.hex()
        is_utf8 = False
        status_msg = (
            "Dekripsi AES-GCM berhasil (tag valid), namun hasil bukan teks UTF-8 "
            "(ditampilkan dalam format Hex)."
        )

    return AesGcmResult(
        operation="decrypt",
        key_repr=key_bytes.decode("utf-8", errors="replace"),
        nonce_hex=nonce_hex,
        payload=payload.strip(),
        output_text=output_text,
        is_utf8=is_utf8,
        technical_success=True,
        status_message=status_msg,
        reasons=["Tag autentikasi diverifikasi (AEAD)"],
    )
