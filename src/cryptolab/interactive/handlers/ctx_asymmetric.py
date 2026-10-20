"""Asymmetric crypto ctx handlers: RSA, Diffie-Hellman.

Logika kripto TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Setiap fungsi ditandai dengan ``_ctx_fn = True``.
"""

from cryptolab.flow import Result
from cryptolab.core.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
)
from cryptolab.core.utils.history import log_history


def fn_rsa(ctx):
    """RSA: KeyGen, Enkripsi, Dekripsi, Tanda Tangan, Verifikasi."""
    op = ctx.choose(
        "Operasi",
        ["Generate Keypair", "Enkripsi", "Dekripsi", "Tanda Tangan", "Verifikasi"],
    )

    if op == "Generate Keypair":
        bits = ctx.choose("Ukuran kunci", ["1024", "2048", "3072", "4096"], default=2)
        kp = ctx.work(
            f"Membuat keypair RSA-{bits}",
            lambda: rsa_generate_keypair(int(bits)),
        )
        log_history("RSA KeyGen", f"{bits} bit", "keypair generated", {"bits": int(bits)})
        return Result(
            [("Public Key", kp.public_key_pem), ("Private Key", kp.private_key_pem)],
            note="Simpan private key di tempat yang aman!",
        )

    elif op == "Enkripsi":
        plaintext = ctx.ask("Plaintext")
        pub_key = ctx.ask("Public Key (PEM)")
        padding = ctx.choose("Padding", ["OAEP", "PKCS1v15"])
        hash_algo = ctx.choose("Hash", ["SHA256", "SHA512"])
        encoding = ctx.choose("Output encoding", ["hex", "base64"])
        res = ctx.work(
            "Mengenkripsi RSA",
            lambda: rsa_encrypt(plaintext, pub_key, padding=padding, hash_algo=hash_algo, encoding=encoding),
        )
        log_history("RSA Encrypt", plaintext, res.output_text[:32] + "...", {"padding": padding})
        return Result([
            ("Plaintext", plaintext),
            ("Padding", padding),
            ("Ciphertext", res.output_text),
        ])

    elif op == "Dekripsi":
        ciphertext = ctx.ask("Ciphertext (hex/base64)")
        priv_key = ctx.ask("Private Key (PEM)", secret=False)
        padding = ctx.choose("Padding", ["OAEP", "PKCS1v15"])
        hash_algo = ctx.choose("Hash", ["SHA256", "SHA512"])
        encoding = ctx.choose("Input encoding", ["hex", "base64"])
        res = ctx.work(
            "Mendekripsi RSA",
            lambda: rsa_decrypt(ciphertext, priv_key, padding=padding, hash_algo=hash_algo, encoding=encoding),
        )
        log_history("RSA Decrypt", ciphertext[:32], res.output_text[:32], {"padding": padding})
        return Result([
            ("Padding", padding),
            ("Plaintext", res.output_text),
        ])

    elif op == "Tanda Tangan":
        message = ctx.ask("Pesan")
        priv_key = ctx.ask("Private Key (PEM)", secret=False)
        padding = ctx.choose("Padding tanda tangan", ["PSS", "PKCS1v15"])
        hash_algo = ctx.choose("Hash", ["SHA256", "SHA512"])
        encoding = ctx.choose("Output encoding", ["hex", "base64"])
        res = ctx.work(
            "Menandatangani dengan RSA",
            lambda: rsa_sign(message, priv_key, padding=padding, hash_algo=hash_algo, encoding=encoding),
        )
        log_history("RSA Sign", message, res.output_text[:32] + "...", {"padding": padding})
        return Result([
            ("Pesan", message),
            ("Padding", padding),
            ("Tanda Tangan", res.output_text),
        ])

    else:  # Verifikasi
        message = ctx.ask("Pesan asli")
        signature = ctx.ask("Tanda tangan (hex/base64)")
        pub_key = ctx.ask("Public Key (PEM)")
        padding = ctx.choose("Padding tanda tangan", ["PSS", "PKCS1v15"])
        hash_algo = ctx.choose("Hash", ["SHA256", "SHA512"])
        encoding = ctx.choose("Input encoding", ["hex", "base64"])
        res = ctx.work(
            "Memverifikasi tanda tangan RSA",
            lambda: rsa_verify(message, signature, pub_key, padding=padding, hash_algo=hash_algo, encoding=encoding),
        )
        log_history("RSA Verify", message, res.output_text, {"padding": padding})
        return Result([
            ("Pesan", message),
            ("Hasil", res.output_text),
        ] + [(r, "") for r in res.reasons])


fn_rsa._ctx_fn = True


def fn_dh(ctx):
    """Diffie-Hellman Key Exchange."""
    bits = ctx.choose("Ukuran prime", ["2048", "3072", "4096"])
    res = ctx.work(
        f"Melakukan DHKE-{bits}",
        lambda: dh_key_exchange(prime_bits=int(bits)),
    )

    # Opsional: turunkan kunci simetris
    derive = ctx.choose("Turunkan kunci simetris?", ["Ya", "Tidak"])
    rows = [
        ("Prime bits", f"{bits} bit"),
        ("Generator", str(res.generator)),
        ("Alice Public", res.alice_public_hex[:32] + "..."),
        ("Bob Public", res.bob_public_hex[:32] + "..."),
        ("Shared Secret", res.shared_secret_hex[:32] + "..."),
    ]
    if derive == "Ya":
        key_len = ctx.ask("Panjang kunci (bytes)", default=32, cast=int)
        hash_algo = ctx.choose("Hash KDF", ["SHA256", "SHA512"])
        derived = ctx.work(
            "Menurunkan kunci simetris",
            lambda: dh_derive_key(res.shared_secret_hex, key_length=key_len, hash_algo=hash_algo),
        )
        rows.append(("Derived Key", derived))

    log_history("DHKE", f"{bits} bit", res.shared_secret_hex[:32] + "...", {"bits": int(bits)})
    return Result(rows)


fn_dh._ctx_fn = True
