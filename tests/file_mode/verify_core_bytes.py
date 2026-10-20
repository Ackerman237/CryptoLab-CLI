"""Bukti bahwa core menerima bytes dan round-trip biner berhasil (tanpa ubah core).

Dirujuk oleh docs/Prompt/mode-file-spec.md §1.1.

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


def main() -> int:
    # Byte acak: hampir pasti bukan UTF-8 -> kasus nyata foto/dokumen.
    data = os.urandom(64)

    print("plaintext:", len(data), "byte biner")

    # --- AES-CBC: plaintext bytes -> raw_bytes berisi byte asli ---
    enc = aes_encrypt(data, KEY, mode="CBC", iv=IV)
    dec = aes_decrypt(enc.output_text, KEY, mode="CBC", iv=IV)
    cbc_ok = dec.raw_bytes == data
    print(f"AES-CBC raw_bytes round-trip: {cbc_ok}")

    # --- AES-GCM: plaintext bytes -> payload hex; dekripsi hex -> bytes.fromhex ---
    g = aes_gcm_encrypt(data, KEY)
    gd = aes_gcm_decrypt(g.payload, KEY)
    # AesGcmResult tidak punya raw_bytes -> hex di output_text saat non-UTF8.
    gcm_bytes = bytes.fromhex(gd.output_text) if not gd.is_utf8 else gd.output_text.encode()
    gcm_ok = gcm_bytes == data
    print(f"AES-GCM output_text(hex) round-trip: {gcm_ok}")

    ok = cbc_ok and gcm_ok
    print("HASIL:", "OK" if ok else "GAGAL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
