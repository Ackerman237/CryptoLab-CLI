"""Result formatters for CLI - uses UI widgets (Panel, Rule, Message)."""

import sys
from typing import List, Dict, Any, Optional

from cryptolab import __version__
from cryptolab.ui import Rule, Panel, Message, Symbol, Color, clip_text
from cryptolab.utils.history import get_history_file
from cryptolab.analysis.brute_force import CaesarCandidate, find_best_candidate
from cryptolab.analysis.detect import DetectionResult
from cryptolab.analysis.auto_decode import AutoDecodeResult
from cryptolab.analysis.pipeline import PipelineResult


def render_box(
    title: str,
    operation: str,
    input_text: str,
    output_text: str,
    params: Optional[dict] = None,
) -> str:
    """Render a clean, screenshot-friendly result box (uses Panel widget)."""
    return Panel.cli_box(title, operation, input_text, output_text, params)


def render_error(title: str, message: str) -> str:
    """Render an error banner (EXACT match to old render_error)."""
    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - ERROR: {title.upper()}",
        Rule.heavy(),
        f"  Pesan Kesalahan : {message}",
        Rule.heavy(),
    ]
    return "\n".join(lines)


def render_brute_force(
    ciphertext: str,
    candidates: List[CaesarCandidate],
    show_best_only: bool = False,
) -> str:
    """Render Caesar candidates in a clean tabular view or best candidate view (EXACT match)."""
    best = find_best_candidate(candidates)

    if show_best_only and best:
        flag_note = " [Pola Flag Ditemukan!]" if best.flag_detected else ""
        lines = [
            Rule.heavy(),
            f"  CRYPTOLAB CLI - CAESAR BRUTE FORCE (KANDIDAT TERBAIK)",
            Rule.heavy(),
            f"  Ciphertext   : {ciphertext}",
            f"  Shift        : {best.shift:02d}",
            f"  Skor Teks    : {best.score:.1f}/100 ({best.score_level}){flag_note}",
            f"  Alasan Skor  : {'; '.join(best.reasons[:3])}",
            Rule.light(),
            "  KANDIDAT TERBAIK:",
            f"  {best.text}",
            Rule.light(),
            "  PERHATIAN PENTING:",
            "  Hasil terbaik didasarkan pada estimasi heuristik keterbacaan teks",
            "  dan belum tentu merupakan plaintext yang benar. Verifikasi konteks!",
            Rule.heavy(),
        ]
        return "\n".join(lines)

    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - CAESAR BRUTE FORCE (26 KANDIDAT)",
        Rule.heavy(),
        f"  Ciphertext : {ciphertext}",
        Rule.light(),
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
        Rule.heavy(),
        "  Catatan: Skor didasarkan pada frekuensi huruf umum (ETAOIN/Vokal).",
        "  Hasil terbaik adalah estimasi heuristik, bukan kepastian mutlak.",
        Rule.heavy(),
    ])
    return "\n".join(lines)


def render_detection(text: str, results: List[DetectionResult]) -> str:
    """Render format detection summary with UTF-8 validity and scoring (EXACT match)."""
    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - ANALISIS DETEKSI FORMAT",
        Rule.heavy(),
        f"  Input Teks  : {text[:60] + ('...' if len(text) > 60 else '')}",
        Rule.light(),
        "  Format      | Status | Keyakinan | UTF-8 | Preview Hasil Dekode",
        "  ------------+--------+-----------+-------+-------------------------",
    ]

    matches_count = sum(1 for r in results if r.is_match)

    for res in results:
        status_str = "MATCH " if res.is_match else "NO    "
        utf8_str = "Ya   " if res.is_valid_utf8 else "Tidak"
        preview = res.preview_decoded if res.preview_decoded else res.details
        if len(preview) > 25:
            preview = preview[:22] + Symbol.ELLIPSIS
        lines.append(
            f"  {res.format_name:<11} | {status_str} | {res.confidence:<9} | {utf8_str} | {preview}"
        )

    lines.extend([
        Rule.heavy(),
        "  HASIL ANALISIS:",
    ] + [
        f"  - [{r.format_name}] {r.details}"
        + (f" (Skor: {r.score:.1f}/100)" if r.is_match and r.is_valid_utf8 else "")
        for r in results
        if r.is_match
    ])

    if matches_count > 1:
        lines.extend([
            Rule.light(),
            f"  CATATAN MULTI-FORMAT: Input cocok dengan {matches_count} format berbeda.",
            "  Pilihlah format yang menghasilkan teks bermakna sesuai konteks lab.",
        ])

    lines.extend([
        Rule.heavy(),
        "  PERHATIAN: Deteksi bersifat heuristik/indikatif dan tidak dijamin",
        "  100% pasti benar. Selalu verifikasi konteks data laboratorium.",
        Rule.heavy(),
    ])
    return "\n".join(lines)


def render_auto_decode(result: AutoDecodeResult) -> str:
    """Render multi-stage auto-decode steps and final result (EXACT match)."""
    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - MULTI-STAGE AUTO-DECODE",
        Rule.heavy(),
        f"  Status       : {result.notes}",
        f"  Total Tahap  : {result.total_steps}",
        Rule.light(),
    ]

    if result.steps:
        for step in result.steps:
            lines.extend([
                f"  [Tahap {step.step_number}] Menggunakan Format: {step.codec_name}",
                f"   - Input  : {step.input_preview}",
                f"   - Output : {step.output_preview}",
                "",
            ])
        lines.append(Rule.light())

    lines.extend([
        "  HASIL AKHIR:",
        f"  {result.final_text}",
        Rule.heavy(),
    ])
    return "\n".join(lines)


def render_pipeline_result(result: PipelineResult) -> str:
    """Render multi-stage pipeline result with branching candidate details (EXACT match)."""
    best = result.best_branch
    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - MULTI-STAGE AUTO-DECODE PIPELINE",
        Rule.heavy(),
        f"  Status       : {result.notes}",
        f"  Total Tahap  : {result.total_steps}",
        f"  Skor Akhir   : {best.score:.1f}/100 ({best.score_level})"
        + (" [FLAG DITEMUKAN!]" if best.flag_detected else ""),
    ]

    if best.reasons:
        lines.append(f"  Indikator    : {'; '.join(best.reasons[:3])}")

    lines.append(Rule.light())

    if best.steps:
        lines.append("  URUTAN TRANSFORMASI TERBAIK:")
        for step in best.steps:
            lines.extend([
                f"  [Tahap {step.step_number}] {step.codec_name}",
                f"   - Input  : {step.input_preview}",
                f"   - Output : {step.output_preview}",
            ])
        lines.append(Rule.light())

    lines.extend([
        "  HASIL AKHIR (KANDIDAT UTAMA):",
        f"  {best.final_text}",
    ])

    if result.alternative_branches:
        lines.extend([
            Rule.light(),
            f"  JALUR ALTERNATIF RELEVAN ({len(result.alternative_branches)} kandidat lain):",
        ])
        for idx, alt in enumerate(result.alternative_branches, start=1):
            transform_chain = " -> ".join(s.codec_name for s in alt.steps)
            lines.append(
                f"  [Alt {idx}] {transform_chain} (Skor: {alt.score:.1f}/100) -> {alt.final_text[:50]}"
            )

    lines.extend([
        Rule.heavy(),
        "  CATATAN: Verifikasi manual disarankan jika hasil berupa kode/flag.",
        Rule.heavy(),
    ])
    return "\n".join(lines)


def render_history_list(records: List[Dict[str, Any]]) -> str:
    """Render table of recent analysis history (EXACT match)."""
    lines = [
        Rule.heavy(),
        f"  CRYPTOLAB CLI - RIWAYAT ANALISIS LOKAL ({get_history_file()})",
        Rule.heavy(),
    ]

    if not records:
        lines.extend([
            "  Belum ada riwayat operasi yang tersimpan.",
            Rule.heavy(),
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
        Rule.heavy(),
        "  Gunakan opsi --clear pada perintah 'history' untuk menghapus log riwayat.",
        Rule.heavy(),
    ])
    return "\n".join(lines)