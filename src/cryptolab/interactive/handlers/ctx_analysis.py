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

    # Jika ada kemungkinan cipher berkunci, tanya kunci
    if getattr(report, "possible_keyed_ciphers", False) or (
        hasattr(report, "confidence") and report.confidence < 0.5
    ):
        key = ctx.ask("Kunci (kosong = lewati)", default="")
        iv = ctx.ask("IV / Nonce (kosong = lewati)", default="")
        if key:
            report = ctx.work(
                "Menganalisis dengan kunci",
                lambda: run_auto_analysis(
                    ciphertext,
                    **{"key": key, **(({"iv": iv}) if iv else {})},
                ),
            )

    rows = []
    # Kandidat terbaik
    candidates = getattr(report, "candidates", []) or []
    if candidates:
        best = candidates[0]
        rows.append(("Format", getattr(best, "format", "-")))
        rows.append(("Hasil", getattr(best, "decoded", "-")))
        rows.append(("Skor", f"{getattr(best, 'score', 0):.2f}"))
        # Alternatif
        for i, alt in enumerate(candidates[1:4], 2):
            rows.append((f"Alt {i}", getattr(alt, "format", "-") + ": " + str(getattr(alt, "decoded", "-"))[:60]))
    else:
        rows.append(("Hasil", getattr(report, "summary", "Tidak ada kandidat yang ditemukan")))

    summary = rows[1][1] if len(rows) > 1 else "-"
    log_history("Auto Analyze", ciphertext, summary, {"candidates": len(candidates)})
    return Result(rows, note=getattr(report, "note", "") or "")


fn_auto._ctx_fn = True
