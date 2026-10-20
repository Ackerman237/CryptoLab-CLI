"""CLI Package - Command Line Interface for CryptoLab."""

from cryptolab.cli.parser import create_parser
from cryptolab.cli.formatters import render_box, render_error
from cryptolab.cli.commands import (
    handle_caesar,
    handle_brute,
    handle_vigenere,
    handle_playfair,
    handle_hill,
    handle_affine,
    handle_railfence,
    handle_base64,
    handle_hex,
    handle_binary,
    handle_analyze,
    handle_detect,
    handle_auto,
    handle_history,
    handle_des,
    handle_aes,
    handle_rc2,
    handle_hash,
    handle_hmac,
    handle_pbkdf2,
    handle_bcrypt,
    handle_random,
    handle_rsa,
    handle_dh,
)

__all__ = [
    "create_parser",
    "render_box",
    "render_error",
    # Classical
    "handle_caesar",
    "handle_brute",
    "handle_vigenere",
    "handle_playfair",
    "handle_hill",
    "handle_affine",
    "handle_railfence",
    # Encoding
    "handle_base64",
    "handle_hex",
    "handle_binary",
    # Analysis
    "handle_analyze",
    "handle_detect",
    "handle_auto",
    # History
    "handle_history",
    # Symmetric
    "handle_des",
    "handle_aes",
    "handle_rc2",
    # Hashing
    "handle_hash",
    "handle_hmac",
    "handle_pbkdf2",
    "handle_bcrypt",
    "handle_random",
    # Asymmetric
    "handle_rsa",
    "handle_dh",
]


def handle_cli_args(args) -> int:
    """Execute direct CLI commands based on parsed arguments."""
    from cryptolab.exceptions import CryptoLabError
    from cryptolab.cli.formatters import render_error
    from cryptolab.interactive import run_interactive_menu
    import sys

    if args.command is None or args.command == "menu":
        run_interactive_menu()
        return 0

    command_handlers = {
        "caesar": handle_caesar,
        "brute": handle_brute,
        "vigenere": handle_vigenere,
        "playfair": handle_playfair,
        "hill": handle_hill,
        "affine": handle_affine,
        "railfence": handle_railfence,
        "base64": handle_base64,
        "hex": handle_hex,
        "binary": handle_binary,
        "analyze": handle_analyze,
        "detect": handle_detect,
        "auto": handle_auto,
        "history": handle_history,
        "des": handle_des,
        "aes": handle_aes,
        "rc2": handle_rc2,
        "hash": handle_hash,
        "hmac": handle_hmac,
        "pbkdf2": handle_pbkdf2,
        "bcrypt": handle_bcrypt,
        "random": handle_random,
        "rsa": handle_rsa,
        "dh": handle_dh,
    }

    handler = command_handlers.get(args.command)
    if not handler:
        print(render_error("Unknown Command", f"Perintah tidak dikenal: {args.command}"), file=sys.stderr)
        return 1

    try:
        return handler(args)
    except CryptoLabError as err:
        print(render_error(err.__class__.__name__, str(err)), file=sys.stderr)
        return 1
    except Exception as err:
        print(render_error("Kesalahan Tak Terduga", str(err)), file=sys.stderr)
        return 2