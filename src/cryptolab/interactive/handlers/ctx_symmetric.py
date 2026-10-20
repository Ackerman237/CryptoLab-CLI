"""Symmetric cipher ctx handlers: DES, AES, RC2.

Logika kripto TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Setiap fungsi ditandai dengan ``_ctx_fn = True``.

Panduan kunci/IV:
- DES: kunci 8 byte, IV 8 byte (untuk mode CBC)
- AES: kunci 16/24/32 byte, IV 16 byte (untuk mode CBC)
- RC2: kunci 5-16 byte, IV 8 byte (untuk mode CBC)
"""

from cryptolab.flow import Result
from cryptolab.core.symmetric.des import des_encrypt, des_decrypt
from cryptolab.core.symmetric.aes import aes_encrypt, aes_decrypt, aes_gcm_encrypt, aes_gcm_decrypt
from cryptolab.core.symmetric.rc2 import rc2_encrypt, rc2_decrypt
from cryptolab.core.utils.history import log_history


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
