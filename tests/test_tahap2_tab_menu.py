"""Tahap 2 - menu tab kategori (upgrade-spec.md).

Tes navigasi menu tab (wrap-around, angka lompat, tag, mode sempit),
item tanpa handler (mode Tahap 3), dan fallback menu lama non-TTY.
"""

import sys

from cryptolab.interactive.tab_menu import (
    CATEGORIES,
    run_tab_menu,
    tab_menu_lines,
)


def _run(keys, capsys=None):
    """Jalankan loop tab dengan kunci tiruan; kembalikan (daftar_panggilan, out)."""
    calls = []
    it = iter(list(keys) + ["q"])  # q penutup: loop hanya keluar via q/esc

    def fake_read_key(*_a, **_k):
        try:
            return next(it)
        except StopIteration:
            raise AssertionError("Kunci skrip habis sebelum menu keluar")

    def fake_dispatch(label, target):
        calls.append((label, target))
        return False

    run_tab_menu(fake_dispatch, fake_read_key)
    out = capsys.readouterr().out if capsys else ""
    return calls, out


class TestNavigasiTab:
    def test_enter_pilih_item_pertama(self):
        calls, _ = _run(["enter"])
        assert [c[0] for c in calls] == ["Caesar Cipher"]

    def test_panah_kanan_kategori_targetnya_item_pertama(self):
        calls, _ = _run(["right", "enter"])
        assert [c[0] for c in calls] == ["AES"]

    def test_wrap_kiri_dari_kategori_pertama(self):
        calls, _ = _run(["left", "enter"])
        assert [c[0] for c in calls] == ["Auto Analyze"]

    def test_wrap_kanan_dari_kategori_terakhir(self):
        # Utilitas (6) -> wrap ke Klasik (1)
        calls, _ = _run(["right", "right", "right", "right", "right", "right", "enter"])
        assert [c[0] for c in calls] == ["Caesar Cipher"]

    def test_panah_atas_wrap_ke_item_terakhir(self):
        calls, _ = _run(["up", "enter"])
        assert [c[0] for c in calls] == ["Vigenere Cipher"]

    def test_panah_bawah_wrap_ke_item_pertama(self):
        # Klasik punya 2 item: down, down -> wrap balik ke atas.
        calls, _ = _run(["down", "down", "enter"])
        assert [c[0] for c in calls] == ["Caesar Cipher"]

    def test_angka_lompat_kategori(self):
        calls, _ = _run(["3", "enter"])
        assert [c[0] for c in calls] == ["RSA"]
        calls, _ = _run(["6", "enter"])
        assert [c[0] for c in calls] == ["Auto Analyze"]

    def test_angka_di_luar_rentang_diabaikan(self):
        calls, _ = _run(["9", "enter"])
        assert [c[0] for c in calls] == ["Caesar Cipher"]

    def test_q_dan_esc_keluar_tanpa_dispatch(self):
        calls, _ = _run(["q"])
        assert calls == []
        calls, _ = _run(["esc"])
        assert calls == []

    def test_kunci_lain_diabaikan(self):
        # home/pgup/dst tidak mengubah pilihan.
        calls, _ = _run(["home", "pgup", "enter"])
        assert [c[0] for c in calls] == ["Caesar Cipher"]


class TestItemBaruTahap3:
    def test_semua_item_sudah_punya_handler(self):
        # Semua mode Tahap 3 sudah punya handler (Argon2id/bcrypt didegradasi
        # ke bcrypt/PBKDF2-SHA256 di fn_password).
        tanpa_handler = [
            f"{name}/{label}"
            for name, group in CATEGORIES
            for label, target, _tag in group
            if target is None
        ]
        assert tanpa_handler == []

    def test_tanpa_handler_tidak_ada_cabang_status_lagi(self):
        # Tombol Enter selalu dispatch selama item punya handler.
        calls, _ = _run(["4", "down", "down", "down", "down", "enter"])
        assert [c[0] for c in calls] == ["Argon2id / bcrypt"]


class TestTampilan:
    def test_baris_memuat_tab_aktif_dan_footer(self):
        lines = "\n".join(tab_menu_lines(0, 0))
        assert "[Klasik]" in lines
        assert "Caesar Cipher" in lines
        assert "Enter pilih" in lines

    def test_header_logo_dan_versi(self):
        lines = "\n".join(tab_menu_lines(0, 0))
        assert "CRYPTOLAB CLI v" in lines
        assert any("█" in l for l in tab_menu_lines(0, 0))

    def test_penjelasan_kategori_ikut_tab_aktif(self):
        assert "substitusi dan pergeseran" in "\n".join(tab_menu_lines(0, 0))
        assert "integritas, MAC, dan password" in "\n".join(tab_menu_lines(3, 0))

    def test_muatan_tinggi_terminal_kecil(self, monkeypatch):
        from cryptolab.interactive import tab_menu as tm
        monkeypatch.setattr(tm, "term_height", lambda default=24: 14)
        lines = tm.tab_menu_lines(3, 1)
        assert len(lines) <= 14
        assert any("Enter pilih" in l for l in lines)  # footer selalu ada

    def test_tinggi_sangat_kecil_masih_ada_tab_dan_footer(self, monkeypatch):
        from cryptolab.interactive import tab_menu as tm
        monkeypatch.setattr(tm, "term_height", lambda default=24: 8)
        lines = tm.tab_menu_lines(3, 1)
        assert any("[Hash]" in l for l in lines)
        assert any("Enter pilih" in l for l in lines)

    def test_tag_baru_dan_usang(self):
        lines = "\n".join(tab_menu_lines(1, 0))  # Simetris
        assert "AES-GCM" in lines and "baru" in lines
        assert "DES" in lines and "usang" in lines

    def test_mode_sempit_hanya_tab_aktif(self, monkeypatch):
        from cryptolab.interactive import tab_menu as tm
        monkeypatch.setattr(tm, "term_width", lambda default=80: 40)
        bar = next(l for l in tm.tab_menu_lines(1, 0) if "[Simetris]" in l)
        assert "(2/6)" in bar
        from cryptolab.banner import vlen
        assert vlen(bar) <= 40


class TestIntegrasiRunInteractiveMenu:
    @staticmethod
    def _press(monkeypatch, *keys):
        import readchar
        it = iter(keys)
        monkeypatch.setattr(readchar, "readkey", lambda *a, **k: next(it))

    def test_tty_memakai_menu_tab_dan_tetap_sapa(self, capsys, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        self._press(monkeypatch, "q")
        from cryptolab.interactive import run_interactive_menu
        run_interactive_menu()
        out = capsys.readouterr().out
        assert "[Klasik]" in out          # tab menu tampil
        assert "Sampai jumpa" in out      # pesan perpisahan tetap ada

    def test_non_tty_fallback_menu_lama(self, capsys, monkeypatch):
        # stdout/stdin pytest bukan TTY -> menu lama (dipertahankan apa adanya).
        self._press(monkeypatch, "q")
        from cryptolab.interactive import run_interactive_menu
        run_interactive_menu()
        out = capsys.readouterr().out
        assert "[Klasik]" not in out
        assert "Sampai jumpa" in out
