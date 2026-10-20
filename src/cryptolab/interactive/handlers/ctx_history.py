"""History ctx handler: lihat dan bersihkan riwayat.

Riwayat TIDAK menggunakan spinner karena pembacaan sangat cepat.
"""

from cryptolab.flow import Result
from cryptolab.core.utils.history import read_history, clear_history


def fn_history(ctx):
    """Tampilkan riwayat operasi; tawarkan opsi bersihkan."""
    records = read_history(limit=20)

    rows = []
    if not records:
        rows.append(("Info", "Belum ada riwayat operasi."))
    else:
        for i, r in enumerate(reversed(records), 1):
            ts = r.get("timestamp", "-")[:19].replace("T", " ")
            op = r.get("operation", "-")
            inp = str(r.get("input", "-"))[:30]
            out = str(r.get("output", "-"))[:30]
            rows.append((f"#{i:>2} {ts}", f"{op}: {inp} → {out}"))

    aksi = ctx.choose(
        "Tindakan",
        ["Lihat saja (kembali)", "Bersihkan seluruh riwayat"],
        default=1,
    )
    if aksi == "Bersihkan seluruh riwayat":
        konfirmasi = ctx.ask("Ketik 'hapus' untuk konfirmasi", default="")
        if konfirmasi.strip().lower() == "hapus":
            ok = clear_history()
            rows = [("Status", "Riwayat berhasil dihapus." if ok else "Gagal menghapus riwayat.")]
        else:
            rows = [("Status", "Penghapusan dibatalkan.")]

    return Result(rows)


fn_history._ctx_fn = True
