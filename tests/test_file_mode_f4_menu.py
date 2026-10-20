"""F4 — menu interaktif "Mode File" (tab Simetris) + penjaga "Hash File".

Step F4 of docs/Prompt/mode-file-spec.md. Two things are proven here:

1. ``fn_mode_file`` (item "Mode File" di tab Simetris) enkripsi/dekripsi berkas
   untuk AES-GCM & AES-CBC, SEMUA format, dengan memakai ulang helper
   ``cryptolab.cli.input`` (jalur yang SAMA dengan CLI — bukan logika duplikat).
2. "Hash File" sudah tersedia lewat ``fn_sha3``/``fn_sha512`` (opsi "File"
   memanggil ``hash_file``), jadi F4 TIDAK menambah item baru untuk itu.

Item menu baru mengubah snapshot menu (pengecualian #1). Tes snapshot tab ada di
``tests/test_tahap2_tab_menu.py``.
"""

import hashlib
import os

import pytest

from cryptolab.core.exceptions import InvalidInputError
from cryptolab.interactive.handlers.ctx_symmetric import fn_mode_file
from cryptolab.interactive.handlers.ctx_hashing import fn_sha3
from cryptolab.interactive.tab_menu import CATEGORIES


KEY = "kunci-enambelas!"  # 16 byte
IV = "iv-enam-belas-by"  # 16 byte


@pytest.fixture(autouse=True)
def no_history(monkeypatch):
    """Handler memanggil log_history - matikan agar tes tidak menulis riwayat."""
    from cryptolab.interactive.handlers import ctx_symmetric

    monkeypatch.setattr(ctx_symmetric, "log_history", lambda *a, **k: True)


class FakeCtx:
    """Ctx tiruan: jawaban diambil berurutan dari daftar (pilihan / input)."""

    def __init__(self, answers):
        self._answers = iter(answers)

    def choose(self, label, options, default=1):
        return next(self._answers)

    def ask(self, label, default=None, cast=str, secret=False):
        return cast(next(self._answers))

    def work(self, text, fn):
        return fn()


def _items(label_kategori):
    for name, group in CATEGORIES:
        if name == label_kategori:
            return {label: target for label, target, _tag in group}
    raise AssertionError(f"Kategori {label_kategori} tidak ditemukan")


# ---------------------------------------------------------------------------
# Item menu terdaftar di tab Simetris (dan "Hash File" tidak diduplikasi)
# ---------------------------------------------------------------------------
class TestRegistrasiMenu:
    def test_mode_file_ada_di_tab_simetris(self):
        assert _items("Simetris")["Mode File"] is fn_mode_file

    def test_mode_file_adalah_ctx_fn(self):
        assert getattr(fn_mode_file, "_ctx_fn", False) is True

    def test_hash_file_tidak_diduplikasi(self):
        """Tidak ada item "Hash File" baru; jalur file sudah ada di fn_sha3.

        (Keputusan reviewer: pilihan A — jangan duplikasi logika.)
        """
        for _name, group in CATEGORIES:
            labels = [label for label, _t, _tag in group]
            assert "Hash File" not in labels

    def test_fn_sha3_masih_menyediakan_file(self, tmp_path):
        """Penjaga kontrak: jalur hash berkas lewat menu tetap ada."""
        f = tmp_path / "d.bin"
        f.write_bytes(b"abc")
        res = fn_sha3(FakeCtx(["SHA3-256", "File", str(f)]))
        rows = dict(res.rows)
        assert rows["SHA3-256"] == hashlib.sha3_256(b"abc").hexdigest()


# ---------------------------------------------------------------------------
# Enkripsi/dekripsi berkas lewat menu — semua algoritma & format
# ---------------------------------------------------------------------------
FORMATS = ["hex", "base64", "raw"]

DATA_CASES = [
    (b"", "kosong"),
    (b"A", "satu-byte"),
    (b"A" * 17, "tujuh-belas"),
    (bytes(range(256)) * 40, "non-utf8"),
]


class TestModeFileGcm:
    @pytest.mark.parametrize("fmt", FORMATS)
    @pytest.mark.parametrize("data,label", DATA_CASES, ids=[c[1] for c in DATA_CASES])
    def test_roundtrip_gcm(self, tmp_path, fmt, data, label):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(data)
        ct = tmp_path / f"ct.{fmt}"
        out = tmp_path / "out.bin"

        # op=Enkripsi, algo=AES-GCM, path-in, format, key, path-out
        res_enc = fn_mode_file(
            FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), fmt, KEY, str(ct)])
        )
        assert ct.exists()
        assert dict(res_enc.rows)["Berkas keluaran"] == str(ct)

        # op=Dekripsi, algo, path-in=ct, format, key, path-out
        fn_mode_file(FakeCtx(["Dekripsi", "AES-GCM (AEAD)", str(ct), fmt, KEY, str(out)]))
        assert hashlib.sha256(out.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()


class TestModeFileCbc:
    @pytest.mark.parametrize("fmt", FORMATS)
    @pytest.mark.parametrize("data,label", DATA_CASES, ids=[c[1] for c in DATA_CASES])
    def test_roundtrip_cbc(self, tmp_path, fmt, data, label):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(data)
        ct = tmp_path / f"ct.{fmt}"
        out = tmp_path / "out.bin"

        # op, algo=AES-CBC, path-in, format, key, IV, path-out
        fn_mode_file(FakeCtx(["Enkripsi", "AES-CBC", str(pt), fmt, KEY, IV, str(ct)]))
        assert ct.exists()

        fn_mode_file(FakeCtx(["Dekripsi", "AES-CBC", str(ct), fmt, KEY, str(out)]))
        assert hashlib.sha256(out.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Perilaku berkas: konfirmasi timpa, raw wajib out, D10, path normalisasi
# ---------------------------------------------------------------------------
class TestModeFilePerilaku:
    def test_raw_tanpa_out_ditolak(self, tmp_path):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(b"halo")
        with pytest.raises(InvalidInputError, match="raw butuh"):
            fn_mode_file(FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), "raw", KEY, ""]))

    def test_gcm_biner_tanpa_out_ditolak(self, tmp_path):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(os.urandom(64))
        ct = tmp_path / "ct.hex"
        fn_mode_file(FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), "hex", KEY, str(ct)]))
        with pytest.raises(InvalidInputError, match="biner"):
            fn_mode_file(FakeCtx(["Dekripsi", "AES-GCM (AEAD)", str(ct), "hex", KEY, ""]))

    def test_konfirmasi_timpa_batal_tidak_menulis(self, tmp_path):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(b"halo")
        ct = tmp_path / "ct.hex"
        ct.write_bytes(b"lama")
        # pilihan "Tidak (batalkan)" -> berkas lama tak berubah
        res = fn_mode_file(
            FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), "hex", KEY, str(ct),
                     "Tidak (batalkan)"])
        )
        assert ct.read_bytes() == b"lama"
        assert "Dibatalkan" in dict(res.rows)["Status"]

    def test_konfirmasi_timpa_ya_menimpa(self, tmp_path):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(b"halo")
        ct = tmp_path / "ct.hex"
        ct.write_bytes(b"lama")
        fn_mode_file(
            FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), "hex", KEY, str(ct),
                     "Ya (timpa)"])
        )
        assert ct.read_bytes() != b"lama"

    def test_path_dengan_kutip_dibersihkan(self, tmp_path):
        """Path yang diseret ke terminal (dibungkus kutip) tetap bisa dibaca."""
        pt = tmp_path / "pt.txt"
        pt.write_bytes(b"halo dunia")
        quoted = f'"{pt}"'
        res = fn_mode_file(FakeCtx(["Enkripsi", "AES-GCM (AEAD)", quoted, "hex", KEY, ""]))
        rows = dict(res.rows)
        # Dibaca sebagai file yang sama -> 10 byte
        assert "(10 byte)" in rows["Berkas masukan"]

    def test_berkas_tidak_ada_galat_ramah(self, tmp_path):
        with pytest.raises(InvalidInputError, match="tidak ditemukan"):
            fn_mode_file(
                FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(tmp_path / "nope"), "hex", KEY, ""])
            )

    def test_gcm_kunci_salah_pesan_autentikasi(self, tmp_path):
        pt = tmp_path / "pt.bin"
        pt.write_bytes(b"halo")
        ct = tmp_path / "ct.hex"
        fn_mode_file(FakeCtx(["Enkripsi", "AES-GCM (AEAD)", str(pt), "hex", KEY, str(ct)]))
        with pytest.raises(InvalidInputError, match="Autentikasi gagal"):
            fn_mode_file(
                FakeCtx(["Dekripsi", "AES-GCM (AEAD)", str(ct), "hex", "kunci-salah-16b!", ""])
            )


# ---------------------------------------------------------------------------
# Ctrl+C / input kosong tidak boleh traceback (lewat run_action)
# ---------------------------------------------------------------------------
class TestModeFileCtrlC:
    def test_ctrl_c_di_input_kembali_tanpa_traceback(self, monkeypatch):
        """Ctx nyata melempar Cancelled saat input EOF; run_action menangkapnya."""
        from cryptolab.flow import Ctx, run_action, Cancelled

        def boom(*_a, **_k):
            raise Cancelled()

        monkeypatch.setattr(Ctx, "choose", boom)
        # run_action mengembalikan "back" (bukan raise) saat Cancelled.
        assert run_action("Mode File", fn_mode_file, lambda: "esc") == "back"
