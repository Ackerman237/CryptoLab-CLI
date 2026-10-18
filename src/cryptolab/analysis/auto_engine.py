"""Auto Analyze engine for smart multi-stage cryptographic and encoding analysis."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from cryptolab.exceptions import CryptoLabError, DecodingError, InvalidInputError, InvalidKeyError
from cryptolab.encoding.base64_codec import base64_decode
from cryptolab.encoding.hex_codec import hex_decode
from cryptolab.encoding.binary_codec import binary_decode
from cryptolab.classical.caesar import caesar_decrypt
from cryptolab.classical.vigenere import vigenere_decrypt
from cryptolab.analysis.detect import detect_format, DetectionResult, is_printable_text

from cryptolab.analysis.scoring import calculate_text_score, ScoreResult
from cryptolab.analysis.pipeline import run_decode_pipeline, PipelineResult
from cryptolab.analysis.brute_force import caesar_brute_force, CaesarCandidate, find_best_candidate


@dataclass
class AutoCandidate:
    """A decryption or decoding candidate produced by Auto Analyze."""

    method: str
    category: str  # "Encoding", "Kriptografi Klasik", "Kriptografi Simetris"
    operation: str  # "Decode", "Decrypt", "Multi-stage Decode"
    status: str
    input_text: str
    output_text: str
    score: float
    score_level: str
    flag_detected: bool
    reasons: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    is_verified: bool = False
    needs_key: bool = False
    mode: Optional[str] = None
    padding: Optional[str] = None


@dataclass
class AutoAnalysisReport:
    """Consolidated report from Auto Analyze."""

    original_text: str
    top_candidate: Optional[AutoCandidate]
    candidates: List[AutoCandidate]
    detection_results: List[DetectionResult]
    possible_keyed_ciphers: List[str]
    has_high_confidence: bool
    notes: str


def _clean_hex_chars(text: str) -> str:
    """Extract clean hex characters without whitespace, delimiters, or prefixes."""
    cleaned = text.strip()
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    return re.sub(r"[\s:\-]+", "", cleaned)


def is_potential_aes_hex(text: str) -> bool:
    """Check if input resembles AES block ciphertext (hex string multiple of 32 chars / 16 bytes)."""
    clean_hex = _clean_hex_chars(text)
    if not clean_hex:
        return False
    if len(clean_hex) >= 32 and len(clean_hex) % 32 == 0:
        return bool(re.fullmatch(r"[0-9a-fA-F]+", clean_hex))
    return False


def is_potential_des_hex(text: str) -> bool:
    """Check if input resembles DES block ciphertext (hex string multiple of 16 chars / 8 bytes)."""
    clean_hex = _clean_hex_chars(text)
    if not clean_hex:
        return False
    if len(clean_hex) >= 16 and len(clean_hex) % 16 == 0:
        return bool(re.fullmatch(r"[0-9a-fA-F]+", clean_hex))
    return False


def is_potential_vigenere(text: str) -> bool:
    """Check if input resembles classical alphabetic ciphertext like Vigenere."""
    alpha_chars = [c for c in text if c.isalpha()]
    if len(alpha_chars) < 4:
        return False
    ratio = len(alpha_chars) / max(len(text.strip()), 1)
    return ratio >= 0.70



def run_auto_analysis(
    text: str,
    key: Optional[str] = None,
    iv: Optional[str] = None,
    max_depth: int = 5,
) -> AutoAnalysisReport:
    """Execute automated analysis on input text.

    1. Analyzes encoding formats (Base64, Hex, Binary) without claiming they are encryption.
    2. Runs multi-stage decoding pipeline up to max_depth.
    3. Runs Caesar brute force on original and intermediate decoded text.
    4. Detects potential keyed ciphers (DES block size hex, Vigenere).
    5. If key and/or IV are provided, evaluates candidate keyed ciphers.
    6. Returns candidates ranked by flag pattern detection, readability score, and validity.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")

    cleaned_input = text.strip()
    if not cleaned_input:
        raise InvalidInputError("Input teks tidak boleh kosong.")

    candidates: List[AutoCandidate] = []
    possible_keyed: List[str] = []

    # 1. Format Detection
    detections = detect_format(cleaned_input)

    # 2. Multi-stage Decode Pipeline (Keyless)
    try:
        pipeline_res: PipelineResult = run_decode_pipeline(cleaned_input, max_depth=max_depth)
        best_branch = pipeline_res.best_branch

        if pipeline_res.is_decoded and best_branch.steps:
            steps_desc = [f"{s.codec_name} ({s.input_preview} -> {s.output_preview})" for s in best_branch.steps]
            status_desc = "Dekode bertingkat berhasil" if best_branch.score >= 50.0 else "Dekode berhasil (kandidat heuristik)"
            candidates.append(
                AutoCandidate(
                    method=" -> ".join(s.codec_name for s in best_branch.steps),
                    category="Encoding",
                    operation="Multi-Stage Decode",
                    status=status_desc,
                    input_text=cleaned_input,
                    output_text=best_branch.final_text,
                    score=best_branch.score,
                    score_level=best_branch.score_level,
                    flag_detected=best_branch.flag_detected,
                    reasons=best_branch.reasons + ["Base64, Hex, dan Binary adalah format encoding, bukan enkripsi ber-kunci."],
                    steps=steps_desc,
                    is_verified=best_branch.flag_detected or best_branch.score >= 80.0,
                    needs_key=False,
                )
            )

            # Check alternative branches
            for alt in pipeline_res.alternative_branches:
                alt_steps = [f"{s.codec_name}" for s in alt.steps]
                candidates.append(
                    AutoCandidate(
                        method=" -> ".join(s.codec_name for s in alt.steps),
                        category="Encoding",
                        operation="Multi-Stage Decode",
                        status="Jalur dekode alternatif",
                        input_text=cleaned_input,
                        output_text=alt.final_text,
                        score=alt.score,
                        score_level=alt.score_level,
                        flag_detected=alt.flag_detected,
                        reasons=alt.reasons + ["Encoding alternatif yang valid secara sintaks."],
                        steps=alt_steps,
                        is_verified=alt.flag_detected,
                        needs_key=False,
                    )
                )
    except Exception:
        pass

    # 3. Caesar Brute Force (Keyless)
    # On original text
    if any(c.isalpha() for c in cleaned_input):
        try:
            caesar_candidates = caesar_brute_force(cleaned_input)
            best_caesar = find_best_candidate(caesar_candidates)
            if best_caesar and (best_caesar.score >= 45.0 or best_caesar.flag_detected):
                status_caesar = "Pola flag terdeteksi" if best_caesar.flag_detected else "Kandidat shift terbaik ditemukan"
                candidates.append(
                    AutoCandidate(
                        method=f"Caesar Cipher (Shift {best_caesar.shift:02d})",
                        category="Kriptografi Klasik",
                        operation="Decrypt",
                        status=status_caesar,
                        input_text=cleaned_input,
                        output_text=best_caesar.text,
                        score=best_caesar.score,
                        score_level=best_caesar.score_level,
                        flag_detected=best_caesar.flag_detected,
                        reasons=best_caesar.reasons + [f"Pergeseran shift {best_caesar.shift:02d} menghasilkan rasio huruf terbaca tinggi."],
                        steps=[f"Caesar Brute Force (Shift {best_caesar.shift:02d})"],
                        is_verified=best_caesar.flag_detected or best_caesar.score >= 80.0,
                        needs_key=False,
                    )
                )
        except Exception:
            pass

    # On decoded text from pipeline if different from original
    if candidates and candidates[0].output_text != cleaned_input and any(c.isalpha() for c in candidates[0].output_text):
        try:
            intermediate_text = candidates[0].output_text
            caesar_candidates_2 = caesar_brute_force(intermediate_text)
            best_caesar_2 = find_best_candidate(caesar_candidates_2)
            if best_caesar_2 and (best_caesar_2.score >= 55.0 or best_caesar_2.flag_detected):
                combined_method = f"{candidates[0].method} -> Caesar (Shift {best_caesar_2.shift:02d})"
                candidates.append(
                    AutoCandidate(
                        method=combined_method,
                        category="Encoding + Kriptografi Klasik",
                        operation="Decode + Decrypt",
                        status="Kandidat kombinasi ditemukan",
                        input_text=cleaned_input,
                        output_text=best_caesar_2.text,
                        score=best_caesar_2.score,
                        score_level=best_caesar_2.score_level,
                        flag_detected=best_caesar_2.flag_detected,
                        reasons=best_caesar_2.reasons + ["Hasil decoding diproses dengan dekripsi Caesar shift."],
                        steps=candidates[0].steps + [f"Caesar Shift {best_caesar_2.shift:02d}"],
                        is_verified=best_caesar_2.flag_detected or best_caesar_2.score >= 80.0,
                        needs_key=False,
                    )
                )
        except Exception:
            pass

    # 4. Check for Keyed Cipher Potential (AES, DES, RC2, Vigenere)
    if is_potential_aes_hex(cleaned_input):
        possible_keyed.append("AES")

    if is_potential_des_hex(cleaned_input):
        possible_keyed.append("DES")
        possible_keyed.append("RC2")

    if is_potential_vigenere(cleaned_input):
        possible_keyed.append("Vigenere")

    # 5. Process with Key and/or IV if provided
    if key:
        # Check AES
        if "AES" in possible_keyed or is_potential_aes_hex(cleaned_input):
            try:
                from cryptolab.symmetric.aes import aes_auto_analyze
                aes_results = aes_auto_analyze(cleaned_input, key=key, iv=iv)
                for ar in aes_results:
                    if ar.technical_success:
                        status_str = "Dekripsi AES berhasil (Teks terbaca)" if ar.readable_success else "Dekripsi teknis berhasil (Kandidat mode/padding)"
                        mode_iv_info = f"AES ({ar.mode}, Padding {ar.padding})"
                        reasons_list = list(ar.reasons)
                        if not ar.is_utf8:
                            reasons_list.append("Hasil berupa bytes non-UTF8 (ditampilkan dalam format heksadesimal)")
                        reasons_list.append("AES adalah standar industri modern (blok 128-bit).")

                        candidates.append(
                            AutoCandidate(
                                method=mode_iv_info,
                                category="Kriptografi Simetris Modern",
                                operation="Decrypt",
                                status=status_str,
                                input_text=cleaned_input,
                                output_text=ar.output_text,
                                score=ar.score,
                                score_level="Tinggi" if ar.readable_success else "Rendah",
                                flag_detected="flag{" in ar.output_text.lower(),
                                reasons=reasons_list,
                                steps=[f"AES Decrypt ({ar.mode}, {ar.padding})"],
                                is_verified=ar.readable_success,
                                needs_key=True,
                                mode=ar.mode,
                                padding=ar.padding,
                            )
                        )
            except Exception:
                pass

        # Check DES
        if "DES" in possible_keyed or is_potential_des_hex(cleaned_input):
            try:
                from cryptolab.symmetric.des import des_auto_analyze

                des_results = des_auto_analyze(cleaned_input, key=key, iv=iv)

                for dr in des_results:
                    if dr.technical_success:
                        status_str = "Dekripsi DES berhasil (Teks terbaca)" if dr.readable_success else "Dekripsi teknis berhasil (Kandidat mode/padding)"
                        mode_iv_info = f"DES ({dr.mode}, Padding {dr.padding})"
                        reasons_list = list(dr.reasons)
                        if not dr.is_utf8:
                            reasons_list.append("Hasil berupa bytes non-UTF8 (ditampilkan dalam format heksadesimal)")
                        reasons_list.append("Catatan: DES (56-bit) adalah cipher warisan untuk pembelajaran/CTF.")

                        candidates.append(
                            AutoCandidate(
                                method=mode_iv_info,
                                category="Kriptografi Simetris",
                                operation="Decrypt",
                                status=status_str,
                                input_text=cleaned_input,
                                output_text=dr.output_text,
                                score=dr.score,
                                score_level="Tinggi" if dr.readable_success else "Rendah",
                                flag_detected="flag{" in dr.output_text.lower(),
                                reasons=reasons_list,
                                steps=[f"DES Decrypt ({dr.mode}, {dr.padding})"],
                                is_verified=dr.readable_success,
                                needs_key=True,
                                mode=dr.mode,
                                padding=dr.padding,
                            )
                        )
            except Exception:
                pass

        # Check RC2/ARC2. RC2 shares DES's 64-bit block size, so both are
        # candidates for the same hexadecimal ciphertext shape.
        if "RC2" in possible_keyed or is_potential_des_hex(cleaned_input):
            try:
                from cryptolab.symmetric.rc2 import rc2_auto_analyze

                rc2_results = rc2_auto_analyze(cleaned_input, key=key, iv=iv)
                for rr in rc2_results:
                    if rr.technical_success:
                        status_str = "Dekripsi RC2 berhasil (Teks terbaca)" if rr.readable_success else "Dekripsi teknis berhasil (Kandidat mode/padding)"
                        mode_iv_info = f"RC2 ({rr.mode}, Padding {rr.padding})"
                        reasons_list = list(rr.reasons)
                        if not rr.is_utf8:
                            reasons_list.append("Hasil berupa bytes non-UTF8 (ditampilkan dalam format heksadesimal)")
                        reasons_list.append("RC2 adalah cipher legacy 64-bit; effective key length default 128-bit.")

                        candidates.append(
                            AutoCandidate(
                                method=mode_iv_info,
                                category="Kriptografi Simetris Legacy",
                                operation="Decrypt",
                                status=status_str,
                                input_text=cleaned_input,
                                output_text=rr.output_text,
                                score=rr.score,
                                score_level="Tinggi" if rr.readable_success else "Rendah",
                                flag_detected="flag{" in rr.output_text.lower(),
                                reasons=reasons_list,
                                steps=[f"RC2 Decrypt ({rr.mode}, {rr.padding})"],
                                is_verified=rr.readable_success,
                                needs_key=True,
                                mode=rr.mode,
                                padding=rr.padding,
                            )
                        )
            except Exception:
                pass

        # Check Vigenere
        if any(c.isalpha() for c in key):
            try:
                # Test on raw input
                if any(c.isalpha() for c in cleaned_input):
                    vig_out = vigenere_decrypt(cleaned_input, key)
                    score_vig = calculate_text_score(vig_out)
                    if score_vig.score >= 40.0 or score_vig.flag_detected:
                        candidates.append(
                            AutoCandidate(
                                method=f"Vigenere Cipher (Key: {key})",
                                category="Kriptografi Klasik",
                                operation="Decrypt",
                                status="Dekripsi Vigenere diuji",
                                input_text=cleaned_input,
                                output_text=vig_out,
                                score=score_vig.score,
                                score_level=score_vig.level,
                                flag_detected=score_vig.flag_detected,
                                reasons=score_vig.reasons,
                                steps=[f"Vigenere Decrypt dengan kunci '{key}'"],
                                is_verified=score_vig.flag_detected or score_vig.score >= 75.0,
                                needs_key=True,
                            )
                        )
            except Exception:
                pass

    # Sort candidates by: flag detected (highest priority), then score
    candidates.sort(
        key=lambda c: (c.flag_detected, c.is_verified, c.score),
        reverse=True,
    )

    # Deduplicate candidates by output_text and method
    unique_candidates: List[AutoCandidate] = []
    seen = set()
    for c in candidates:
        key_tuple = (c.method, c.output_text)
        if key_tuple not in seen:
            seen.add(key_tuple)
            unique_candidates.append(c)

    top_candidate = unique_candidates[0] if unique_candidates else None
    has_high_confidence = top_candidate.is_verified if top_candidate else False

    # Notes
    if top_candidate:
        if top_candidate.flag_detected:
            notes = "Pola format flag ditemukan pada kandidat utama. Kemungkinan besar merupakan solusi tantangan CTF."
        elif top_candidate.score >= 75.0:
            notes = "Kandidat memiliki tingkat keterbacaan tinggi berdasarkan analisis frekuensi huruf dan vokal."
        elif top_candidate.score >= 50.0:
            notes = "Kandidat ditemukan dengan keterbacaan sedang. Silakan periksa apakah makna teks sesuai konteks."
        else:
            notes = "Kandidat ditemukan secara teknis, namun skor keterbacaan masih rendah. Ciphertext mungkin membutuhkan key atau metode berkunci."
    else:
        notes = "Tidak ditemukan kandidat decoding langsung. Ciphertext kemungkinan menggunakan enkripsi berkunci (DES, Vigenere, dll)."

    return AutoAnalysisReport(
        original_text=cleaned_input,
        top_candidate=top_candidate,
        candidates=unique_candidates,
        detection_results=detections,
        possible_keyed_ciphers=possible_keyed,
        has_high_confidence=has_high_confidence,
        notes=notes,
    )
