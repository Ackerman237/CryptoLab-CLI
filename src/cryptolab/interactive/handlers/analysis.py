"""Analysis interactive handlers (Auto Analyze)."""

from typing import List, Optional

from cryptolab.analysis.auto_engine import run_auto_analysis, AutoAnalysisReport, AutoCandidate
from cryptolab.analysis.brute_force import caesar_brute_force, find_best_candidate, CaesarCandidate

from cryptolab.exceptions import CryptoLabError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, navigation_menu,
    BackToMenu,
)


def handle_auto_analyze() -> None:
    """Interactive handler for Auto Analyze feature."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - AUTO ANALYZE (DETEKSI & ANALISIS CERDAS)")
        print(Rule.heavy())
        print("  Fitur ini otomatis mendeteksi encoding (Base64, Hex, Binary),")
        print("  menguji decoding bertingkat, dan mencoba Caesar brute-force.")
        print("  Ketik 'b' untuk kembali ke menu utama kapan saja.")
        print(Rule.thin())

        try:
            ciphertext = Prompt.ask("Masukkan ciphertext atau data yang ingin dianalisis")
            if not ciphertext:
                Message.warning("Input tidak boleh kosong")
                continue

            print("\n  [*] Menganalisis format encoding (Base64, Hex, Binary)...")
            print("  [*] Menguji pipeline decoding bertingkat...")
            print("  [*] Menguji Caesar brute-force (26 kemungkinan shift)...")

            # First run keyless analysis
            report: AutoAnalysisReport = run_auto_analysis(ciphertext)

            user_key: Optional[str] = None
            user_iv: Optional[str] = None

            # Check if keyed cipher is possible or confidence is low
            if report.possible_keyed_ciphers or not report.has_high_confidence:
                print(Rule.thin())
                if report.possible_keyed_ciphers:
                    keyed_list = ", ".join(report.possible_keyed_ciphers)
                    Message.warning(f"Karakteristik data cocok dengan cipher ber-kunci ({keyed_list})")

                key_input = Prompt.ask(
                    "Metode ini mungkin membutuhkan key. Masukkan key jika tersedia, atau Enter untuk melewati",
                    allow_empty=True,
                )
                if key_input:
                    user_key = key_input
                    key_bytes_len = len(user_key.encode("utf-8"))

                    # AES uses a 16-byte key; DES and RC2 use an 8-byte key.
                    if key_bytes_len == 16 and (
                        "AES" in report.possible_keyed_ciphers or not report.possible_keyed_ciphers
                    ):
                        iv_input = Prompt.ask(
                            "Metode AES CBC membutuhkan IV (16 byte). Masukkan IV jika ada, atau Enter untuk mode ECB",
                            allow_empty=True,
                        )
                        if iv_input:
                            iv_bytes_len = len(iv_input.encode("utf-8"))
                            if iv_bytes_len != 16:
                                Message.warning(f"Panjang IV AES CBC harus tepat 16 byte. Melewati CBC ber-IV.")
                            else:
                                user_iv = iv_input

                    elif key_bytes_len == 8 and (
                        "DES" in report.possible_keyed_ciphers or "RC2" in report.possible_keyed_ciphers
                    ):
                        iv_input = Prompt.ask(
                            "Metode DES/RC2 CBC membutuhkan IV (8 byte). Masukkan IV jika ada, atau Enter untuk mode ECB saja",
                            allow_empty=True,
                        )
                        if iv_input:
                            iv_bytes_len = len(iv_input.encode("utf-8"))
                            if iv_bytes_len != 8:
                                Message.warning(f"Panjang IV DES CBC harus tepat 8 byte. Melewati CBC ber-IV.")
                            else:
                                user_iv = iv_input

                    elif "AES" in report.possible_keyed_ciphers:
                        Message.warning(f"Panjang key AES-128 harus tepat 16 byte (saat ini: {key_bytes_len}).")

                    # Re-run analysis with supplied parameters
                    report = run_auto_analysis(ciphertext, key=user_key, iv=user_iv)

            # Display results
            top = report.top_candidate
            if top:
                card = Panel.result(
                    title="HASIL ANALISIS CRYPTOLAB",
                    method=top.method,
                    operation=top.operation,
                    status=top.status,
                    input_text=ciphertext,
                    output_text=top.output_text,
                    reasons=top.reasons,
                    extra_fields={
                        "Kategori": top.category,
                        "Skor Teks": f"{top.score:.1f}/100 ({top.score_level})",
                    },
                )
                Panel.display(card)

                # Show alternative candidates if available
                alt_candidates = [c for c in report.candidates if c != top][:4]
                if alt_candidates:
                    print("\n  KANDIDAT ALTERNATIF LAIN:")
                    print("  " + Rule.thin() + Rule.thin())
                    for idx, alt in enumerate(alt_candidates, start=1):
                        flag_mark = " [FLAG!]" if alt.flag_detected else ""
                        prev = alt.output_text[:40] + ("..." if len(alt.output_text) > 40 else "")
                        print(f"  [{idx}] {alt.method} ({alt.category}) | Skor: {alt.score:.1f}/100{flag_mark}")
                        print(f"      Hasil: {prev}")

                print(Rule.thin())
                print(f"  Catatan: {report.notes}")
                print("  Perhatian: Base64/Hex/Binary adalah encoding, bukan enkripsi ber-kunci.")
                print("  Hasil heuristik adalah estimasi terbaik dan perlu diverifikasi dengan konteks.")
                print(Rule.heavy())

                log_history(
                    "Auto Analyze",
                    ciphertext,
                    top.output_text,
                    {"method": top.method, "score": top.score},
                )

                repeat = _post_result_menu(card, "hasil_auto_analyze.txt")
                if not repeat:
                    break
            else:
                Message.warning("Tidak ditemukan kandidat yang menghasilkan teks terbaca")
                Message.warning("Ciphertext mungkin menggunakan key yang belum dimasukkan")
                repeat = _post_result_menu("Tidak ada kandidat.", "hasil_auto_analyze.txt")
                if not repeat:
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _post_result_menu(result_text: str, default_filename: str = "hasil_cryptolab.txt") -> bool:
    """Display post-result options. Returns True if user wants to repeat, False to go back."""
    while True:
        choice = navigation_menu(
            options=[
                "Ulangi proses / Coba data lain",
                "Simpan hasil ke file",
                "Kembali ke menu utama",
            ],
            title="OPSI SETELAH PROSES",
            back_label="Kembali ke menu utama",
            clear_display=False,
        )
        if choice is None or choice == 2:
            return False
        elif choice == 0:
            return True
        elif choice == 1:
            _save_result_prompt(result_text, default_filename)


def _save_result_prompt(content: str, default_filename: str = "hasil_cryptolab.txt") -> None:
    """Prompt user to optionally save text content to a file."""
    try:
        choice = Prompt.ask("Simpan hasil ke file? (y/n) [n]", default="n").lower()
        if choice in ("y", "ya", "yes"):
            fn_input = Prompt.ask(f"Nama file [{default_filename}]", default=default_filename)
            filename = fn_input or default_filename
            from pathlib import Path
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")
            Message.success("Hasil berhasil disimpan", str(filepath.resolve()))
    except Exception as err:
        Message.error("Gagal menyimpan file", str(err))