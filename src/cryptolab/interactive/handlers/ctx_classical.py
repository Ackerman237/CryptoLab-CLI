"""Classical cipher ctx handlers: Caesar, Vigenere, DES, AES, RC2.

Logika kripto TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Setiap fungsi ditandai dengan ``_ctx_fn = True``.
"""

from cryptolab.flow import Result
from cryptolab.core.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.core.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.core.analysis.brute_force import caesar_brute_force, find_best_candidate
from cryptolab.core.utils.history import log_history


def fn_caesar(ctx):
    """Caesar Cipher: enkripsi, dekripsi, atau brute-force."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi", "Brute-force"])
    text = ctx.ask("Teks")

    if op == "Enkripsi":
        shift = ctx.ask("Shift (1-25)", default=3, cast=lambda x: _validate_shift(int(x)))
        result = ctx.work("Mengenkripsi Caesar", lambda: caesar_encrypt(text, shift))
        log_history("Caesar Encrypt", text, result, {"shift": shift})
        return Result([("Plaintext", text), ("Shift", str(shift)), ("Ciphertext", result)])

    elif op == "Dekripsi":
        shift = ctx.ask("Shift (1-25)", default=3, cast=lambda x: _validate_shift(int(x)))
        result = ctx.work("Mendekripsi Caesar", lambda: caesar_decrypt(text, shift))
        log_history("Caesar Decrypt", text, result, {"shift": shift})
        return Result([("Ciphertext", text), ("Shift", str(shift)), ("Plaintext", result)])

    else:  # Brute-force
        candidates = ctx.work("Mencoba semua shift", lambda: caesar_brute_force(text))
        best = find_best_candidate(candidates)
        rows = [("Teks asli", text)]
        if best:
            rows.append(("Shift terbaik", str(best.shift)))
            rows.append(("Hasil", best.plaintext))
            rows.append(("Skor", f"{best.score:.2f}"))
        for c in (candidates or [])[:5]:
            rows.append((f"Shift {c.shift:>2}", f"{c.score:.2f} | {c.plaintext[:40]}"))
        log_history("Caesar BruteForce", text, best.plaintext if best else "-")
        return Result(rows)


fn_caesar._ctx_fn = True


def _validate_shift(n):
    if not 1 <= n <= 25:
        raise ValueError("shift harus antara 1 dan 25")
    return n


def fn_vigenere(ctx):
    """Vigenere Cipher: enkripsi atau dekripsi."""
    op = ctx.choose("Operasi", ["Enkripsi", "Dekripsi"])
    text = ctx.ask("Teks")
    key = ctx.ask("Kunci (huruf saja)")

    if op == "Enkripsi":
        result = ctx.work("Mengenkripsi Vigenere", lambda: vigenere_encrypt(text, key))
        log_history("Vigenere Encrypt", text, result, {"key_len": len(key)})
        return Result([("Plaintext", text), ("Kunci", key), ("Ciphertext", result)])
    else:
        result = ctx.work("Mendekripsi Vigenere", lambda: vigenere_decrypt(text, key))
        log_history("Vigenere Decrypt", text, result, {"key_len": len(key)})
        return Result([("Ciphertext", text), ("Kunci", key), ("Plaintext", result)])


fn_vigenere._ctx_fn = True
