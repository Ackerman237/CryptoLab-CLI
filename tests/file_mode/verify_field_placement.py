"""Bukti penempatan field D11: kenapa raw_bytes harus sebelum field berdefault.

Dirujuk oleh docs/Prompt/mode-file-spec.md §3.1.

Menunjukkan:
  - Opsi A (raw_bytes tanpa default DI BELAKANG field berdefault) -> TypeError
  - Opsi B (raw_bytes sebelum field berdefault) -> OK (dipilih)
  - Opsi C (raw_bytes dengan default b"") -> OK (tidak dipilih)
  - Konstruktor nyata di aes.py memakai keyword dan belum mengisi raw_bytes.

Jalankan:
    .venv\\Scripts\\python.exe tests/file_mode/verify_field_placement.py
"""

import pathlib
import re
from dataclasses import dataclass, field
from typing import List


def cek_opsi_a() -> str:
    try:
        @dataclass
        class A:  # noqa: D401
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
        c: List[str] = field(default_factory=list)

    b = B(a="x", raw_bytes=b"\x01\x02")
    return f"OK (keyword): raw_bytes={b.raw_bytes!r}; positional B('x', b'\\x01')={B('x', b'\x01').raw_bytes!r}"


def cek_opsi_c() -> str:
    @dataclass
    class C:
        a: str
        b: str = ""
        raw_bytes: bytes = b""

    return f"OK (default kosong): C(a='x').raw_bytes={C(a='x').raw_bytes!r}"


def cek_konstruktor() -> list:
    src = pathlib.Path(
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "src" / "cryptolab" / "core" / "symmetric" / "aes.py"
    ).read_text(encoding="utf-8")
    hasil = []
    for m in re.finditer(r"return AesGcmResult\((.*?)\n    \)", src, re.S):
        body = m.group(1)
        hasil.append(
            ("KEYWORD" if "=" in body else "POSISIONAL", "raw_bytes" in body)
        )
    return hasil


def main() -> int:
    print("== Opsi A: raw_bytes tanpa default di belakang default ==")
    print("  ->", cek_opsi_a())
    print("== Opsi B: raw_bytes sebelum field berdefault (DIPILIH) ==")
    print("  ->", cek_opsi_b())
    print("== Opsi C: raw_bytes dengan default b'' (tidak dipilih) ==")
    print("  ->", cek_opsi_c())

    print("\n== Konstruktor nyata di aes.py ==")
    for i, (gaya, isi) in enumerate(cek_konstruktor(), 1):
        print(f"  konstruktor {i}: {gaya}, raw_bytes sudah diisi? {isi}")

    a_gagal = cek_opsi_a().startswith("TypeError")
    print("\nHASIL:", "OK (Opsi A memang gagal, Opsi B aman)" if a_gagal else "TIDAK KONSISTEN")
    return 0 if a_gagal else 1


if __name__ == "__main__":
    raise SystemExit(main())
