"""Logo header: bentuk CRYPTOLAB, kerapian tepi, dan mode ASCII polos.

Regresi: logo lama (LOGO_LARGE) baris pertamanya salah, sehingga tulisan
terbaca sebagai "RYPTOLAB" dan tepi kanan tidak rata. Tes ini mengunci
perbaikan tersebut.
"""

import pytest

from cryptolab import banner as b


class TestBentukLogo:
    @pytest.mark.parametrize(
        "logo",
        [b.LOGO_LARGE, b.LOGO_MEDIUM, b.LOGO_SMALL],
    )
    def test_baris_logo_rata_kiri_dan_kanan(self, logo):
        lines = logo.splitlines()
        assert len(lines) == 5
        # Semua baris punya lebar terlihat sama (tepi kanan rata).
        widths = {b.vlen(l) for l in lines}
        assert len(widths) == 1, f"lebar baris tidak seragam: {widths}"
        # Tepi kiri: beda lekukan antar huruf maksimal 1 kolom (bentuk glyph
        # Y/T/A memang menjorok), jadi blok tidak terlihat bergerigi.
        lefts = {len(l) - len(l.lstrip(" ")) for l in lines}
        assert max(lefts) - min(lefts) <= 1, f"lekukan tepi kiri: {lefts}"

    @pytest.mark.parametrize(
        "logo",
        [b.LOGO_LARGE, b.LOGO_MEDIUM, b.LOGO_SMALL],
    )
    def test_baris_pertama_memuat_huruf_c_utuh(self, logo):
        # Huruf C = 6 kolom terisi pada baris atas, di awal logo.
        first = logo.splitlines()[0]
        assert first.startswith("██████ ")

    def test_huruf_pertama_bukan_yang_dimulai_spasi(self):
        # Regresi: logo lama dimulai spasi lalu blok, sehingga terbaca
        # "RYPTOLAB" karena huruf C tampak terpotong.
        for logo in (b.LOGO_LARGE, b.LOGO_MEDIUM, b.LOGO_SMALL):
            assert not logo.startswith(" ")

    def test_huruf_r_punya_bahu_seperti_p(self):
        # Regresi: baris tengah R dulu "██  ██" sehingga R terlihat seperti A.
        # Bahu R harus "█████ " (tertutup) pada baris ke-3 semua logo.
        for logo in (b.LOGO_LARGE, b.LOGO_MEDIUM, b.LOGO_SMALL):
            baris3 = logo.splitlines()[2]
            assert baris3[7:13] == "█████ ", f"bahu R salah: {baris3[7:13]!r}"

    def test_huruf_r_dan_a_berbeda(self):
        # R: bahu lurus (█████ ) - A: bahu penuh (██████).
        for logo in (b.LOGO_LARGE, b.LOGO_MEDIUM, b.LOGO_SMALL):
            baris3 = logo.splitlines()[2]
            assert baris3[7:13] != "██████"

    def test_lebar_menurun_tiap_tingkat(self):
        assert b._block_width(b.LOGO_LARGE) > b._block_width(b.LOGO_MEDIUM)
        assert b._block_width(b.LOGO_MEDIUM) > b._block_width(b.LOGO_SMALL)

    def test_sembilan_huruf_terbaca_dari_jarak_antar_huruf(self):
        # CRYPTOLAB = 9 huruf -> 8 kolom jarak pada baris teratas.
        first = b.LOGO_LARGE.splitlines()[0]
        assert first.count(" ") >= 8


class TestCenterBlock:
    def test_lebar_terlihat_seragam_setelah_dipusatkan(self):
        out = b.center_block(b.LOGO_LARGE, 80).splitlines()
        assert len({b.vlen(l) for l in out}) == 1

    def test_lekukan_tepi_kiri_maksimal_satu_kolom(self):
        out = b.center_block(b.LOGO_LARGE, 80).splitlines()
        lefts = {len(l) - len(l.lstrip(" ")) for l in out}
        assert max(lefts) - min(lefts) <= 1

    def test_blok_tidak_terpotong_di_lebar_kecil(self):
        out = b.center_block(b.LOGO_SMALL, 80).splitlines()
        assert all(l.startswith(" " * 20) for l in out[:1])


class TestPickLogo:
    def test_lebar_sempit_jatuh_ke_tiny(self):
        assert b.pick_logo(10) == b.LOGO_TINY

    def test_tinggi_kecil_jatuh_ke_tiny(self):
        assert b.pick_logo(120, max_rows=1) == b.LOGO_TINY

    def test_lebar_besar_memilih_logo_terbesar(self):
        assert b.pick_logo(120) == b.LOGO_LARGE


class TestModeAscii:
    def test_set_ascii_logo_mengganti_pilihan(self):
        b.set_ascii_logo(True)
        try:
            assert b.ascii_logo_enabled()
            picked = b.pick_logo(120)
            assert "█" not in picked
            assert "CRYPTOLAB" not in picked  # digambar dengan ASCII, bukan teks biasa
        finally:
            b.set_ascii_logo(False)

    def test_ascii_tidak_memakai_glyph_blok(self):
        for logo in (b.LOGO_ASCII, b.LOGO_ASCII_MEDIUM):
            assert "█" not in logo

    def test_env_var_mengaktifkan_ascii(self, monkeypatch):
        import importlib

        monkeypatch.setenv("CRYPTOLAB_ASCII_LOGO", "1")
        mod = importlib.reload(b)
        try:
            assert mod.ascii_logo_enabled()
            assert "█" not in mod.pick_logo(120)
        finally:
            monkeypatch.delenv("CRYPTOLAB_ASCII_LOGO", raising=False)
            importlib.reload(b)

    def test_reset_kembali_ke_blok(self):
        b.set_ascii_logo(True)
        b.set_ascii_logo(False)
        assert not b.ascii_logo_enabled()
        assert b.pick_logo(120) == b.LOGO_LARGE


class TestRenderHeader:
    def test_header_memuat_subtitle_versi(self):
        out = b.render_header(b.HEADER_SUBTITLE)
        assert "CRYPTOLAB CLI v" in out
        assert b.APP_VERSION in out

    def test_header_ascii_mode_tetap_rapi(self):
        b.set_ascii_logo(True)
        try:
            out = b.render_header(b.HEADER_SUBTITLE)
            assert "█" not in out
            assert "CRYPTOLAB CLI v" in out
        finally:
            b.set_ascii_logo(False)

    def test_subtitle_diredupkan_logo_ditebalkan(self):
        # Hierarki visual: logo BOLD+WHITE, subtitle grey - harus beda gaya.
        out = b.render_header(b.HEADER_SUBTITLE)
        lines = out.split("\n")
        logo_line = next(l for l in lines if "█" in l)
        sub_line = next(l for l in lines if "CRYPTOLAB CLI v" in l)
        assert b.BOLD in logo_line and b.WHITE in logo_line
        assert b.GREY in sub_line
        assert b.BOLD not in sub_line and b.WHITE not in sub_line


class TestFormatSubtitle:
    def test_subtitle_final_tidak_menyisakan_placeholder(self):
        # Regresi: HEADER_SUBTITLE pernah jadi template mentah sehingga
        # render_header menampilkan "{version}" apa adanya.
        assert "{" not in b.HEADER_SUBTITLE
        assert b.APP_VERSION in b.HEADER_SUBTITLE

    def test_template_dan_hasil_final_sama(self):
        assert b.format_subtitle() == b.HEADER_SUBTITLE

    def test_tanpa_dev_saat_versi_sama_dengan_rilis(self):
        out = b.format_subtitle(dev=False)
        assert "(dev)" not in out
        assert "CRYPTOLAB CLI v" in out

    def test_dengan_dev_saat_diminta(self):
        out = b.format_subtitle(dev=True)
        assert out.endswith("(dev)")

    def test_versi_kustom_dipakai(self):
        assert "v9.9.9" in b.format_subtitle(version="9.9.9")

    def test_dev_otomatis_dari_perbandingan_versi(self):
        # Versi lokal == rilis terakhir -> bukan build pengembangan.
        assert b.development_build() is False


class TestCliFlag:
    def test_parser_menerima_ascii_logo(self):
        from cryptolab.cli import create_parser

        args = create_parser().parse_args(["--ascii-logo"])
        assert args.ascii_logo is True

    def test_default_tanpa_flag(self):
        from cryptolab.cli import create_parser

        args = create_parser().parse_args([])
        assert args.ascii_logo is False


class TestThemeSinkron:
    """Regresi: ui/theme.py punya salinan logo sendiri yang menyimpang dari
    banner.py (huruf C hilang). Sekarang theme harus memakai sumber yang sama."""

    def test_logo_blok_identik_dengan_banner(self):
        from cryptolab.ui import theme as t

        # theme memilih varian sesuai dukungan Unicode terminal; bandingkan
        # terhadap varian yang sama di banner, bukan selalu versi blok.
        pairs = (
            ("LOGO_LARGE", b.LOGO_LARGE),
            ("LOGO_MEDIUM", b.LOGO_MEDIUM),
            ("LOGO_SMALL", b.LOGO_SMALL),
        )
        for name, expected in pairs:
            got = getattr(t, name)
            # theme boleh jatuh ke ASCII di non-TTY; itu tetap harus salah satu
            # varian resmi dari banner (tidak boleh salinan mandiri).
            assert got.splitlines() in (
                expected.splitlines(),
                b.LOGO_ASCII.splitlines(),
                b.LOGO_ASCII_MEDIUM.splitlines(),
            ), name

    def test_logo_small_tersedia(self):
        from cryptolab.ui import theme as t

        assert hasattr(t, "LOGO_SMALL")

    def test_pick_logo_theme_menghormati_mode_ascii(self):
        from cryptolab.ui import theme as t

        b.set_ascii_logo(True)
        try:
            assert "█" not in t.pick_logo(120)
        finally:
            b.set_ascii_logo(False)

    def test_pick_logo_theme_lebar_sempit(self):
        from cryptolab.ui import theme as t

        assert t.pick_logo(5) == t.LOGO_TINY
