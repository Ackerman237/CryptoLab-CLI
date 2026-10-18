"""Format detection for Binary, Hexadecimal, and Base64 with UTF-8 validation."""

import re
from dataclasses import dataclass, field
from typing import List, Optional
from cryptolab.exceptions import InvalidInputError, DecodingError
from cryptolab.encoding.base64_codec import base64_decode
from cryptolab.encoding.hex_codec import hex_decode
from cryptolab.encoding.binary_codec import binary_decode
from cryptolab.analysis.scoring import calculate_text_score, ScoreResult


@dataclass
class DetectionResult:
    """Represents format detection analysis for a specific encoding format."""

    format_name: str
    is_match: bool
    confidence: str  # "High", "Medium", "Low", "None"
    details: str
    preview_decoded: Optional[str] = None
    is_valid_utf8: bool = False
    score: float = 0.0
    score_reasons: List[str] = field(default_factory=list)


def is_printable_text(text: str) -> bool:
    """Check if string mostly consists of printable ASCII / UTF-8 characters."""
    if not text:
        return False
    printable_count = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
    return (printable_count / len(text)) >= 0.85


def detect_format(text: str) -> List[DetectionResult]:
    """Analyze input text and assess likelihood of Binary, Hexadecimal, or Base64 format.

    Note:
        Heuristic detection is an educated estimate and is not guaranteed to be
        100% correct. Syntactic validity does not prove the format was intended.
        Always verify candidates in context.

    Args:
        text: String to analyze.

    Returns:
        List of DetectionResult for each supported format.

    Raises:
        InvalidInputError: If text is empty or not a string.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")

    cleaned = text.strip()
    if len(cleaned) == 0:
        raise InvalidInputError("Input teks tidak boleh kosong.")

    results: List[DetectionResult] = []

    # 1. Binary Detection (8-bit per byte)
    bin_clean = re.sub(r"\s+", "", cleaned)
    if re.fullmatch(r"[01]+", bin_clean) and len(bin_clean) >= 8 and len(bin_clean) % 8 == 0:
        try:
            decoded = binary_decode(cleaned)
            score_res = calculate_text_score(decoded)
            printable = is_printable_text(decoded)
            confidence = "High" if printable else "Medium"
            results.append(
                DetectionResult(
                    format_name="Binary",
                    is_match=True,
                    confidence=confidence,
                    details=f"Sintaks biner valid ({len(bin_clean)} bit = {len(bin_clean)//8} byte), teks UTF-8 valid.",
                    preview_decoded=decoded if printable else "<non-printable bytes>",
                    is_valid_utf8=True,
                    score=score_res.score,
                    score_reasons=score_res.reasons,
                )
            )
        except DecodingError as err:
            results.append(
                DetectionResult(
                    format_name="Binary",
                    is_match=True,
                    confidence="Low",
                    details=f"Sintaks biner valid ({len(bin_clean)} bit), tetapi bukan representasi UTF-8 yang valid ({err}).",
                    preview_decoded=None,
                    is_valid_utf8=False,
                    score=0.0,
                    score_reasons=["Gagal didekode sebagai teks UTF-8"],
                )
            )
    else:
        results.append(
            DetectionResult(
                format_name="Binary",
                is_match=False,
                confidence="None",
                details="Karakter mengandung non-[0,1] atau panjang bukan kelipatan 8 bit.",
            )
        )

    # 2. Hexadecimal Detection
    hex_candidate = cleaned
    if hex_candidate.startswith(("0x", "0X")):
        hex_candidate = hex_candidate[2:]
    hex_clean = re.sub(r"[\s:\-]+", "", hex_candidate)

    if (
        re.fullmatch(r"[0-9a-fA-F]+", hex_clean)
        and len(hex_clean) >= 2
        and len(hex_clean) % 2 == 0
    ):
        try:
            decoded = hex_decode(cleaned)
            score_res = calculate_text_score(decoded)
            printable = is_printable_text(decoded)
            # Short hex strings (<= 4 chars) like 'dead', 'beef' could easily be plain words
            if len(hex_clean) <= 4 and hex_clean.isalpha():
                confidence = "Low"
            else:
                confidence = "High" if printable else "Medium"

            results.append(
                DetectionResult(
                    format_name="Hexadecimal",
                    is_match=True,
                    confidence=confidence,
                    details=f"Sintaks heksadesimal valid ({len(hex_clean)//2} byte), teks UTF-8 valid.",
                    preview_decoded=decoded if printable else "<non-printable bytes>",
                    is_valid_utf8=True,
                    score=score_res.score,
                    score_reasons=score_res.reasons,
                )
            )
        except DecodingError as err:
            results.append(
                DetectionResult(
                    format_name="Hexadecimal",
                    is_match=True,
                    confidence="Low",
                    details=f"Byte heksadesimal valid ({len(hex_clean)//2} byte), tetapi bukan teks UTF-8 valid ({err}).",
                    preview_decoded=None,
                    is_valid_utf8=False,
                    score=0.0,
                    score_reasons=["Gagal didekode sebagai teks UTF-8"],
                )
            )
    else:
        results.append(
            DetectionResult(
                format_name="Hexadecimal",
                is_match=False,
                confidence="None",
                details="Mengandung karakter di luar [0-9a-fA-F] atau panjang karakter ganjil.",
            )
        )

    # 3. Base64 Detection
    b64_candidate = cleaned
    # Base64 standard character set: A-Z, a-z, 0-9, +, /, and = padding
    # Length must be multiple of 4 if padding is present
    is_b64_pattern = bool(re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", b64_candidate))
    if is_b64_pattern and len(b64_candidate) % 4 == 0 and len(b64_candidate) >= 4:
        try:
            decoded = base64_decode(b64_candidate)
            score_res = calculate_text_score(decoded)
            printable = is_printable_text(decoded)
            if "=" in b64_candidate and printable:
                confidence = "High"
            elif printable:
                confidence = "Medium"
            else:
                confidence = "Low"

            results.append(
                DetectionResult(
                    format_name="Base64",
                    is_match=True,
                    confidence=confidence,
                    details=f"Panjang {len(b64_candidate)} karakter, charset Base64 valid, teks UTF-8 valid.",
                    preview_decoded=decoded if printable else "<non-printable bytes>",
                    is_valid_utf8=True,
                    score=score_res.score,
                    score_reasons=score_res.reasons,
                )
            )
        except DecodingError as err:
            results.append(
                DetectionResult(
                    format_name="Base64",
                    is_match=False,
                    confidence="None",
                    details=f"Pola Base64 cocok namun gagal didekode: {err}",
                )
            )
    else:
        results.append(
            DetectionResult(
                format_name="Base64",
                is_match=False,
                confidence="None",
                details="Karakter berada di luar set Base64 atau panjang bukan kelipatan 4.",
            )
        )

    return results
