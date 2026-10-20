"""Hashing ctx handler: MD5, SHA, HMAC, PBKDF2, Bcrypt, Random.

Logika hashing TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Fungsi ditandai dengan ``_ctx_fn = True``.
"""

import os
import hashlib
import hmac

from cryptolab.flow import Result
from cryptolab.core.hashing import (
    hash_compute,
    hmac_compute,
    pbkdf2_hash,
    generate_random_bytes,
    BCRYPT_AVAILABLE,
)
from cryptolab.core.utils.history import log_history


def fn_hash(ctx):
    """Hashing & Password: MD5, SHA-256, HMAC-SHA256, PBKDF2-SHA256."""
    algo = ctx.choose(
        "Algoritma",
        ["MD5", "SHA-256", "SHA-512", "HMAC-SHA256", "PBKDF2-SHA256", "Random Bytes"],
        default=2,
    )

    if algo == "MD5":
        text = ctx.ask("Teks")
        res = ctx.work("Menghitung MD5", lambda: hash_compute(text, algorithm="MD5"))
        note = "PERINGATAN: MD5 adalah hash lemah. JANGAN gunakan untuk keamanan."
        log_history("Hash MD5", text, res.output_hash, {"algo": "MD5"})
        return Result([("Teks", text), ("Hash", res.output_hash)], note=note)

    elif algo == "SHA-256":
        text = ctx.ask("Teks")
        res = ctx.work("Menghitung SHA-256", lambda: hash_compute(text, algorithm="SHA256"))
        log_history("Hash SHA-256", text, res.output_hash, {"algo": "SHA256"})
        return Result([("Teks", text), ("Hash", res.output_hash)])

    elif algo == "SHA-512":
        text = ctx.ask("Teks")
        res = ctx.work("Menghitung SHA-512", lambda: hash_compute(text, algorithm="SHA512"))
        log_history("Hash SHA-512", text, res.output_hash, {"algo": "SHA512"})
        return Result([("Teks", text), ("Hash", res.output_hash)])

    elif algo == "HMAC-SHA256":
        text = ctx.ask("Teks")
        key = ctx.ask("Kunci HMAC", secret=True)
        res = ctx.work("Menghitung HMAC-SHA256", lambda: hmac_compute(text, key, algorithm="SHA256"))
        log_history("HMAC-SHA256", text, res.output_hmac, {"algo": "SHA256"})
        return Result([("Teks", text), ("HMAC", res.output_hmac)])

    elif algo == "PBKDF2-SHA256":
        text = ctx.ask("Teks / Password")
        iters = ctx.ask("Iterasi", default=600000, cast=lambda x: _validate_iters(int(x)))
        salt = os.urandom(16)
        res = ctx.work(
            f"Menghitung PBKDF2 ({iters:,} iterasi)".replace(",", "."),
            lambda: pbkdf2_hash(text, iterations=iters, algorithm="SHA256"),
        )
        log_history("PBKDF2-SHA256", text, res.hash_value[:32] + "...", {"iterations": iters})
        return Result([
            ("Teks", text),
            ("Algoritma", "PBKDF2-SHA256"),
            ("Iterasi", str(iters)),
            ("Salt", res.salt),
            ("Hash", res.hash_value),
        ])

    else:  # Random Bytes
        length = ctx.ask("Panjang (bytes)", default=32, cast=lambda x: _validate_length(int(x)))
        out = ctx.work("Menghasilkan random bytes", lambda: generate_random_bytes(length))
        log_history("Random Bytes", f"{length} bytes", out, {"length": length})
        return Result([("Panjang", f"{length} bytes"), ("Hex", out)])


fn_hash._ctx_fn = True


def _validate_iters(n):
    if n < 1:
        raise ValueError("iterasi harus >= 1")
    return n


def _validate_length(n):
    if not 1 <= n <= 1024:
        raise ValueError("panjang harus 1-1024")
    return n
