"""Bukti penempatan field D11: kenapa raw_bytes harus sebelum field berdefault.

Dirujuk oleh docs/Prompt/mode-file-spec.md §3.1.

BATAS BUKTI (penting):
  - Bagian "semantik Python" memakai dataclass TIRUAN. Tujuannya membuktikan
    aturan urutan field dataclass, bukan menguji AesGcmResult asli.
  - Bagian "kelas nyata" hanya memverifikasi bahwa AesGcmResult bisa di-import
    dan urutan field-nya konsisten. Sebelum F0b, ini TIDAK membuktikan apa-apa:
    kelas yang bisa di-import pasti lolos karena dataclass sendiri menolak
    field non-default setelah field berdefault.
  - Bukti NYATA untuk D11 adalah tes F0b (tests/test_tahap3_modes.py).

STATUS: skrip sementara. Setelah F0b selesai, HAPUS skrip ini atau LIPAT
isinya ke tests/test_file_mode.py.

Jalankan:
    .venv\\Scripts\\python.exe tests/file_mode/verify_field_placement.py
"""

import dataclasses
import pathlib
import re
import sys
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "src"))


# --------------------------------------------------------------------
# Bagian 1: semantik Python (dataclass tiruan)
# --------------------------------------------------------------------
def cek_opsi_a() -> str:
    try:
        @dataclass
        class A:
            a: str
            b: str = ""
            raw_bytes: bytes  # non-default setelah default

        return "TIDAK error (tak terduga)"
    except TypeError as e:
        return f"TypeError: {e}"


def cek_opsi_b() -> str:
    @dataclass
    class B:
        a: str
        raw_bytes: bytes
        b: str = ""

    b = B(a="x", raw_bytes=b"\x01\x02")
    return f"OK (keyword): raw_bytes={b.raw_bytes!r}"


def cek_opsi_c() -> str:
    @dataclass
    class C:
        a: str
        b: str = ""
        raw_bytes: bytes = b""

    return f"OK (default kosong): C(a='x').raw_bytes={C(a='x').raw_bytes!r}"


# --------------------------------------------------------------------
# Bagian 2: kelas NYATA (AesGcmResult) + pemanggil nyata
# --------------------------------------------------------------------
def cek_kelas_nyata() -> list:
    from cryptolab.core.symmetric.aes import AesGcmResult

    nama_field = [f.name for f in dataclasses.fields(AesGcmResult)]
    berdefault = [
        f.name for f in dataclasses.fields(AesGcmResult)
        if f.default is not dataclasses.MISSING
        or f.default_factory is not dataclasses.MISSING
    ]
    print("  urutan field AesGcmResult:")
    print("   ", nama_field)
    print("  field berdefault:", berdefault)
    print("  raw_bytes sudah ada?", "raw_bytes" in nama_field)

    # Field tanpa default tidak boleh muncul setelah field berdefault.
    idx_default_pertama = next(
        (i for i, f in enumerate(dataclasses.fields(AesGcmResult))
         if f.default is not dataclasses.MISSING
         or f.default_factory is not dataclasses.MISSING),
        len(nama_field),
    )
    non_default_setelah = [
        f.name for f in dataclasses.fields(AesGcmResult)[idx_default_pertama:]
        if f.default is dataclasses.MISSING
        and f.default_factory is dataclasses.MISSING
    ]
    print("  field non-default setelah default (harus kosong):", non_default_setelah)
    return non_default_setelah


def grep_pemanggil() -> list:
    akar = pathlib.Path(__file__).resolve().parent.parent.parent
    pola = re.compile(r"AesGcmResult\(")
    hasil = []
    for direktori in ("src", "tests"):
        for f in (akar / direktori).rglob("*.py"):
            for i, baris in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if pola.search(baris):
                    hasil.append(f"{f.relative_to(akar)}:{i}")
    return hasil


def main() -> int:
    print("== Bagian 1: semantik Python (dataclass tiruan) ==")
    print("  Opsi A ->", cek_opsi_a())
    print("  Opsi B ->", cek_opsi_b())
    print("  Opsi C ->", cek_opsi_c())

    print("\n== Bagian 2a: pemanggil AesGcmResult( (src + tests) ==")
    for lokasi in grep_pemanggil():
        print("  ", lokasi)

    print("\n== Bagian 2b: kelas nyata AesGcmResult ==")
    non_default_setelah = cek_kelas_nyata()

    a_gagal = cek_opsi_a().startswith("TypeError")
    kelas_aman = non_default_setelah == []
    ok = a_gagal and kelas_aman
    print("\nHASIL:", "OK" if ok else "PERLU DIPERIKSA")
    if not ok:
        print("  (Opsi A harus gagal:", a_gagal, "; kelas aman:", kelas_aman, ")")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
