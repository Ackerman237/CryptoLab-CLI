"""Analysis ctx handler: Auto Analyze.

Logika analisis TIDAK diubah - hanya lapisan UI diganti ke ctx API.
"""

from cryptolab.flow import Result
from cryptolab.core.analysis.auto_engine import run_auto_analysis
from cryptolab.core.utils.history import log_history


def fn_auto(ctx):
    """Auto Analyze: deteksi otomatis jenis cipher / encoding dari teks."""
    ciphertext = ctx.ask("Teks / Ciphertext")

    # Jalankan analisis tanpa kunci dulu
    report = ctx.work("Menganalisis teks", lambda: run_auto_analysis(ciphertext))

    # Jika belum ada hasil berkepercayaan tinggi, tawarkan input kunci untuk cipher berkunci
    keyed_ciphers = getattr(report, "possible_keyed_ciphers", []) or []
    has_high_conf = getattr(report, "has_high_confidence", False)

    if not has_high_conf:
        if keyed_ciphers:
            hint = f"Kunci cipher ({', '.join(keyed_ciphers)}) [kosong = lewati]"
        else:
            hint = "Kunci cipher (kosong = lewati)"

        key = ctx.ask(hint, default="")
        if key:
            iv = ""
            if any(c in keyed_ciphers for c in ("AES", "DES", "RC2")) or len(key.encode("utf-8")) in (8, 16):
                iv = ctx.ask("IV / Nonce (kosong = lewati)", default="")
            report = ctx.work(
                "Menganalisis dengan kunci",
                lambda: run_auto_analysis(
                    ciphertext,
                    key=key,
                    iv=iv if iv else None,
                ),
            )

    rows = []
    candidates = getattr(report, "candidates", []) or []
    top = getattr(report, "top_candidate", None) or (candidates[0] if candidates else None)

    if top:
        rows.append(("Metode", getattr(top, "method", "-")))
        rows.append(("Kategori", getattr(top, "category", "-")))
        rows.append(("Status", getattr(top, "status", "-")))
        score_val = getattr(top, "score", 0.0)
        score_lvl = getattr(top, "score_level", "")
        score_str = f"{score_val:.1f}/100" + (f" ({score_lvl})" if score_lvl else "")
        rows.append(("Skor", score_str))
        if getattr(top, "flag_detected", False):
            rows.append(("Flag", "Pola format flag terdeteksi!"))
        rows.append(("Hasil", getattr(top, "output_text", "-")))
        if getattr(top, "reasons", None):
            rows.append(("Alasan", "; ".join(top.reasons[:2])))

        # Alternatif kandidat lain jika ada
        alt_candidates = [c for c in candidates if c != top]
        for i, alt in enumerate(alt_candidates[:3], 2):
            preview = getattr(alt, "output_text", "").replace("\n", " ").strip()
            if len(preview) > 50:
                preview = preview[:47] + "..."
            rows.append((f"Alt {i}", f"[{getattr(alt, 'method', '-')}] {preview} (skor {getattr(alt, 'score', 0):.1f})"))
    else:
        notes_text = getattr(report, "notes", "") or "Tidak ada kandidat decoding/dekripsi yang valid ditemukan."
        rows.append(("Hasil", notes_text))

    summary = getattr(top, "output_text", "-") if top else (getattr(report, "notes", "-") or "-")
    method_name = getattr(top, "method", "-") if top else "-"
    log_history("Auto Analyze", ciphertext, summary, {"candidates": len(candidates), "method": method_name})
    return Result(rows, note=getattr(report, "notes", "") or "")


fn_auto._ctx_fn = True

