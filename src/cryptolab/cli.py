"""Command Line Interface and Presentation Layer for CryptoLab."""

import argparse
import sys
from typing import List, Optional, Dict, Any

from cryptolab import __version__
from cryptolab.exceptions import CryptoLabError, InvalidInputError
from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
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
from cryptolab.interactive import run_interactive_menu


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
