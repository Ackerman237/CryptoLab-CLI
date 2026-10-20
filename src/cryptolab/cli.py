"""Command Line Interface and Presentation Layer for CryptoLab."""

import argparse
import sys
from typing import List, Optional, Dict, Any

from cryptolab import __version__
from cryptolab.exceptions import CryptoLabError, InvalidInputError
from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.classical.playfair import playfair_encrypt, playfair_decrypt
from cryptolab.classical.hill import hill_encrypt, hill_decrypt
from cryptolab.classical.affine import affine_encrypt, affine_decrypt, affine_brute_force, VALID_A_VALUES
from cryptolab.classical.railfence import railfence_encrypt, railfence_decrypt, railfence_brute_force
from cryptolab.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.encoding.binary_codec import binary_encode, binary_decode
from cryptolab.analysis.detect import detect_format, DetectionResult
from cryptolab.analysis.brute_force import (
    caesar_brute_force,
    CaesarCandidate,
    find_best_candidate,
)
from cryptolab.analysis.auto_decode import auto_decode, AutoDecodeResult
from cryptolab.analysis.pipeline import run_decode_pipeline, PipelineResult
from cryptolab.utils.history import (
    log_history,
    read_history,
    clear_history,
    get_history_file,
)
from cryptolab.symmetric.des import des_encrypt, des_decrypt, des_auto_analyze
from cryptolab.symmetric.aes import aes_encrypt, aes_decrypt, aes_auto_analyze
from cryptolab.symmetric.rc2 import rc2_encrypt, rc2_decrypt, rc2_auto_analyze
from cryptolab.hashing import (
    hash_compute,
    hash_file,
    hmac_compute,
    hmac_verify,
    pbkdf2_hash,
    pbkdf2_verify,
    bcrypt_hash,
    bcrypt_verify,
    hash_verify_integrity,
    generate_random_bytes,
    HashResult,
    HMACResult,
    BCRYPT_AVAILABLE,
)
from cryptolab.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
    RSAKeyPair,
    RSAResult,
    DHKeyExchangeResult,
)
from cryptolab.interactive import run_interactive_menu
from cryptolab.banner import warn_weak_hash, warn_ecb_mode, warn_rc2, print_warning


# UI Formatters designed for terminal clarity & lab screenshot reporting
DIVIDER = "=" * 70
THIN_DIVIDER = "-" * 70


def render_box(
    title: str,
    operation: str,
    input_text: str,
    output_text: str,
    params: Optional[dict] = None,
) -> str:
    """Render a clean, screenshot-friendly result box."""
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI v{__version__} - {title.upper()}",
        DIVIDER,
        f"  Operasi     : {operation}",
    ]
    if params:
        for k, v in params.items():
            lines.append(f"  {k:<12}: {v}")

    lines.extend([
        f"  Status      : BERHASIL (OK)",
        THIN_DIVIDER,
        "  INPUT:",
        f"  {input_text}",
        THIN_DIVIDER,
        "  OUTPUT:",
        f"  {output_text}",
        DIVIDER,
    ])
    return "\n".join(lines)


def render_error(title: str, message: str) -> str:
    """Render an error banner."""
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - ERROR: {title.upper()}",
        DIVIDER,
        f"  Pesan Kesalahan : {message}",
        DIVIDER,
    ]
    return "\n".join(lines)


def render_brute_force(
    ciphertext: str,
    candidates: List[CaesarCandidate],
    show_best_only: bool = False,
) -> str:
    """Render Caesar candidates in a clean tabular view or best candidate view."""
    best = find_best_candidate(candidates)

    if show_best_only and best:
        flag_note = " [Pola Flag Ditemukan!]" if best.flag_detected else ""
        lines = [
            DIVIDER,
            f"  CRYPTOLAB CLI - CAESAR BRUTE FORCE (KANDIDAT TERBAIK)",
            DIVIDER,
            f"  Ciphertext   : {ciphertext}",
            f"  Shift        : {best.shift:02d}",
            f"  Skor Teks    : {best.score:.1f}/100 ({best.score_level}){flag_note}",
            f"  Alasan Skor  : {'; '.join(best.reasons[:3])}",
            THIN_DIVIDER,
            "  KANDIDAT TERBAIK:",
            f"  {best.text}",
            THIN_DIVIDER,
            "  PERHATIAN PENTING:",
            "  Hasil terbaik didasarkan pada estimasi heuristik keterbacaan teks",
            "  dan belum tentu merupakan plaintext yang benar. Verifikasi konteks!",
            DIVIDER,
        ]
        return "\n".join(lines)

    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - CAESAR BRUTE FORCE (26 KANDIDAT)",
        DIVIDER,
        f"  Ciphertext : {ciphertext}",
        THIN_DIVIDER,
        "  Shift | Skor Huruf | Flag | Teks Hasil Dekripsi",
        "  ------+------------+------+----------------------------------------",
    ]

    for cand in candidates:
        is_best = best and cand.shift == best.shift
        tag = "  <-- (Kemungkinan Terbesar)" if is_best else ""
        flag_mark = "FLAG" if cand.flag_detected else "    "
        lines.append(
            f"   [{cand.shift:02d}]  |   {cand.common_ratio*100:5.1f}%   | {flag_mark} | {cand.text}{tag}"
        )

    lines.extend([
        DIVIDER,
        "  Catatan: Skor didasarkan pada frekuensi huruf umum (ETAOIN/Vokal).",
        "  Hasil terbaik adalah estimasi heuristik, bukan kepastian mutlak.",
        DIVIDER,
    ])
    return "\n".join(lines)


def render_detection(text: str, results: List[DetectionResult]) -> str:
    """Render format detection summary with UTF-8 validity and scoring."""
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - ANALISIS DETEKSI FORMAT",
        DIVIDER,
        f"  Input Teks  : {text[:60] + ('...' if len(text) > 60 else '')}",
        THIN_DIVIDER,
        "  Format      | Status | Keyakinan | UTF-8 | Preview Hasil Dekode",
        "  ------------+--------+-----------+-------+-------------------------",
    ]

    matches_count = sum(1 for r in results if r.is_match)

    for res in results:
        status_str = "MATCH " if res.is_match else "NO    "
        utf8_str = "Ya   " if res.is_valid_utf8 else "Tidak"
        preview = res.preview_decoded if res.preview_decoded else res.details
        if len(preview) > 25:
            preview = preview[:22] + "..."
        lines.append(
            f"  {res.format_name:<11} | {status_str} | {res.confidence:<9} | {utf8_str} | {preview}"
        )

    lines.extend([
        DIVIDER,
        "  HASIL ANALISIS:",
    ] + [
        f"  - [{r.format_name}] {r.details}"
        + (f" (Skor: {r.score:.1f}/100)" if r.is_match and r.is_valid_utf8 else "")
        for r in results
        if r.is_match
    ])

    if matches_count > 1:
        lines.extend([
            THIN_DIVIDER,
            f"  CATATAN MULTI-FORMAT: Input cocok dengan {matches_count} format berbeda.",
            "  Pilihlah format yang menghasilkan teks bermakna sesuai konteks lab.",
        ])

    lines.extend([
        DIVIDER,
        "  PERHATIAN: Deteksi bersifat heuristik/indikatif dan tidak dijamin",
        "  100% pasti benar. Selalu verifikasi konteks data laboratorium.",
        DIVIDER,
    ])
    return "\n".join(lines)


def render_auto_decode(result: AutoDecodeResult) -> str:
    """Render multi-stage auto-decode steps and final result (backward compatible)."""
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - MULTI-STAGE AUTO-DECODE",
        DIVIDER,
        f"  Status       : {result.notes}",
        f"  Total Tahap  : {result.total_steps}",
        THIN_DIVIDER,
    ]

    if result.steps:
        for step in result.steps:
            lines.extend([
                f"  [Tahap {step.step_number}] Menggunakan Format: {step.codec_name}",
                f"   - Input  : {step.input_preview}",
                f"   - Output : {step.output_preview}",
                "",
            ])
        lines.append(THIN_DIVIDER)

    lines.extend([
        "  HASIL AKHIR:",
        f"  {result.final_text}",
        DIVIDER,
    ])
    return "\n".join(lines)


def render_pipeline_result(result: PipelineResult) -> str:
    """Render multi-stage pipeline result with branching candidate details."""
    best = result.best_branch
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - MULTI-STAGE AUTO-DECODE PIPELINE",
        DIVIDER,
        f"  Status       : {result.notes}",
        f"  Total Tahap  : {result.total_steps}",
        f"  Skor Akhir   : {best.score:.1f}/100 ({best.score_level})"
        + (" [FLAG DITEMUKAN!]" if best.flag_detected else ""),
    ]

    if best.reasons:
        lines.append(f"  Indikator    : {'; '.join(best.reasons[:3])}")

    lines.append(THIN_DIVIDER)

    if best.steps:
        lines.append("  URUTAN TRANSFORMASI TERBAIK:")
        for step in best.steps:
            lines.extend([
                f"  [Tahap {step.step_number}] {step.codec_name}",
                f"   - Input  : {step.input_preview}",
                f"   - Output : {step.output_preview}",
            ])
        lines.append(THIN_DIVIDER)

    lines.extend([
        "  HASIL AKHIR (KANDIDAT UTAMA):",
        f"  {best.final_text}",
    ])

    if result.alternative_branches:
        lines.extend([
            THIN_DIVIDER,
            f"  JALUR ALTERNATIF RELEVAN ({len(result.alternative_branches)} kandidat lain):",
        ])
        for idx, alt in enumerate(result.alternative_branches, start=1):
            transform_chain = " -> ".join(s.codec_name for s in alt.steps)
            lines.append(
                f"  [Alt {idx}] {transform_chain} (Skor: {alt.score:.1f}/100) -> {alt.final_text[:50]}"
            )

    lines.extend([
        DIVIDER,
        "  CATATAN: Verifikasi manual disarankan jika hasil berupa kode/flag.",
        DIVIDER,
    ])
    return "\n".join(lines)


def render_history_list(records: List[Dict[str, Any]]) -> str:
    """Render table of recent analysis history."""
    lines = [
        DIVIDER,
        f"  CRYPTOLAB CLI - RIWAYAT ANALISIS LOKAL ({get_history_file()})",
        DIVIDER,
    ]

    if not records:
        lines.extend([
            "  Belum ada riwayat operasi yang tersimpan.",
            DIVIDER,
        ])
        return "\n".join(lines)

    lines.extend([
        "  Waktu (UTC)          | Operasi                 | Input / Hasil Ringkas",
        "  ---------------------+-------------------------+--------------------",
    ])

    for r in records:
        time_str = r.get("timestamp", "")[:19].replace("T", " ")
        op_str = r.get("operation", "")[:23]
        inp_str = r.get("input", "")[:15]
        out_str = r.get("output", "")[:20]
        preview = f"{inp_str} -> {out_str}"
        lines.append(f"  {time_str:<20} | {op_str:<23} | {preview}")

    lines.extend([
        DIVIDER,
        "  Gunakan opsi --clear pada perintah 'history' untuk menghapus log riwayat.",
        DIVIDER,
    ])
    return "\n".join(lines)


# Interactive menu implementation is modularized in cryptolab.interactive
# The imported run_interactive_menu function is exported here for backward compatibility.



def create_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser with Fase 2 capabilities."""
    parser = argparse.ArgumentParser(
        prog="cryptolab",
        description="CryptoLab CLI - Toolkit Kriptografi Klasik & Encoding untuk Praktikum Keamanan Informasi",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Nonaktifkan pencatatan riwayat operasi ke file lokal",
    )

    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    # Interactive menu
    subparsers.add_parser("menu", help="Buka antarmuka menu interaktif")

    # Caesar
    caesar_parser = subparsers.add_parser("caesar", help="Caesar Cipher operations")
    caesar_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "brute-force", "brute"],
        help="Aksi: encrypt, decrypt, atau brute-force",
    )
    caesar_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    caesar_parser.add_argument(
        "-s",
        "--shift",
        type=int,
        default=None,
        help="Nilai pergeseran integer (wajib untuk encrypt/decrypt)",
    )
    caesar_parser.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Tampilkan hanya kandidat terbaik berdasarkan skor heuristik",
    )

    # Brute Force Caesar (top-level shortcut)
    brute_parser = subparsers.add_parser(
        "brute", help="Caesar Cipher brute force (26 kandidat)"
    )
    brute_parser.add_argument(
        "-t", "--text", required=True, help="Ciphertext yang akan diuji"
    )
    brute_parser.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Tampilkan hanya kandidat terbaik berdasarkan skor heuristik",
    )

    # Vigenere
    vigenere_parser = subparsers.add_parser(
        "vigenere", help="Vigenere Cipher operations"
    )
    vigenere_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    vigenere_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    vigenere_parser.add_argument(
        "-k", "--key", required=True, help="Kunci alfabet untuk Vigenere"
    )

    # Playfair
    playfair_parser = subparsers.add_parser(
        "playfair", help="Playfair Cipher (Digram substitution 5x5 matrix)"
    )
    playfair_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    playfair_parser.add_argument(
        "-t", "--text", required=True, help="Plaintext (encrypt) atau ciphertext (decrypt)"
    )
    playfair_parser.add_argument(
        "-k", "--key", required=True, help="Kunci kata untuk matrix 5x5 (huruf A-Z)"
    )

    # Hill Cipher
    hill_parser = subparsers.add_parser(
        "hill", help="Hill Cipher (Matrix polygraphic substitution 2x2/3x3)"
    )
    hill_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    hill_parser.add_argument(
        "-t", "--text", required=True, help="Plaintext (encrypt) atau ciphertext (decrypt)"
    )
    hill_parser.add_argument(
        "-k", "--key", required=True, help="Key matrix space-separated (0-25). Contoh 2x2: '3 3 2 5'"
    )
    hill_parser.add_argument(
        "-s", "--size", type=int, default=2, choices=[2, 3], help="Ukuran matrix: 2 (2x2) atau 3 (3x3)"
    )

    # Affine Cipher
    affine_parser = subparsers.add_parser(
        "affine", help="Affine Cipher E(x) = (ax + b) mod 26"
    )
    affine_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "brute"], help="Aksi: encrypt, decrypt, atau brute-force"
    )
    affine_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    affine_parser.add_argument(
        "-a", "--mult", type=int, required=False, help="Kunci perkalian 'a' (harus coprime dengan 26: 1,3,5,7,9,11,15,17,19,21,23,25)"
    )
    affine_parser.add_argument(
        "-b", "--add", type=int, required=False, help="Kunci penjumlahan 'b' (0-25)"
    )

    # Rail Fence
    railfence_parser = subparsers.add_parser(
        "railfence", help="Rail Fence / Transposition Cipher (Zig-zag)"
    )
    railfence_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "brute"], help="Aksi: encrypt, decrypt, atau brute-force"
    )
    railfence_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    railfence_parser.add_argument(
        "-r", "--rails", type=int, default=2, help="Jumlah rail (minimal 2)"
    )
    railfence_parser.add_argument(
        "--max-rails", type=int, default=10, help="Maksimal rail untuk brute-force (default: 10)"
    )

    # Base64
    b64_parser = subparsers.add_parser("base64", help="Base64 encode/decode")
    b64_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    b64_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )

    # Hexadecimal
    hex_parser = subparsers.add_parser("hex", help="Hexadecimal encode/decode")
    hex_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    hex_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    hex_parser.add_argument(
        "-d",
        "--delimiter",
        default=" ",
        help="Pemisah byte heksadesimal pada encode (default: spasi)",
    )

    # Binary
    bin_parser = subparsers.add_parser("binary", help="8-bit Binary encode/decode")
    bin_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    bin_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    bin_parser.add_argument(
        "-d",
        "--delimiter",
        default=" ",
        help="Pemisah byte biner pada encode (default: spasi)",
    )

    # Analyze (Fase 2)
    analyze_parser = subparsers.add_parser(
        "analyze", help="Auto detect encoding & analisis format (Binary / Hex / Base64)"
    )
    analyze_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan dianalisis formatnya"
    )

    # Detect (Fase 1 alias)
    detect_parser = subparsers.add_parser(
        "detect", help="Deteksi format (Binary / Hex / Base64)"
    )
    detect_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan dianalisis formatnya"
    )

    # Auto-decode
    auto_parser = subparsers.add_parser(
        "auto", help="Multi-stage auto-decode pipeline untuk encoding bertingkat"
    )
    auto_parser.add_argument(
        "-t", "--text", required=True, help="Teks bertingkat yang akan di-decode"
    )
    auto_parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=5,
        help="Batas kedalaman maksimal transformasi (default: 5)",
    )

    # History (Fase 2)
    hist_parser = subparsers.add_parser(
        "history", help="Kelola dan lihat riwayat analisis lokal"
    )
    hist_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=15,
        help="Jumlah entri riwayat terbaru yang ditampilkan (default: 15)",
    )
    hist_parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Hapus seluruh catatan riwayat analisis lokal",
    )

    # DES (CBC / ECB)
    des_parser = subparsers.add_parser(
        "des", help="Operasi DES (Data Encryption Standard) CBC/ECB"
    )
    des_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    des_parser.add_argument(
        "-t",
        "--text",
        required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    des_parser.add_argument(
        "-k",
        "--key",
        default=None,
        help="Kunci DES sepanjang tepat 8 byte/karakter",
    )
    des_parser.add_argument(
        "-m",
        "--mode",
        default="CBC",
        choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode DES: CBC atau ECB (default: CBC)",
    )
    des_parser.add_argument(
        "--iv",
        default=None,
        help="Initialization Vector (IV) untuk mode CBC (tepat 8 byte)",
    )
    des_parser.add_argument(
        "-p",
        "--padding",
        default="PKCS7",
        choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )

    # AES (CBC / ECB)
    aes_parser = subparsers.add_parser(
        "aes", help="Operasi AES (Advanced Encryption Standard) 128-bit CBC/ECB"
    )
    aes_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    aes_parser.add_argument(
        "-t",
        "--text",
        required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    aes_parser.add_argument(
        "-k",
        "--key",
        default=None,
        help="Kunci AES sepanjang 16 byte/karakter (AES-128)",
    )
    aes_parser.add_argument(
        "-m",
        "--mode",
        default="CBC",
        choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode AES: CBC atau ECB (default: CBC)",
    )
    aes_parser.add_argument(
        "--iv",
        default=None,
        help="Initialization Vector (IV) untuk mode CBC (tepat 16 byte)",
    )
    aes_parser.add_argument(
        "-p",
        "--padding",
        default="PKCS7",
        choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )

    # RC2 / ARC2 (CBC / ECB)
    rc2_parser = subparsers.add_parser(
        "rc2", help="Operasi RC2 (ARC2) CBC/ECB untuk kompatibilitas cipher legacy"
    )
    rc2_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    rc2_parser.add_argument(
        "-t", "--text", required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    rc2_parser.add_argument("-k", "--key", default=None, help="Kunci RC2 sepanjang 5-16 byte")
    rc2_parser.add_argument(
        "-m", "--mode", default="CBC", choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode RC2: CBC atau ECB (default: CBC)",
    )
    rc2_parser.add_argument("--iv", default=None, help="IV CBC sepanjang tepat 8 byte")
    rc2_parser.add_argument(
        "-p", "--padding", default="PKCS7", choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )
    rc2_parser.add_argument(
        "--effective-keylen", type=int, default=128,
        help="Effective key length RC2 dalam bit (default: 128; rentang 40-1024)",
    )

    # Hash (MD5, SHA1, SHA256, SHA512)
    hash_parser = subparsers.add_parser("hash", help="Hash kriptografis (MD5, SHA1, SHA256, SHA512)")
    hash_parser.add_argument(
        "action", choices=["compute", "file", "verify"],
        help="Aksi: compute (string), file (hash file), verify (verifikasi integritas)"
    )
    hash_parser.add_argument(
        "-t", "--text", default=None, help="Input string untuk compute/verify"
    )
    hash_parser.add_argument(
        "-f", "--file", default=None, help="Path file untuk hash file"
    )
    hash_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["MD5", "SHA1", "SHA256", "SHA512"],
        help="Algoritma hash (default: SHA256)"
    )
    hash_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    hash_parser.add_argument(
        "--expected", default=None, help="Hash yang diharapkan untuk verify"
    )

    # HMAC
    hmac_parser = subparsers.add_parser("hmac", help="HMAC (Hash-based Message Authentication Code)")
    hmac_parser.add_argument(
        "action", choices=["compute", "verify"],
        help="Aksi: compute atau verify"
    )
    hmac_parser.add_argument(
        "-t", "--text", required=True, help="Pesan untuk HMAC"
    )
    hmac_parser.add_argument(
        "-k", "--key", required=True, help="Kunci rahasia"
    )
    hmac_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["MD5", "SHA1", "SHA256", "SHA512"],
        help="Algoritma HMAC (default: SHA256)"
    )
    hmac_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    hmac_parser.add_argument(
        "--expected", default=None, help="HMAC yang diharapkan untuk verify"
    )

    # PBKDF2
    pbkdf2_parser = subparsers.add_parser("pbkdf2", help="PBKDF2 password hashing")
    pbkdf2_parser.add_argument(
        "action", choices=["hash", "verify"],
        help="Aksi: hash password atau verify password"
    )
    pbkdf2_parser.add_argument(
        "-p", "--password", required=True, help="Password"
    )
    pbkdf2_parser.add_argument(
        "-s", "--salt", default=None, help="Salt (hex atau base64, random jika kosong)"
    )
    pbkdf2_parser.add_argument(
        "-i", "--iterations", type=int, default=100000, help="Jumlah iterasi (default: 100000)"
    )
    pbkdf2_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["SHA256", "SHA512"],
        help="Algoritma PBKDF2 (default: SHA256)"
    )
    pbkdf2_parser.add_argument(
        "--dklen", type=int, default=32, help="Panjang derived key dalam byte (default: 32)"
    )
    pbkdf2_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    pbkdf2_parser.add_argument(
        "--expected", default=None, help="Hash yang diharapkan untuk verify"
    )

    # Bcrypt (if available)
    if BCRYPT_AVAILABLE:
        bcrypt_parser = subparsers.add_parser("bcrypt", help="Bcrypt password hashing (adaptive)")
        bcrypt_parser.add_argument(
            "action", choices=["hash", "verify"],
            help="Aksi: hash password atau verify password"
        )
        bcrypt_parser.add_argument(
            "-p", "--password", required=True, help="Password"
        )
        bcrypt_parser.add_argument(
            "-r", "--rounds", type=int, default=12, help="Cost factor/rounds (4-31, default: 12)"
        )
        bcrypt_parser.add_argument(
            "--expected", default=None, help="Hash bcrypt untuk verify"
        )

    # Random bytes generator
    random_parser = subparsers.add_parser("random", help="Generate cryptographically secure random bytes")
    random_parser.add_argument(
        "-l", "--length", type=int, default=32, help="Panjang byte (default: 32, max: 1024)"
    )
    random_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )

    # RSA (Asymmetric Cryptography)
    rsa_parser = subparsers.add_parser("rsa", help="RSA Asymmetric Cryptography (KeyGen, Encrypt, Decrypt, Sign, Verify)")
    rsa_parser.add_argument(
        "action", choices=["keygen", "encrypt", "decrypt", "sign", "verify"],
        help="Aksi: keygen, encrypt, decrypt, sign, verify"
    )
    rsa_parser.add_argument(
        "-t", "--text", default=None, help="Plaintext (encrypt) / ciphertext (decrypt) / message (sign/verify)"
    )
    rsa_parser.add_argument(
        "--pubkey", default=None, help="Public key PEM (file path atau inline)"
    )
    rsa_parser.add_argument(
        "--privkey", default=None, help="Private key PEM (file path atau inline)"
    )
    rsa_parser.add_argument(
        "-k", "--keysize", type=int, default=2048, choices=[1024, 2048, 3072, 4096],
        help="Key size untuk keygen (default: 2048)"
    )
    rsa_parser.add_argument(
        "-p", "--padding", default="OAEP", choices=["OAEP", "PKCS1v15", "oaep", "pkcs1v15"],
        help="Padding scheme (default: OAEP)"
    )
    rsa_parser.add_argument(
        "--hash", default="SHA256", choices=["SHA256", "SHA512"],
        help="Hash algorithm untuk OAEP/PSS (default: SHA256)"
    )
    rsa_parser.add_argument(
        "--sigpadding", default="PSS", choices=["PSS", "PKCS1v15", "pss", "pkcs1v15"],
        help="Signature padding (default: PSS)"
    )
    rsa_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    rsa_parser.add_argument(
        "--signature", default=None, help="Signature untuk verify (hex/base64)"
    )

    # Diffie-Hellman Key Exchange
    dh_parser = subparsers.add_parser("dh", help="Diffie-Hellman Key Exchange (DHKE)")
    dh_parser.add_argument(
        "action", choices=["exchange", "derive"],
        help="Aksi: exchange (simulasi Alice-Bob), derive (derive key dari shared secret)"
    )
    dh_parser.add_argument(
        "-b", "--bits", type=int, default=2048, choices=[2048, 3072, 4096],
        help="Prime size dalam bit (default: 2048)"
    )
    dh_parser.add_argument(
        "--alice-priv", default=None, help="Alice private key (opsional, hex)"
    )
    dh_parser.add_argument(
        "--bob-priv", default=None, help="Bob private key (opsional, hex)"
    )
    dh_parser.add_argument(
        "--shared", default=None, help="Shared secret hex (untuk derive)"
    )
    dh_parser.add_argument(
        "--keylen", type=int, default=32, help="Derived key length dalam byte (default: 32)"
    )
    dh_parser.add_argument(
        "--hash", default="SHA256", choices=["SHA256", "SHA512"],
        help="Hash algorithm untuk key derivation (default: SHA256)"
    )
    dh_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )

    return parser




def handle_cli_args(args: argparse.Namespace) -> int:
    """Execute direct CLI commands based on parsed arguments."""
    try:
        history_enabled = not getattr(args, "no_history", False)

        if args.command == "menu" or args.command is None:
            run_interactive_menu()
            return 0

        if args.command == "caesar":
            if args.action in ("brute-force", "brute"):
                candidates = caesar_brute_force(args.text)
                show_best = getattr(args, "best", False)
                print(render_brute_force(args.text, candidates, show_best_only=show_best))
                best = find_best_candidate(candidates)
                log_history(
                    "Caesar Brute Force",
                    args.text,
                    best.text if best else "",
                    {"best_shift": best.shift if best else None},
                    enabled=history_enabled,
                )
                return 0

            # Encrypt / Decrypt actions require shift
            if args.shift is None:
                raise InvalidInputError(
                    "Operasi encrypt/decrypt Caesar memerlukan parameter --shift / -s."
                )

            if args.action == "encrypt":
                res = caesar_encrypt(args.text, args.shift)
                print(
                    render_box(
                        "Hasil Enkripsi",
                        "Caesar Cipher (ENCRYPT)",
                        args.text,
                        res,
                        {"Shift": args.shift},
                    )
                )
                log_history("Caesar Encrypt", args.text, res, {"shift": args.shift}, enabled=history_enabled)
            else:
                res = caesar_decrypt(args.text, args.shift)
                print(
                    render_box(
                        "Hasil Dekripsi",
                        "Caesar Cipher (DECRYPT)",
                        args.text,
                        res,
                        {"Shift": args.shift},
                    )
                )
                log_history("Caesar Decrypt", args.text, res, {"shift": args.shift}, enabled=history_enabled)
            return 0

        if args.command == "brute":
            candidates = caesar_brute_force(args.text)
            show_best = getattr(args, "best", False)
            print(render_brute_force(args.text, candidates, show_best_only=show_best))
            best = find_best_candidate(candidates)
            log_history(
                "Caesar Brute Force",
                args.text,
                best.text if best else "",
                {"best_shift": best.shift if best else None},
                enabled=history_enabled,
            )
            return 0

        if args.command == "vigenere":
            if args.action == "encrypt":
                res = vigenere_encrypt(args.text, args.key)
                print(
                    render_box(
                        "Hasil Enkripsi",
                        "Vigenere Cipher (ENCRYPT)",
                        args.text,
                        res,
                        {"Kunci": args.key},
                    )
                )
                log_history("Vigenere Encrypt", args.text, res, {"key_length": len(args.key)}, enabled=history_enabled)
            else:
                res = vigenere_decrypt(args.text, args.key)
                print(
                    render_box(
                        "Hasil Dekripsi",
                        "Vigenere Cipher (DECRYPT)",
                        args.text,
                        res,
                        {"Kunci": args.key},
                    )
                )
                log_history("Vigenere Decrypt", args.text, res, {"key_length": len(args.key)}, enabled=history_enabled)
            return 0

        if args.command == "playfair":
            if args.action == "encrypt":
                res = playfair_encrypt(args.text, args.key)
                print(
                    render_box(
                        "Hasil Enkripsi Playfair",
                        "Playfair Cipher (ENCRYPT)",
                        args.text,
                        res.output_text,
                        {"Key": args.key, "Matrix": "5x5 (I=J)"},
                    )
                )
                log_history("Playfair Encrypt", args.text, res.output_text, {"key": args.key}, enabled=history_enabled)
            else:
                res = playfair_decrypt(args.text, args.key)
                print(
                    render_box(
                        "Hasil Dekripsi Playfair",
                        "Playfair Cipher (DECRYPT)",
                        args.text,
                        res.output_text,
                        {"Key": args.key, "Note": "Mungkin mengandung padding X"},
                    )
                )
                log_history("Playfair Decrypt", args.text, res.output_text, {"key": args.key}, enabled=history_enabled)
            return 0

        if args.command == "hill":
            if args.action == "encrypt":
                res = hill_encrypt(args.text, args.key, args.size)
                print(
                    render_box(
                        f"Hasil Enkripsi Hill {args.size}x{args.size}",
                        f"Hill Cipher (ENCRYPT)",
                        args.text,
                        res.output_text,
                        {"Key Matrix": args.key, "Size": f"{args.size}x{args.size}", "Det": res.determinant, "DetInv": res.determinant_inv},
                    )
                )
                log_history(f"Hill {args.size}x{args.size} Encrypt", args.text, res.output_text, {"key": args.key, "size": args.size}, enabled=history_enabled)
            else:
                res = hill_decrypt(args.text, args.key, args.size)
                print(
                    render_box(
                        f"Hasil Dekripsi Hill {args.size}x{args.size}",
                        f"Hill Cipher (DECRYPT)",
                        args.text,
                        res.output_text,
                        {"Key Matrix": args.key, "Size": f"{args.size}x{args.size}", "Note": "Mungkin mengandung padding X"},
                    )
                )
                log_history(f"Hill {args.size}x{args.size} Decrypt", args.text, res.output_text, {"key": args.key, "size": args.size}, enabled=history_enabled)
            return 0

        if args.command == "affine":
            if args.action == "brute":
                if not args.text:
                    raise InvalidInputError("Brute-force memerlukan --text / -t.")
                candidates = affine_brute_force(args.text)
                if not candidates:
                    print(render_error("Affine Brute Force", "Tidak ada kandidat valid."))
                    return 1
                best = candidates[0]
                print(
                    render_box(
                        "Hasil Affine Brute Force",
                        f"Affine (Best: a={best.a}, b={best.b})",
                        args.text,
                        best.output_text,
                        {"Total Candidates": len(candidates), "Top a": best.a, "Top b": best.b},
                    )
                )
                log_history("Affine Brute Force", args.text, best.output_text, {"candidates": len(candidates)}, enabled=history_enabled)
                return 0
            
            if args.mult is None or args.add is None:
                raise InvalidInputError("Operasi encrypt/decrypt memerlukan --mult / -a dan --add / -b.")
            
            if args.action == "encrypt":
                res = affine_encrypt(args.text, args.mult, args.add)
                print(
                    render_box(
                        "Hasil Enkripsi Affine",
                        f"Affine Cipher (ENCRYPT) a={args.mult}, b={args.add}",
                        args.text,
                        res.output_text,
                        {"a": args.mult, "b": args.add, "a_inv": res.a_inv, "Valid a": f"{len(VALID_A_VALUES)} values"},
                    )
                )
                log_history("Affine Encrypt", args.text, res.output_text, {"a": args.mult, "b": args.add}, enabled=history_enabled)
            else:
                res = affine_decrypt(args.text, args.mult, args.add)
                print(
                    render_box(
                        "Hasil Dekripsi Affine",
                        f"Affine Cipher (DECRYPT) a={args.mult}, b={args.add}",
                        args.text,
                        res.output_text,
                        {"a": args.mult, "b": args.add, "a_inv": res.a_inv},
                    )
                )
                log_history("Affine Decrypt", args.text, res.output_text, {"a": args.mult, "b": args.add}, enabled=history_enabled)
            return 0

        if args.command == "railfence":
            if args.action == "brute":
                if not args.text:
                    raise InvalidInputError("Brute-force memerlukan --text / -t.")
                candidates = railfence_brute_force(args.text, args.max_rails)
                if not candidates:
                    print(render_error("Rail Fence Brute Force", "Tidak ada kandidat valid."))
                    return 1
                best = candidates[0]
                print(
                    render_box(
                        "Hasil Rail Fence Brute Force",
                        f"Rail Fence (Best: {best.rails} rails)",
                        args.text,
                        best.output_text,
                        {"Total Candidates": len(candidates), "Top Rails": best.rails},
                    )
                )
                log_history("Rail Fence Brute Force", args.text, best.output_text, {"candidates": len(candidates)}, enabled=history_enabled)
                return 0
            
            if args.action == "encrypt":
                res = railfence_encrypt(args.text, args.rails)
                pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                print(
                    render_box(
                        f"Hasil Enkripsi Rail Fence",
                        f"Rail Fence (ENCRYPT) {args.rails} rails",
                        args.text,
                        res.output_text,
                        {"Rails": args.rails, "Pattern": "Zig-zag"},
                    )
                )
                print(f"\n  Rail Pattern:\n{pattern_str}\n")
                log_history(f"Rail Fence {args.rails} Encrypt", args.text, res.output_text, {"rails": args.rails}, enabled=history_enabled)
            else:
                res = railfence_decrypt(args.text, args.rails)
                pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                print(
                    render_box(
                        f"Hasil Dekripsi Rail Fence",
                        f"Rail Fence (DECRYPT) {args.rails} rails",
                        args.text,
                        res.output_text,
                        {"Rails": args.rails, "Note": "Transposition cipher"},
                    )
                )
                print(f"\n  Rail Pattern:\n{pattern_str}\n")
                log_history(f"Rail Fence {args.rails} Decrypt", args.text, res.output_text, {"rails": args.rails}, enabled=history_enabled)
            return 0


        if args.command == "base64":
            if args.action == "encode":
                res = base64_encode(args.text)
                print(render_box("Hasil Base64", "Base64 (ENCODE)", args.text, res))
                log_history("Base64 Encode", args.text, res, enabled=history_enabled)
            else:
                res = base64_decode(args.text)
                print(render_box("Hasil Base64", "Base64 (DECODE)", args.text, res))
                log_history("Base64 Decode", args.text, res, enabled=history_enabled)
            return 0

        if args.command == "hex":
            if args.action == "encode":
                delim = getattr(args, "delimiter", " ")
                res = hex_encode(args.text, delimiter=delim)
                print(
                    render_box(
                        "Hasil Hex",
                        "Hexadecimal (ENCODE)",
                        args.text,
                        res,
                        {"Delimiter": repr(delim)},
                    )
                )
                log_history("Hex Encode", args.text, res, {"delimiter": delim}, enabled=history_enabled)
            else:
                res = hex_decode(args.text)
                print(render_box("Hasil Hex", "Hexadecimal (DECODE)", args.text, res))
                log_history("Hex Decode", args.text, res, enabled=history_enabled)
            return 0

        if args.command == "binary":
            if args.action == "encode":
                delim = getattr(args, "delimiter", " ")
                res = binary_encode(args.text, delimiter=delim)
                print(
                    render_box(
                        "Hasil Binary",
                        "Binary 8-Bit (ENCODE)",
                        args.text,
                        res,
                        {"Delimiter": repr(delim)},
                    )
                )
                log_history("Binary Encode", args.text, res, {"delimiter": delim}, enabled=history_enabled)
            else:
                res = binary_decode(args.text)
                print(
                    render_box(
                        "Hasil Binary", "Binary 8-Bit (DECODE)", args.text, res
                    )
                )
                log_history("Binary Decode", args.text, res, enabled=history_enabled)
            return 0

        if args.command == "des":
            norm_mode = args.mode.upper()
            norm_padding = "PKCS7" if args.padding.upper() == "PKCS7" else "None"

            # Warning for ECB mode
            if norm_mode == "ECB":
                print_warning(warn_ecb_mode())

            if args.action == "auto":
                candidates = des_auto_analyze(args.text, key=args.key, iv=args.iv)
                if not candidates:
                    print(render_error("DES Auto", "Tidak ada konfigurasi DES yang berhasil didekripsi."))
                    return 1
                best_des = candidates[0]
                print(
                    render_box(
                        "Hasil DES Auto",
                        f"DES Auto ({best_des.mode}, Padding {best_des.padding})",
                        args.text,
                        best_des.output_text,
                        {"Mode": best_des.mode, "Padding": best_des.padding, "Skor": f"{best_des.score:.1f}/100"},
                    )
                )
                log_history("DES Auto", args.text, best_des.output_text, {"mode": best_des.mode, "padding": best_des.padding}, enabled=history_enabled)
                return 0

            if not args.key:
                raise InvalidInputError("Operasi encrypt/decrypt DES memerlukan parameter --key / -k (8 byte).")

            if args.action == "encrypt":
                enc_res = des_encrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
                print(
                    render_box(
                        "Hasil Enkripsi DES",
                        f"DES ({norm_mode}) (ENCRYPT)",
                        args.text,
                        enc_res.output_text,
                        {"Mode": norm_mode, "Padding": norm_padding},
                    )
                )
                log_history("DES Encrypt", args.text, enc_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
                return 0
            else:
                dec_res = des_decrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
                print(
                    render_box(
                        "Hasil Dekripsi DES",
                        f"DES ({norm_mode}) (DECRYPT)",
                        args.text,
                        dec_res.output_text,
                        {"Mode": norm_mode, "Padding": norm_padding, "UTF-8": "Ya" if dec_res.is_utf8 else "Tidak (Hex)"},
                    )
                )
                log_history("DES Decrypt", args.text, dec_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
                return 0

        if args.command == "aes":
            norm_mode = args.mode.upper()
            norm_padding = "PKCS7" if args.padding.upper() == "PKCS7" else "None"

            # Warning for ECB mode
            if norm_mode == "ECB":
                print_warning(warn_ecb_mode())

            if args.action == "auto":
                candidates = aes_auto_analyze(args.text, key=args.key, iv=args.iv)
                if not candidates:
                    print(render_error("AES Auto", "Tidak ada konfigurasi AES yang berhasil didekripsi."))
                    return 1
                best_aes = candidates[0]
                print(
                    render_box(
                        "Hasil AES Auto",
                        f"AES Auto ({best_aes.mode}, Padding {best_aes.padding})",
                        args.text,
                        best_aes.output_text,
                        {"Mode": best_aes.mode, "Padding": best_aes.padding, "Skor": f"{best_aes.score:.1f}/100"},
                    )
                )
                log_history("AES Auto", args.text, best_aes.output_text, {"mode": best_aes.mode, "padding": best_aes.padding}, enabled=history_enabled)
                return 0

            if not args.key:
                raise InvalidInputError("Operasi encrypt/decrypt AES memerlukan parameter --key / -k (16 byte).")

            if args.action == "encrypt":
                enc_res = aes_encrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
                print(
                    render_box(
                        "Hasil Enkripsi AES",
                        f"AES ({norm_mode}) (ENCRYPT)",
                        args.text,
                        enc_res.output_text,
                        {"Mode": norm_mode, "Padding": norm_padding},
                    )
                )
                log_history("AES Encrypt", args.text, enc_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
                return 0
            else:
                dec_res = aes_decrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
                print(
                    render_box(
                        "Hasil Dekripsi AES",
                        f"AES ({norm_mode}) (DECRYPT)",
                        args.text,
                        dec_res.output_text,
                        {"Mode": norm_mode, "Padding": norm_padding, "UTF-8": "Ya" if dec_res.is_utf8 else "Tidak (Hex)"},
                    )
                )
                log_history("AES Decrypt", args.text, dec_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
                return 0

        if args.command == "rc2":
            norm_mode = args.mode.upper()
            norm_padding = "PKCS7" if args.padding.upper() == "PKCS7" else "None"
            effective_keylen = args.effective_keylen

            # Warning for RC2 legacy cipher
            print_warning(warn_rc2())
            
            # Warning for ECB mode
            if norm_mode == "ECB":
                print_warning(warn_ecb_mode())

            if args.action == "auto":
                candidates = rc2_auto_analyze(
                    args.text, key=args.key, iv=args.iv, effective_keylen=effective_keylen
                )
                if not candidates:
                    print(render_error("RC2 Auto", "Tidak ada konfigurasi RC2 yang berhasil didekripsi."))
                    return 1
                best_rc2 = candidates[0]
                print(render_box(
                    "Hasil RC2 Auto", f"RC2 Auto ({best_rc2.mode}, Padding {best_rc2.padding})",
                    args.text, best_rc2.output_text,
                    {"Mode": best_rc2.mode, "Padding": best_rc2.padding,
                     "Effective": f"{effective_keylen} bit", "Skor": f"{best_rc2.score:.1f}/100"},
                ))
                log_history("RC2 Auto", args.text, best_rc2.output_text,
                            {"mode": best_rc2.mode, "padding": best_rc2.padding}, enabled=history_enabled)
                return 0

            if not args.key:
                raise InvalidInputError("Operasi encrypt/decrypt RC2 memerlukan parameter --key / -k.")
            params = {"Mode": norm_mode, "Padding": norm_padding, "Effective": f"{effective_keylen} bit"}
            if args.action == "encrypt":
                result = rc2_encrypt(args.text, args.key, norm_mode, args.iv, norm_padding, effective_keylen)
                print(render_box("Hasil Enkripsi RC2", f"RC2 ({norm_mode}) (ENCRYPT)", args.text, result.output_text, params))
                log_history("RC2 Encrypt", args.text, result.output_text, params, enabled=history_enabled)
            else:
                result = rc2_decrypt(args.text, args.key, norm_mode, args.iv, norm_padding, effective_keylen)
                params["UTF-8"] = "Ya" if result.is_utf8 else "Tidak (Hex)"
                print(render_box("Hasil Dekripsi RC2", f"RC2 ({norm_mode}) (DECRYPT)", args.text, result.output_text, params))
                log_history("RC2 Decrypt", args.text, result.output_text, params, enabled=history_enabled)
            return 0

        if args.command == "hash":
            algo = args.algorithm.upper()
            enc = args.encoding.lower()

            # Show warning for weak hash algorithms
            warning = warn_weak_hash(algo)
            if warning:
                print_warning(warning)

            if args.action == "compute":
                if not args.text:
                    raise InvalidInputError("Operasi compute memerlukan parameter --text / -t.")
                res = hash_compute(args.text, algorithm=algo, encoding=enc)
                print(
                    render_box(
                        f"Hasil Hash {algo}",
                        f"{algo} Hash (COMPUTE)",
                        args.text,
                        res.output_hash,
                        {"Algorithm": algo, "Encoding": enc.upper()},
                    )
                )
                log_history(f"Hash {algo} Compute", args.text, res.output_hash, {"algo": algo, "encoding": enc}, enabled=history_enabled)
                return 0

            elif args.action == "file":
                if not args.file:
                    raise InvalidInputError("Operasi file memerlukan parameter --file / -f.")
                res = hash_file(args.file, algorithm=algo)
                print(
                    render_box(
                        f"Hasil Hash File {algo}",
                        f"{algo} Hash (FILE)",
                        args.file,
                        res.output_hash,
                        {"Algorithm": algo, "File": args.file},
                    )
                )
                log_history(f"Hash {algo} File", args.file, res.output_hash, {"algo": algo, "filepath": args.file}, enabled=history_enabled)
                return 0

            elif args.action == "verify":
                if not args.text or not args.expected:
                    raise InvalidInputError("Operasi verify memerlukan --text / -t dan --expected.")
                res = hash_verify_integrity(args.text, args.expected, algorithm=algo, encoding=enc)
                status = "VALID" if res.match else "INVALID"
                print(
                    render_box(
                        f"Verifikasi Integritas {algo}",
                        f"{algo} Verify ({status})",
                        args.text,
                        "COCOK" if res.match else "TIDAK COCOK",
                        {"Algorithm": algo, "Expected": args.expected, "Status": status},
                    )
                )
                log_history(f"Hash {algo} Verify", args.text, "COCOK" if res.match else "TIDAK COCOK", {"algo": algo, "match": res.match}, enabled=history_enabled)
                return 0

        if args.command == "hmac":
            algo = args.algorithm.upper()
            enc = args.encoding.lower()

            if args.action == "compute":
                res = hmac_compute(args.text, args.key, algorithm=algo, encoding=enc)
                print(
                    render_box(
                        f"Hasil HMAC-{algo}",
                        f"HMAC-{algo} (COMPUTE)",
                        args.text,
                        res.output_hmac,
                        {"Algorithm": f"HMAC-{algo}", "Key Length": f"{len(args.key)} bytes", "Encoding": enc.upper()},
                    )
                )
                log_history(f"HMAC-{algo} Compute", args.text, res.output_hmac, {"algo": algo, "encoding": enc}, enabled=history_enabled)
                return 0

            elif args.action == "verify":
                if not args.expected:
                    raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
                match = hmac_verify(args.text, args.key, args.expected, algorithm=algo, encoding=enc)
                status = "VALID" if match else "INVALID"
                print(
                    render_box(
                        f"Verifikasi HMAC-{algo}",
                        f"HMAC-{algo} Verify ({status})",
                        args.text,
                        "COCOK" if match else "TIDAK COCOK",
                        {"Algorithm": f"HMAC-{algo}", "Status": status},
                    )
                )
                log_history(f"HMAC-{algo} Verify", args.text, "COCOK" if match else "TIDAK COCOK", {"algo": algo, "match": match}, enabled=history_enabled)
                return 0

        if args.command == "pbkdf2":
            algo = args.algorithm.upper()
            enc = args.encoding.lower()

            if args.action == "hash":
                res = pbkdf2_hash(args.password, salt=args.salt, iterations=args.iterations, algorithm=algo, dklen=args.dklen, encoding=enc)
                print(
                    render_box(
                        f"Hasil PBKDF2-{algo}",
                        f"PBKDF2-{algo} (HASH)",
                        "********",
                        f"Salt: {res.salt}\nHash: {res.hash_value}",
                        {"Algorithm": f"PBKDF2-{algo}", "Iterations": f"{res.iterations:,}", "DKLen": f"{args.dklen} bytes", "Encoding": enc.upper()},
                    )
                )
                log_history(f"PBKDF2-{algo} Hash", "********", res.hash_value, {"algo": algo, "iterations": args.iterations, "salt": res.salt}, enabled=history_enabled)
                return 0

            elif args.action == "verify":
                if not args.expected:
                    raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
                res = pbkdf2_verify(args.password, args.salt, args.expected, iterations=args.iterations, algorithm=algo, dklen=args.dklen, encoding=enc)
                status = "COCOK" if res.match else "TIDAK COCOK"
                print(
                    render_box(
                        f"Verifikasi PBKDF2-{algo}",
                        f"PBKDF2-{algo} Verify ({status})",
                        "********",
                        status,
                        {"Algorithm": f"PBKDF2-{algo}", "Status": status},
                    )
                )
                log_history(f"PBKDF2-{algo} Verify", "********", status, {"algo": algo, "match": res.match}, enabled=history_enabled)
                return 0

        if BCRYPT_AVAILABLE and args.command == "bcrypt":
            if args.action == "hash":
                res = bcrypt_hash(args.password, rounds=args.rounds)
                print(
                    render_box(
                        "Hasil Bcrypt",
                        f"BCRYPT (HASH)",
                        "********",
                        res.hash_value,
                        {"Algorithm": "BCRYPT", "Rounds": res.iterations},
                    )
                )
                log_history("Bcrypt Hash", "********", res.hash_value, {"rounds": args.rounds}, enabled=history_enabled)
                return 0

            elif args.action == "verify":
                if not args.expected:
                    raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
                res = bcrypt_verify(args.password, args.expected)
                status = "COCOK" if res.match else "TIDAK COCOK"
                print(
                    render_box(
                        "Verifikasi Bcrypt",
                        f"BCRYPT Verify ({status})",
                        "********",
                        status,
                        {"Algorithm": "BCRYPT", "Status": status},
                    )
                )
                log_history("Bcrypt Verify", "********", status, {"match": res.match}, enabled=history_enabled)
                return 0

        if args.command == "random":
            length = args.length
            enc = args.encoding.lower()
            out = generate_random_bytes(length, encoding=enc)
            print(
                render_box(
                    "Random Bytes",
                    f"Random ({length} bytes, {enc.upper()})",
                    "",
                    out,
                    {"Length": f"{length} bytes", "Encoding": enc.upper()},
                )
            )
            log_history("Random Bytes", "", out, {"length": length, "encoding": enc}, enabled=history_enabled)
            return 0

        if args.command == "rsa":
            action = args.action
            enc = args.encoding.lower()
            padding = args.padding.upper()
            hash_algo = args.hash.upper()
            sig_padding = args.sigpadding.upper()

            def load_key(key_arg: str, is_private: bool) -> str:
                """Load key from file or use inline."""
                if key_arg is None:
                    return None
                if key_arg.startswith("-----BEGIN"):
                    return key_arg
                try:
                    with open(key_arg, "r") as f:
                        return f.read().strip()
                except OSError:
                    return key_arg

            if action == "keygen":
                kp = rsa_generate_keypair(args.keysize)
                print(
                    render_box(
                        f"RSA {args.keysize}-bit Key Pair",
                        "RSA Key Generation",
                        "",
                        f"PRIVATE KEY:\n{kp.private_key_pem}\n\nPUBLIC KEY:\n{kp.public_key_pem}",
                        {"Key Size": f"{args.keysize} bit"},
                    )
                )
                log_history(f"RSA KeyGen {args.keysize}", "", "KEYPAIR GENERATED", {"keysize": args.keysize}, enabled=history_enabled)
                return 0

            elif action == "encrypt":
                if not args.text:
                    raise InvalidInputError("Encrypt memerlukan --text / -t.")
                if not args.pubkey:
                    raise InvalidInputError("Encrypt memerlukan --pubkey.")
                pubkey = load_key(args.pubkey, is_private=False)
                res = rsa_encrypt(args.text, pubkey, padding=padding, hash_algo=hash_algo, encoding=enc)
                print(
                    render_box(
                        f"Hasil RSA Enkripsi",
                        f"RSA-{res.algorithm} (ENCRYPT)",
                        args.text,
                        res.output_text,
                        {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Encoding": enc.upper()},
                    )
                )
                log_history(f"RSA Encrypt", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
                return 0

            elif action == "decrypt":
                if not args.text:
                    raise InvalidInputError("Decrypt memerlukan --text / -t (ciphertext).")
                if not args.privkey:
                    raise InvalidInputError("Decrypt memerlukan --privkey.")
                privkey = load_key(args.privkey, is_private=True)
                res = rsa_decrypt(args.text, privkey, padding=padding, hash_algo=hash_algo, encoding=enc)
                print(
                    render_box(
                        f"Hasil RSA Dekripsi",
                        f"RSA-{res.algorithm} (DECRYPT)",
                        f"[{len(args.text)} chars ciphertext]",
                        res.output_text,
                        {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": "UTF-8" if not res.is_hex else "Hex"},
                    )
                )
                log_history(f"RSA Decrypt", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
                return 0

            elif action == "sign":
                if not args.text:
                    raise InvalidInputError("Sign memerlukan --text / -t (message).")
                if not args.privkey:
                    raise InvalidInputError("Sign memerlukan --privkey.")
                privkey = load_key(args.privkey, is_private=True)
                res = rsa_sign(args.text, privkey, padding=sig_padding, hash_algo=hash_algo, encoding=enc)
                print(
                    render_box(
                        f"Hasil RSA Sign",
                        f"RSA-{res.algorithm} (SIGN)",
                        args.text,
                        res.output_text,
                        {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Encoding": enc.upper()},
                    )
                )
                log_history(f"RSA Sign", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
                return 0

            elif action == "verify":
                if not args.text:
                    raise InvalidInputError("Verify memerlukan --text / -t (message).")
                if not args.pubkey:
                    raise InvalidInputError("Verify memerlukan --pubkey.")
                if not args.signature:
                    raise InvalidInputError("Verify memerlukan --signature.")
                pubkey = load_key(args.pubkey, is_private=False)
                res = rsa_verify(args.text, args.signature, pubkey, padding=sig_padding, hash_algo=hash_algo, encoding=enc)
                status = "VALID (SAH)" if "VALID" in res.output_text else "INVALID (TIDAK SAH)"
                print(
                    render_box(
                        f"Verifikasi RSA Signature",
                        f"RSA-{res.algorithm} (VERIFY)",
                        args.text,
                        res.output_text,
                        {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": status},
                    )
                )
                log_history(f"RSA Verify", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
                return 0

        if args.command == "dh":
            action = args.action
            enc = args.encoding.lower()
            hash_algo = args.hash.upper()

            if action == "exchange":
                alice_priv = None
                bob_priv = None
                if args.alice_priv:
                    alice_priv = int(_clean_hex(args.alice_priv), 16)
                if args.bob_priv:
                    bob_priv = int(_clean_hex(args.bob_priv), 16)

                res = dh_key_exchange(args.bits, alice_private=alice_priv, bob_private=bob_priv)
                output = (
                    f"Prime (p): {res.prime_hex[:64]}... ({len(res.prime_hex)} hex chars)\n"
                    f"Generator (g): {res.generator}\n\n"
                    f"Alice Private: {res.alice_private_hex}\n"
                    f"Alice Public:  {res.alice_public_hex}\n\n"
                    f"Bob Private:   {res.bob_private_hex}\n"
                    f"Bob Public:    {res.bob_public_hex}\n\n"
                    f"SHARED SECRET: {res.shared_secret_hex}"
                )
                print(
                    render_box(
                        f"DHKE {args.bits}-bit Exchange",
                        f"Diffie-Hellman Key Exchange",
                        "",
                        output,
                        {"Prime Size": f"{args.bits} bit", "Generator": str(res.generator)},
                    )
                )
                log_history(f"DHKE {args.bits}", "", "EXCHANGE COMPLETE", {"bits": args.bits}, enabled=history_enabled)
                return 0

            elif action == "derive":
                if not args.shared:
                    raise InvalidInputError("Derive memerlukan --shared (shared secret hex).")
                derived = dh_derive_key(args.shared, key_length=args.keylen, hash_algo=hash_algo)
                print(
                    render_box(
                        f"DHKE Key Derivation",
                        f"HKDF-SHA{hash_algo[-3:]} Derive",
                        f"Shared Secret: {args.shared[:32]}...",
                        derived,
                        {"Key Length": f"{args.keylen} bytes", "Hash": hash_algo, "Encoding": enc.upper()},
                    )
                )
                log_history(f"DHKE Derive", args.shared, derived, {"keylen": args.keylen, "hash": hash_algo}, enabled=history_enabled)
                return 0


        if args.command in ("detect", "analyze"):
            results = detect_format(args.text)
            print(render_detection(args.text, results))
            summary = ", ".join(r.format_name for r in results if r.is_match)
            log_history("Format Detection", args.text, summary or "None", enabled=history_enabled)
            return 0

        if args.command == "auto":
            pipeline_res = run_decode_pipeline(args.text, max_depth=args.depth)
            print(render_pipeline_result(pipeline_res))
            log_history(
                "Auto Decode Pipeline",
                args.text,
                pipeline_res.best_branch.final_text,
                {"depth": args.depth, "steps": pipeline_res.total_steps},
                enabled=history_enabled,
            )
            return 0

        if args.command == "history":
            if getattr(args, "clear", False):
                success = clear_history()
                if success:
                    print("\n  [OK] Riwayat analisis lokal berhasil dibersihkan.\n")
                else:
                    print("\n  [Gagal] Tidak dapat menghapus file riwayat.\n")
            else:
                records = read_history(limit=args.limit)
                print("\n" + render_history_list(records))
            return 0

    except CryptoLabError as err:
        print(render_error(err.__class__.__name__, str(err)), file=sys.stderr)
        return 1
    except Exception as err:
        print(render_error("Kesalahan Tak Terduga", str(err)), file=sys.stderr)
        return 2

    return 0
