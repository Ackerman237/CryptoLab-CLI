"""RC2 (also known as ARC2) implementation for legacy lab challenges.

WARNING: RC2 is an obsolete 64-bit block cipher. Use modern authenticated
encryption for new systems; this module exists for compatibility and learning.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Union

from Crypto.Cipher import ARC2
from Crypto.Util.Padding import pad, unpad

from cryptolab.analysis.scoring import calculate_text_score
from cryptolab.exceptions import DecodingError, InvalidInputError, InvalidKeyError


@dataclass
class Rc2Result:
    """Result of an RC2 cryptographic operation."""

    mode: str
    padding: str
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
    if data is None:
        raise InvalidInputError(f"{name} tidak boleh None.")
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    raise InvalidInputError(f"{name} harus berupa string atau bytes.")


def _clean_hex(hex_str: str) -> str:
    if hex_str is None or not isinstance(hex_str, str):
        raise InvalidInputError("Ciphertext harus berupa string heksadesimal.")
    cleaned = hex_str.strip()
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    cleaned = re.sub(r"[\s:\-]+", "", cleaned)
    if not cleaned:
        raise InvalidInputError("Ciphertext heksadesimal tidak boleh kosong.")
    if not re.fullmatch(r"[0-9a-fA-F]+", cleaned):
        raise DecodingError("Ciphertext mengandung karakter bukan heksadesimal.")
    if len(cleaned) % 2:
        raise DecodingError("Panjang ciphertext heksadesimal harus genap.")
    return cleaned


def _validate_options(
    key: Union[str, bytes], mode: str, iv: Optional[Union[str, bytes]], padding_name: str
):
    key_bytes = _to_bytes(key, "Key RC2")
    if not 5 <= len(key_bytes) <= 16:
        raise InvalidKeyError(
            f"Panjang key RC2 harus 5 sampai 16 byte. Ditemukan: {len(key_bytes)} byte."
        )
    norm_mode = mode.upper().strip()
    norm_padding = padding_name.upper().strip()
    if norm_mode not in ("CBC", "ECB"):
        raise InvalidInputError(f"Mode RC2 tidak didukung: '{mode}'. Gunakan 'CBC' atau 'ECB'.")
    if norm_padding not in ("PKCS7", "NONE"):
        raise InvalidInputError("Skema padding tidak didukung. Gunakan 'PKCS7' atau 'None'.")

    iv_bytes = None
    if norm_mode == "CBC":
        if iv is None:
            raise InvalidInputError("Mode RC2 CBC memerlukan IV sepanjang 8 byte.")
        iv_bytes = _to_bytes(iv, "IV RC2")
        if len(iv_bytes) != 8:
            raise InvalidInputError(f"Panjang IV RC2 CBC harus tepat 8 byte. Ditemukan: {len(iv_bytes)} byte.")
    return key_bytes, norm_mode, norm_padding, iv_bytes


def _cipher(key_bytes: bytes, mode: str, iv_bytes: Optional[bytes], effective_keylen: int):
    if mode == "CBC":
        return ARC2.new(key_bytes, ARC2.MODE_CBC, iv=iv_bytes, effective_keylen=effective_keylen)
    return ARC2.new(key_bytes, ARC2.MODE_ECB, effective_keylen=effective_keylen)


def rc2_encrypt(
    plaintext: Union[str, bytes], key: Union[str, bytes], mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None, padding: str = "PKCS7", effective_keylen: int = 128,
) -> Rc2Result:
    if not 40 <= effective_keylen <= 1024:
        raise InvalidInputError("Effective key length RC2 harus antara 40 dan 1024 bit.")
    key_bytes, norm_mode, norm_padding, iv_bytes = _validate_options(key, mode, iv, padding)
    pt_bytes = _to_bytes(plaintext, "Plaintext")
    if norm_padding == "PKCS7":
        padded = pad(pt_bytes, 8)
    elif len(pt_bytes) % 8 == 0:
        padded = pt_bytes
    else:
        raise InvalidInputError("Plaintext tanpa padding harus berupa kelipatan blok 8 byte.")
    ct_bytes = _cipher(key_bytes, norm_mode, iv_bytes, effective_keylen).encrypt(padded)
    return Rc2Result(norm_mode, norm_padding, key_bytes.decode("utf-8", errors="replace"),
                     iv_bytes.decode("utf-8", errors="replace") if iv_bytes else None,
                     pt_bytes.hex(), ct_bytes.hex(), ct_bytes, True, True, True,
                     100.0, "Enkripsi RC2 berhasil diselesaikan.", ["Enkripsi selesai tanpa kesalahan"])


def rc2_decrypt(
    ciphertext_hex: str, key: Union[str, bytes], mode: str = "CBC",
    iv: Optional[Union[str, bytes]] = None, padding: str = "PKCS7", effective_keylen: int = 128,
) -> Rc2Result:
    if not 40 <= effective_keylen <= 1024:
        raise InvalidInputError("Effective key length RC2 harus antara 40 dan 1024 bit.")
    clean_hex = _clean_hex(ciphertext_hex)
    ct_bytes = bytes.fromhex(clean_hex)
    if len(ct_bytes) % 8:
        raise InvalidInputError("Panjang ciphertext RC2 harus kelipatan blok 8 byte.")
    key_bytes, norm_mode, norm_padding, iv_bytes = _validate_options(key, mode, iv, padding)
    raw = _cipher(key_bytes, norm_mode, iv_bytes, effective_keylen).decrypt(ct_bytes)
    if norm_padding == "PKCS7":
        try:
            pt_bytes = unpad(raw, 8)
        except ValueError as err:
            raise DecodingError(f"Padding PKCS#7 tidak valid ({err}). Kemungkinan key/IV salah.")
    else:
        pt_bytes = raw
    try:
        output_text = pt_bytes.decode("utf-8")
        score_info = calculate_text_score(output_text)
        score = score_info.score
        readable = score >= 50.0
        reasons = score_info.reasons
        status = f"Dekripsi RC2 berhasil (Skor: {score:.1f}/100)"
        is_utf8 = True
    except UnicodeDecodeError:
        output_text, score, readable, reasons, status, is_utf8 = (
            pt_bytes.hex(), 10.0, False, ["Byte hasil dekripsi bukan UTF-8 valid"],
            "Dekripsi RC2 berhasil secara teknis, hasil ditampilkan dalam Hex.", False,
        )
    return Rc2Result(norm_mode, norm_padding, key_bytes.decode("utf-8", errors="replace"),
                     iv_bytes.decode("utf-8", errors="replace") if iv_bytes else None,
                     clean_hex, output_text, pt_bytes, is_utf8, True, readable,
                     score, status, reasons)


def rc2_auto_analyze(ciphertext_hex: str, key: Optional[Union[str, bytes]] = None,
                     iv: Optional[Union[str, bytes]] = None, effective_keylen: int = 128) -> List[Rc2Result]:
    if key is None:
        return []
    candidates = []
    for mode, mode_iv in (("ECB", None), ("CBC", iv)):
        if mode == "CBC" and iv is None:
            continue
        for padding_name in ("PKCS7", "None"):
            try:
                candidates.append(rc2_decrypt(ciphertext_hex, key, mode, mode_iv, padding_name, effective_keylen))
            except Exception:
                pass
    candidates.sort(key=lambda result: (result.readable_success, result.is_utf8, result.score), reverse=True)
    return candidates