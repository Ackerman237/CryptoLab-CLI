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
    hash_file,
    hmac_compute,
    hmac_verify,
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


def fn_sha3(ctx):
    """SHA-3 (Tahap 3): hash teks atau file, dengan SHA-256 sebagai pembanding."""
    algo = ctx.choose("Algoritma", ["SHA3-256", "SHA3-512"], default=1)
    return _hash_text_or_file(ctx, algo)


fn_sha3._ctx_fn = True


def fn_hmac256(ctx):
    """HMAC-SHA-256 (Tahap 3): buat MAC atau verifikasi MAC dengan kunci rahasia."""
    op = ctx.choose("Operasi", ["Buat MAC", "Verifikasi MAC"], default=1)
    text = ctx.ask("Pesan")
    key = ctx.ask("Kunci rahasia", secret=True)

    if op == "Buat MAC":
        res = ctx.work("Menghitung HMAC-SHA256", lambda: hmac_compute(text, key, algorithm="SHA256"))
        log_history("HMAC-SHA256", text, res.output_hmac, {"algo": "SHA256"})
        return Result([
            ("Pesan", text),
            ("Algoritma", "HMAC-SHA256"),
            ("MAC", res.output_hmac),
        ])

    expected = ctx.ask("MAC yang diharapkan (hex)")
    match = ctx.work(
        "Memverifikasi HMAC-SHA256",
        lambda: hmac_verify(text, key, expected, algorithm="SHA256"),
    )
    status = "COCOK" if match else "TIDAK COCOK"
    log_history("HMAC-SHA256 Verify", text, status, {"algo": "SHA256", "match": match})
    return Result(
        [("Pesan", text), ("MAC diharapkan", expected), ("Status", status)],
        note="" if match else "MAC tidak cocok - pesan atau kunci berbeda / data dimodifikasi.",
    )


fn_hmac256._ctx_fn = True


def fn_sha512(ctx):
    """SHA-512 (Tahap 3): hash teks atau file, dengan SHA-256 sebagai pembanding.

    Core hash SHA-512 sudah ada sejak awal; handler ini menambah jalur input
    file dan tampilan pembanding SHA-256 sesuai spesifikasi upgrade.
    """
    return _hash_text_or_file(ctx, "SHA512")


fn_sha512._ctx_fn = True


def _hash_text_or_file(ctx, algo):
    src = ctx.choose("Sumber", ["Teks", "File"], default=1)
    if src == "File":
        path = ctx.ask("Path file")
        res = ctx.work(f"Menghitung {algo} (file)", lambda: hash_file(path, algorithm=algo))
        base = ctx.work("Pembanding SHA-256 (file)", lambda: hash_file(path, algorithm="SHA256"))
        log_history(f"Hash {algo} File", path, res.output_hash, {"algo": algo, "filepath": path})
        return Result([
            ("File", path),
            (algo, res.output_hash),
            ("SHA-256 (pembanding)", base.output_hash),
        ])

    text = ctx.ask("Teks")
    res = ctx.work(f"Menghitung {algo}", lambda: hash_compute(text, algorithm=algo))
    base = ctx.work("Pembanding SHA-256", lambda: hash_compute(text, algorithm="SHA256"))
    log_history(f"Hash {algo}", text, res.output_hash, {"algo": algo})
    return Result([
        ("Teks", text),
        (algo, res.output_hash),
        ("SHA-256 (pembanding)", base.output_hash),
    ])


def fn_keygen(ctx):
    """Generate Key (Tahap 3): kunci/byte acak aman dari ``secrets``."""
    length = ctx.ask("Panjang (bytes)", default=32, cast=lambda x: _validate_length(int(x)))
    out = ctx.work("Menghasilkan kunci acak", lambda: generate_random_bytes(length))
    log_history("Generate Key", f"{length} bytes", out[:32] + "...", {"length": length})
    return Result([
        ("Panjang", f"{length} bytes"),
        ("Kunci (hex)", out),
    ], note="Dibuat dengan secrets.token_bytes (CSPRNG), bukan random biasa.")


fn_keygen._ctx_fn = True


def _validate_iters(n):
    if n < 1:
        raise ValueError("iterasi harus >= 1")
    return n


def _validate_length(n):
    if not 1 <= n <= 1024:
        raise ValueError("panjang harus 1-1024")
    return n
