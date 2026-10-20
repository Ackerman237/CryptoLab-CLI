"""History interactive handler."""

from cryptolab.utils.history import log_history, read_history, clear_history, get_history_file
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, navigation_menu,
    BackToMenu,
)


def handle_history() -> None:
    """Interactive handler for viewing and managing local history."""
    while True:
        hist_file = get_history_file()
        records = read_history(limit=20)

        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - RIWAYAT ANALISIS & OPERASI LOKAL")
        print(Rule.heavy())
        print(f"  Lokasi file riwayat : {hist_file}")
        print(f"  Total catatan aktif : {len(records)} operasi terakhir")
        print(Rule.thin())

        if not records:
            print("  Belum ada riwayat operasi yang tersimpan.")
            print(Rule.heavy())
        else:
            print("  Waktu (UTC)          | Operasi                 | Input -> Output")
            print("  " + Rule.thin())
            for r in records:
                time_str = r.get("timestamp", "")[:19].replace("T", " ")
                op_str = r.get("operation", "")[:23]
                inp_str = r.get("input", "")[:14]
                out_str = r.get("output", "")[:16]
                preview = f"{inp_str} -> {out_str}"
                print(f"  {time_str:<20} | {op_str:<23} | {preview}")
            print(Rule.heavy())

        choice = navigation_menu(
            options=["Bersihkan Seluruh Riwayat", "Kembali ke Menu Utama"],
            title="RIWAYAT - PILIH OPSI",
            back_label="Kembali ke Menu Utama",
        )

        if choice is None or choice == 1:
            break
        elif choice == 0:
            confirm = Prompt.ask("Yakin ingin menghapus seluruh riwayat? (y/n) [n]", default="n", allow_back=False).lower()
            if confirm in ("y", "ya", "yes"):
                success = clear_history()
                if success:
                    Message.print_success("Riwayat analisis lokal berhasil dibersihkan")
                else:
                    Message.print_error("Gagal", "Tidak dapat menghapus file riwayat")