"""Encoding ctx handlers: Base64, Hex, Binary.

Fungsi-fungsi ini menerima ``ctx`` dan mengembalikan ``Result``.
Logika encoding TIDAK diubah - hanya lapisan UI diganti ke ctx API.
Tandai setiap fungsi dengan ``_ctx_fn = True`` agar ``run_interactive_menu``
tahu untuk memanggilnya via ``run_action``.
"""

from cryptolab.flow import Result
from cryptolab.core.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.core.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.core.encoding.binary_codec import binary_encode, binary_decode
from cryptolab.core.utils.history import log_history


def fn_base64(ctx):
    """Base64 encode / decode."""
    op = ctx.choose("Operasi", ["Encode (Teks → Base64)", "Decode (Base64 → Teks)"])
    data = ctx.ask("Teks")
    if op.startswith("Encode"):
        out = ctx.work("Mengkode Base64", lambda: base64_encode(data))
        log_history("Base64 Encode", data, out)
        return Result([("Input", data), ("Base64", out)])
    else:
        out = ctx.work("Mendekode Base64", lambda: base64_decode(data))
        log_history("Base64 Decode", data, out)
        return Result([("Input", data), ("Teks", out)])


fn_base64._ctx_fn = True


def fn_hex(ctx):
    """Hex encode / decode."""
    op = ctx.choose("Operasi", ["Encode (Teks → Hex)", "Decode (Hex → Teks)"])
    data = ctx.ask("Teks")
    if op.startswith("Encode"):
        out = ctx.work("Mengkode Hex", lambda: hex_encode(data))
        log_history("Hex Encode", data, out)
        return Result([("Input", data), ("Hex", out)])
    else:
        out = ctx.work("Mendekode Hex", lambda: hex_decode(data))
        log_history("Hex Decode", data, out)
        return Result([("Input", data), ("Teks", out)])


fn_hex._ctx_fn = True


def fn_binary(ctx):
    """Binary encode / decode."""
    op = ctx.choose("Operasi", ["Encode (Teks → Binary)", "Decode (Binary → Teks)"])
    data = ctx.ask("Teks")
    if op.startswith("Encode"):
        delim_options = [
            "Spasi (' ')",
            "Strip ('-')",
            "Titik ('.')",
            "Koma (',')",
            "Tanpa pemisah",
            "Custom (input sendiri)",
        ]
        choice = ctx.choose("Pemisah (delimiter)", delim_options, default=1)
        if choice.startswith("Spasi"):
            delim = " "
        elif choice.startswith("Strip"):
            delim = "-"
        elif choice.startswith("Titik"):
            delim = "."
        elif choice.startswith("Koma"):
            delim = ","
        elif choice.startswith("Tanpa"):
            delim = ""
        else:
            def _validate_delimiter(raw: str) -> str:
                if not raw:
                    raise ValueError("Pemisah tidak boleh kosong")
                if any(ch in "01" for ch in raw):
                    raise ValueError("Pemisah tidak boleh mengandung angka 0 atau 1")
                if any(ch.isalnum() for ch in raw):
                    raise ValueError("Pemisah harus berupa simbol atau spasi (tanpa huruf/angka)")
                if len(raw) > 5:
                    raise ValueError("Pemisah maksimal 5 karakter")
                return raw

            delim = ctx.ask(
                "Pemisah kustom (maks 5 simbol, tanpa angka 0 atau 1)",
                cast=_validate_delimiter,
            )

        out = ctx.work("Mengkode Binary", lambda: binary_encode(data, delimiter=delim))
        log_history("Binary Encode", data, out, {"delimiter": delim})
        delim_label = (
            "Tanpa pemisah"
            if delim == ""
            else ("Spasi (' ')" if delim == " " else repr(delim))
        )
        return Result([
            ("Input", data),
            ("Pemisah", delim_label),
            ("Binary", out),
        ])
    else:
        out = ctx.work("Mendekode Binary", lambda: binary_decode(data))
        log_history("Binary Decode", data, out)
        return Result([("Input", data), ("Teks", out)])


fn_binary._ctx_fn = True
