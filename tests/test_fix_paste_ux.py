"""Regresi perbaikan UX & input (branch fix/paste-multiline-and-ux).

Mengunci empat perbaikan:
1. ``Ctx.choose`` memberi pesan ramah untuk input non-angka (bukan
   ``invalid literal for int()...``).
2. Input multi-baris (paste) tidak bocor ke prompt berikutnya.
3. ``Message.print_warning`` benar-benar mencetak (dulu handler memanggil
   ``Message.warning`` yang hanya mengembalikan string, lalu dibuang).
4. ``hex_decode`` memberi pesan ramah untuk prefix '0x' per byte, tanpa
   mengubah perilaku lama.
"""

import subprocess
import sys

import pytest

from cryptolab import hex_decode
from cryptolab.core.exceptions import DecodingError
from cryptolab.flow import Ctx, _drain_extra_lines


# ============================================================
# 1. Pesan ramah di Ctx.choose
# ============================================================
class TestChoosePesanRamah:
    def _ctx_dengan_input(self, values, monkeypatch):
        it = iter(values)
        # Mock lapisan baca baris (bukan builtins.input), karena _read_line
        # memilih jalur TTY/non-TTY secara internal.
        monkeypatch.setattr("cryptolab.flow._read_line", lambda prompt, secret: next(it))
        ctx = Ctx("Tes")
        pesan = []
        monkeypatch.setattr(ctx, "_error", lambda m: pesan.append(m))
        return ctx, pesan

    def test_input_bukan_angka_tidak_bocorkan_pesan_teknis(self, monkeypatch):
        ctx, pesan = self._ctx_dengan_input(["abc", "2"], monkeypatch)
        hasil = ctx.choose("Pilih", ["A", "B"])
        assert hasil == "B"
        assert not any("invalid literal" in m for m in pesan)
        assert any("angka pilihan" in m for m in pesan)

    def test_angka_di_luar_rentang(self, monkeypatch):
        ctx, pesan = self._ctx_dengan_input(["99", "1"], monkeypatch)
        hasil = ctx.choose("Pilih", ["A", "B"])
        assert hasil == "A"
        assert any("1-2" in m for m in pesan)

    def test_input_valid_langsung(self, monkeypatch):
        ctx, pesan = self._ctx_dengan_input(["2"], monkeypatch)
        assert ctx.choose("Pilih", ["A", "B"]) == "B"
        assert pesan == []


# ============================================================
# 2. Paste multi-baris tidak bocor
# ============================================================
class TestPasteMultiBaris:
    def test_drain_mengembalikan_nol_saat_bukan_tty(self):
        # Di bawah pytest, stdin bukan TTY -> tidak ada yang perlu dikuras.
        assert _drain_extra_lines() == 0

    def test_pipe_hanya_mengambil_satu_baris_per_prompt(self):
        """Regresi: dulu seluruh isi pipe terbaca prompt berikutnya."""
        kode = (
            "import sys; sys.path.insert(0, 'src');"
            "from cryptolab.flow import Ctx;"
            "c = Ctx('T');"
            "a = c.ask('P1');"
            "b = c.ask('P2');"
            "print('HASIL1=%r HASIL2=%r' % (a, b))"
        )
        p = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", kode],
            input="satu\ndua\n",
            capture_output=True,
            text=True,
        )
        assert "HASIL1='satu'" in p.stdout
        assert "HASIL2='dua'" in p.stdout

    def test_paste_berlebih_dibuang_tidak_bocor(self):
        """Paste 3 baris padahal hanya 1 pertanyaan: sisanya diabaikan."""
        kode = (
            "import sys; sys.path.insert(0, 'src');"
            "from cryptolab.flow import Ctx;"
            "c = Ctx('T');"
            "a = c.ask('P1');"
            "print('HASIL=%r' % a)"
        )
        p = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", kode],
            input="baris1\nbaris2\nbaris3\n",
            capture_output=True,
            text=True,
        )
        assert "HASIL='baris1'" in p.stdout


# ============================================================
# 3. Message.print_warning benar-benar mencetak
# ============================================================
class TestWarningTerCetak:
    def test_warning_mengembalikan_string_tanpa_mencetak(self, capsys):
        from cryptolab.ui import Message

        hasil = Message.warning("Data kosong")
        assert "Data kosong" in hasil
        assert capsys.readouterr().out == ""

    def test_print_warning_mencetak_ke_stdout(self, capsys):
        from cryptolab.ui import Message

        Message.print_warning("Data kosong")
        assert "Data kosong" in capsys.readouterr().out

    def test_handler_tidak_lagi_memanggil_warning_tanpa_print(self):
        """Semua pemanggilan di handler harus memakai print_warning."""
        import re
        from pathlib import Path

        akar = Path(__file__).resolve().parent.parent / "src" / "cryptolab" / "interactive" / "handlers"
        pola = re.compile(r"Message\.warning\(")
        pelanggar = []
        for f in akar.glob("*.py"):
            for i, baris in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if pola.search(baris):
                    pelanggar.append(f"{f.name}:{i}")
        assert pelanggar == [], f"masih memakai Message.warning: {pelanggar}"

    def test_handler_memakai_print_warning(self):
        from pathlib import Path

        akar = Path(__file__).resolve().parent.parent / "src" / "cryptolab" / "interactive" / "handlers"
        total = sum(
            f.read_text(encoding="utf-8").count("Message.print_warning(")
            for f in akar.glob("*.py")
        )
        assert total > 0


# ============================================================
# 4. Prefix 0x pada hex_decode
# ============================================================
class TestPrefix0xRamah:
    def test_prefix_di_awal_tetap_didukung(self):
        # Perilaku lama: '0x' tunggal di awal tetap dibuang.
        assert hex_decode("0x48656c6c6f") == "Hello"

    def test_prefix_per_byte_ditolak_dengan_pesan_ramah(self):
        with pytest.raises(DecodingError) as exc:
            hex_decode("0x48 0x69")
        pesan = str(exc.value)
        assert "0x" in pesan
        assert "Hapus" in pesan  # ada arahan solusi
        assert "tidak valid: x" not in pesan  # bukan pesan teknis lama

    def test_karakter_asing_tetap_pesan_lama(self):
        with pytest.raises(DecodingError) as exc:
            hex_decode("4865ZZ")
        assert "tidak valid" in str(exc.value)
        assert "Z" in str(exc.value)

    def test_hex_polos_tetap_berhasil(self):
        assert hex_decode("48656c6c6f") == "Hello"
