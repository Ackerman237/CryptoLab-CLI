"""Symmetric cipher ctx handlers: DES, AES, RC2.

Logika kripto TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Setiap fungsi ditandai dengan ``_ctx_fn = True``.

Panduan kunci/IV:
- DES: kunci 8 byte, IV 8 byte (untuk mode CBC)
- AES: kunci 16/24/32 byte, IV 16 byte (untuk mode CBC)
- RC2: kunci 5-16 byte, IV 8 byte (untuk mode CBC)
"""

import os

from cryptolab.flow import Result
from cryptolab.core.symmetric.des import des_encrypt, des_decrypt
from cryptolab.core.symmetric.aes import aes_encrypt, aes_decrypt, aes_gcm_encrypt, aes_gcm_decrypt
from cryptolab.core.symmetric.rc2 import rc2_encrypt, rc2_decrypt
from cryptolab.core.utils.history import log_history
from cryptolab.cli import input as fin
from cryptolab.core.exceptions import InvalidInputError, DecodingError


def fn_des(ctx):
    """DES: enkripsi atau dekripsi."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"])
    mode = ctx.choose("Mode", ["CBC", "ECB"])
    key = ctx.ask("Kunci (tepat 8 karakter)", secret=True)
    iv = ctx.ask("IV (tepat 8 karakter, kosong untuk ECB)", default="") if mode == "CBC" else ""

    if op == "Enkripsi":
        plaintext = ctx.ask("Plaintext")
        res = ctx.work(
            f"Mengenkripsi DES-{mode}",
            lambda: des_encrypt(plaintext, key, mode=mode, iv=iv if iv else None),
        )
        log_history("DES Encrypt", plaintext, res.output_text, {"mode": mode})
        rows = [("Mode", f"DES-{mode}"), ("Ciphertext (hex)", res.output_text)]
        if iv:
            rows.insert(1, ("IV (hex)", iv.encode().hex() if isinstance(iv, str) else iv.hex()))
        return Result(rows)
    else:
        ciphertext_hex = ctx.ask("Ciphertext (hex)")
        res = ctx.work(
            f"Mendekripsi DES-{mode}",
            lambda: des_decrypt(ciphertext_hex, key, mode=mode, iv=iv if iv else None),
        )
        log_history("DES Decrypt", ciphertext_hex, res.output_text, {"mode": mode})
        rows = [("Mode", f"DES-{mode}"), ("Plaintext", res.output_text)]
        if not res.is_utf8:
            rows.append(("(hex)", res.input_hex if hasattr(res, "input_hex") else "-"))
        return Result(rows)


fn_des._ctx_fn = True


def fn_aes(ctx):
    """AES: enkripsi atau dekripsi."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"])
    mode = ctx.choose("Mode", ["CBC", "ECB"])
    key = ctx.ask("Kunci (16/24/32 karakter untuk AES-128/192/256)", secret=True)
    iv = ctx.ask("IV (tepat 16 karakter, kosong untuk ECB)", default="") if mode == "CBC" else ""

    if op == "Enkripsi":
        plaintext = ctx.ask("Plaintext")
        res = ctx.work(
            f"Mengenkripsi AES-{mode}",
            lambda: aes_encrypt(plaintext, key, mode=mode, iv=iv if iv else None),
        )
        log_history("AES Encrypt", plaintext, res.output_text, {"mode": mode})
        rows = [("Mode", f"AES-{mode}"), ("Ciphertext (hex)", res.output_text)]
        return Result(rows)
    else:
        ciphertext_hex = ctx.ask("Ciphertext (hex)")
        res = ctx.work(
            f"Mendekripsi AES-{mode}",
            lambda: aes_decrypt(ciphertext_hex, key, mode=mode, iv=iv if iv else None),
        )
        log_history("AES Decrypt", ciphertext_hex, res.output_text, {"mode": mode})
        rows = [("Mode", f"AES-{mode}"), ("Plaintext", res.output_text)]
        return Result(rows)


fn_aes._ctx_fn = True


def fn_aes_gcm(ctx):
    """AES-GCM (Tahap 3): enkripsi/dekripsi terautentikasi dengan nonce acak 12 byte."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"])
    key = ctx.ask("Kunci (16/24/32 karakter untuk AES-128/192/256)", secret=True)

    if op == "Enkripsi":
        plaintext = ctx.ask("Plaintext")
        res = ctx.work("Mengenkripsi AES-GCM", lambda: aes_gcm_encrypt(plaintext, key))
        log_history("AES-GCM Encrypt", plaintext, res.payload, {"mode": "GCM"})
        return Result([
            ("Mode", "AES-GCM (AEAD)"),
            ("Nonce (hex, 12 byte)", res.nonce_hex),
            ("Payload (nonce:ciphertext:tag)", res.payload),
        ])

    payload = ctx.ask("Payload (nonce:ciphertext:tag)")
    res = ctx.work("Mendekripsi AES-GCM", lambda: aes_gcm_decrypt(payload, key))
    log_history("AES-GCM Decrypt", payload, res.output_text, {"mode": "GCM"})
    rows = [("Mode", "AES-GCM (AEAD)"), ("Tag", "VALID"), ("Plaintext", res.output_text)]
    if not res.is_utf8:
        rows.append(("(bukan UTF-8)", "ditampilkan dalam hex"))
    return Result(rows)


fn_aes_gcm._ctx_fn = True


def fn_rc2(ctx):
    """RC2: enkripsi atau dekripsi."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"])
    mode = ctx.choose("Mode", ["CBC", "ECB"])
    key = ctx.ask("Kunci (5-16 karakter)", secret=True)
    iv = ctx.ask("IV (tepat 8 karakter, kosong untuk ECB)", default="") if mode == "CBC" else ""

    if op == "Enkripsi":
        plaintext = ctx.ask("Plaintext")
        res = ctx.work(
            f"Mengenkripsi RC2-{mode}",
            lambda: rc2_encrypt(plaintext, key, mode=mode, iv=iv if iv else None),
        )
        log_history("RC2 Encrypt", plaintext, res.output_text, {"mode": mode})
        rows = [("Mode", f"RC2-{mode}"), ("Ciphertext (hex)", res.output_text)]
        note = "PERINGATAN: RC2/ARC2 adalah cipher legacy (deprecated 2015). Gunakan AES untuk sistem baru."
        return Result(rows, note=note)
    else:
        ciphertext_hex = ctx.ask("Ciphertext (hex)")
        res = ctx.work(
            f"Mendekripsi RC2-{mode}",
            lambda: rc2_decrypt(ciphertext_hex, key, mode=mode, iv=iv if iv else None),
        )
        log_history("RC2 Decrypt", ciphertext_hex, res.output_text, {"mode": mode})
        rows = [("Mode", f"RC2-{mode}"), ("Plaintext", res.output_text)]
        note = "PERINGATAN: RC2/ARC2 adalah cipher legacy (deprecated 2015). Gunakan AES untuk sistem baru."
        return Result(rows, note=note)


fn_rc2._ctx_fn = True


# ---------------------------------------------------------------------------
# F4 — "Mode File": enkripsi/dekripsi berkas (GCM/CBC).
# Memakai ULANG helper cli/input.py (tidak menduplikasi logika I/O/format).
# ---------------------------------------------------------------------------


def _bersihkan_path(raw: str) -> str:
    """Normalisasi path yang diseret ke terminal.

    Membuang tanda kutip pembungkus ('' atau "") dan spasi tepi, lalu
    meng-expand ``~``. Mengembalikan path absolut bila memungkinkan.
    """
    s = (raw or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()
    s = os.path.expanduser(s)
    return s


def _tanya_path(ctx, label, default=None):
    return ctx.ask(label, default=default, cast=_bersihkan_path)


def fn_mode_file(ctx):
    """Mode File: enkripsi/dekripsi berkas dengan AES-GCM atau AES-CBC.

    Seluruh I/O berkas, konversi format, dan batas ukuran memakai helper yang
    SAMA dengan CLI (``cryptolab.cli.input``) supaya tidak ada logika ganda.
    """
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"], default=1)
    algo = ctx.choose("Algoritma", ["AES-GCM (AEAD)", "AES-CBC"], default=1)
    algoritma = "GCM" if algo.startswith("AES-GCM") else "CBC"

    path_in = _tanya_path(ctx, "Path berkas masukan")
    fmt = ctx.choose("Format berkas", ["hex", "base64", "raw"], default=1)

    # Kunci (dan IV untuk CBC).
    key = ctx.ask("Kunci (16/24/32 byte)", secret=True)
    iv = ""
    if algoritma == "CBC":
        if op == "Enkripsi":
            iv = ctx.ask("IV (tepat 16 karakter)")

    path_out = _tanya_path(
        ctx, "Path berkas keluaran (kosongkan untuk menampilkan di layar)", default=""
    )

    if op == "Enkripsi":
        return _mode_file_enkripsi(ctx, algoritma, path_in, fmt, key, iv, path_out)
    return _mode_file_dekripsi(ctx, algoritma, path_in, fmt, key, path_out)


fn_mode_file._ctx_fn = True


def _konfirmasi_timpa(ctx, path_out):
    """Tanya konfirmasi bila berkas keluaran sudah ada. True = boleh timpa."""
    if not path_out or not os.path.exists(path_out):
        return True
    pilihan = ctx.choose(
        f"Berkas '{path_out}' sudah ada. Timpa?",
        ["Tidak (batalkan)", "Ya (timpa)"],
        default=1,
    )
    return pilihan.startswith("Ya")


def _mode_file_enkripsi(ctx, algoritma, path_in, fmt, key, iv, path_out):
    if fmt == "raw" and not path_out:
        raise InvalidInputError("Format raw butuh berkas keluaran (path --out).")

    data = fin.read_file_bytes(path_in, fin.LIMIT_PLAINTEXT_BYTES)

    if algoritma == "GCM":
        res = ctx.work("Mengenkripsi berkas (AES-GCM)", lambda: aes_gcm_encrypt(data, key))
        payload = res.payload
    else:
        if not iv:
            raise InvalidInputError("Mode CBC memerlukan IV (tepat 16 karakter).")
        res = ctx.work(
            "Mengenkripsi berkas (AES-CBC)",
            lambda: aes_encrypt(data, key, mode="CBC", iv=iv),
        )
        iv_bytes = iv.encode("utf-8") if isinstance(iv, str) else iv
        payload = fin.build_cbc_payload(iv_bytes.hex(), res.output_text)

    out = fin.encode_ciphertext(payload, fmt, algoritma)

    rows = [
        ("Operasi", "Enkripsi berkas"),
        ("Algoritma", f"AES-{algoritma}"),
        ("Berkas masukan", f"{path_in} ({len(data)} byte)"),
        ("Format", fmt),
        ("Ukuran ciphertext", f"{len(out)} byte"),
    ]
    if path_out:
        if not _konfirmasi_timpa(ctx, path_out):
            return Result(rows + [("Status", "Dibatalkan; berkas keluaran tidak ditulis.")])
        ctx.work("Menulis berkas keluaran", lambda: fin.write_output(path_out, out, force=True, source_path=path_in))
        rows.append(("Berkas keluaran", path_out))
    else:
        rows.append(("Ciphertext", out.decode("ascii", errors="replace")))

    log_history("Mode File Encrypt", path_in, path_out or "(stdout)", {"algo": algoritma, "format": fmt})
    return Result(rows)


def _mode_file_dekripsi(ctx, algoritma, path_in, fmt, key, path_out):
    raw_in = fin.read_decrypt_bytes(path_in, fmt, algoritma)
    parsed = fin.decode_ciphertext(raw_in, fmt, algoritma)

    if algoritma == "GCM":
        payload = f"{parsed['nonce_hex']}:{parsed['ct_hex']}:{parsed['tag_hex']}"
        try:
            res = ctx.work("Mendekripsi berkas (AES-GCM)", lambda: aes_gcm_decrypt(payload, key))
        except (DecodingError, InvalidInputError):
            raise InvalidInputError("Autentikasi gagal: kunci salah, tag rusak, atau data berubah.")
    else:
        iv = bytes.fromhex(parsed["iv_hex"]) if "iv_hex" in parsed else None
        try:
            res = ctx.work(
                "Mendekripsi berkas (AES-CBC)",
                lambda: aes_decrypt(parsed["ct_hex"], key, mode="CBC", iv=iv),
            )
        except (DecodingError, InvalidInputError):
            raise InvalidInputError("Dekripsi gagal: kunci salah atau data rusak.")

    raw_out = res.raw_bytes

    rows = [
        ("Operasi", "Dekripsi berkas"),
        ("Algoritma", f"AES-{algoritma}"),
        ("Berkas masukan", f"{path_in} ({len(raw_in)} byte)"),
        ("Format", fmt),
        ("Ukuran plaintext", f"{len(raw_out)} byte"),
    ]

    if path_out:
        if not _konfirmasi_timpa(ctx, path_out):
            return Result(rows + [("Status", "Dibatalkan; berkas keluaran tidak ditulis.")])
        ctx.work("Menulis berkas keluaran", lambda: fin.write_output(path_out, raw_out, force=True, source_path=path_in))
        rows.append(("Berkas keluaran", path_out))
    else:
        try:
            rows.append(("Plaintext", raw_out.decode("utf-8")))
        except UnicodeDecodeError:
            raise InvalidInputError(
                "Hasil dekripsi biner (bukan UTF-8). Isi 'Path berkas keluaran' untuk menyimpannya."
            )

    log_history("Mode File Decrypt", path_in, path_out or "(stdout)", {"algo": algoritma, "format": fmt})
    return Result(rows)
