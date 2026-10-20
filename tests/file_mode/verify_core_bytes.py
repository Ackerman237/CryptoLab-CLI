"""Bukti bahwa core menerima bytes dan round-trip biner berhasil (tanpa ubah core).

Dirujuk oleh docs/Prompt/mode-file-spec.md §1.1 dan §1.2.

Menguji DUA hal:
  1. AES-CBC: AesResult.raw_bytes berisi byte asli (semua kasus).
  2. AES-GCM: output_text BERBEDA untuk UTF-8 (teks) vs non-UTF8 (hex), dan
     cara mengubahnya kembali ke byte harus memakai penanda is_utf8 -- bukan
     menebak lewat bytes.fromhex().

Jalankan:
    .venv\\Scripts\\python.exe tests/file_mode/verify_core_bytes.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cryptolab.core.symmetric.aes import (  # noqa: E402
    aes_encrypt,
    aes_decrypt,
    aes_gcm_encrypt,
    aes_gcm_decrypt,
)

KEY = b"kunci-enambelas!"   # 16 byte (AES-128)
IV = b"iv-enam-belas-by"    # 16 byte

KASUS = (
    (b"halo", "UTF-8 biasa"),
    (b"deadbeef", "UTF-8 sekaligus hex valid (kasus jebakan)"),
    (os.urandom(64), "biner acak non-UTF8"),
)


def to_bytes_aman(result) -> bytes:
    """Jalur aman tanpa D11: pakai penanda is_utf8, bukan tebakan."""
    if result.is_utf8:
        return result.output_text.encode("utf-8")
    return bytes.fromhex(result.output_text)


def main() -> int:
    semua_ok = True

    for data, ket in KASUS:
        print(f"\n== {ket} ==  plaintext={len(data)} byte")

        # --- AES-CBC: raw_bytes selalu byte asli ---
        enc = aes_encrypt(data, KEY, mode="CBC", iv=IV)
        cbc = aes_decrypt(enc.output_text, KEY, mode="CBC", iv=IV)
        cbc_ok = cbc.raw_bytes == data
        print(f"  CBC  raw_bytes round-trip      : {cbc_ok}")

        # --- AES-GCM: output_text bergantung is_utf8 ---
        g = aes_gcm_encrypt(data, KEY)
        gd = aes_gcm_decrypt(g.payload, KEY)
        gcm_ok = to_bytes_aman(gd) == data
        print(f"  GCM  is_utf8={gd.is_utf8}  output_text={gd.output_text[:24]!r}")
        print(f"  GCM  round-trip (via is_utf8)  : {gcm_ok}")

        # Demonstrasi jebakan: bytes.fromhex() pada UTF-8.
        if gd.is_utf8:
            try:
                salah = bytes.fromhex(gd.output_text)
                print(f"  JEBAKAN bytes.fromhex() -> {salah!r}"
                      f"  (BENAR? {salah == data})")
            except ValueError as e:
                print(f"  JEBAKAN bytes.fromhex() -> GAGAL: {e}")

        semua_ok = semua_ok and cbc_ok and gcm_ok

    print("\nHASIL:", "OK" if semua_ok else "GAGAL")
    return 0 if semua_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
