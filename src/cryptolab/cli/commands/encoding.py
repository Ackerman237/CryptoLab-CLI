"""Encoding command handlers (Base64, Hex, Binary)."""

import sys
from argparse import Namespace

from cryptolab.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.encoding.binary_codec import binary_encode, binary_decode

from cryptolab.exceptions import InvalidInputError
from cryptolab.utils.history import log_history
from cryptolab.cli.formatters import render_box


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def handle_base64(args: Namespace) -> int:
    """Handle base64 command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encode":
            res = base64_encode(args.text)
            print(render_box("Hasil Base64", "Base64 (ENCODE)", args.text, res))
            log_history("Base64 Encode", args.text, res, enabled=history_enabled)
        else:
            res = base64_decode(args.text)
            print(render_box("Hasil Base64", "Base64 (DECODE)", args.text, res))
            log_history("Base64 Decode", args.text, res, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_box("Error", "Base64", "", str(err)), file=sys.stderr)
        return 1


def handle_hex(args: Namespace) -> int:
    """Handle hex command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encode":
            delim = getattr(args, "delimiter", " ")
            res = hex_encode(args.text, delimiter=delim)
            print(
                render_box(
                    "Hasil Hex",
                    "Hexadecimal (ENCODE)",
                    args.text,
                    res,
                    {"Delimiter": repr(delim)},
                )
            )
            log_history("Hex Encode", args.text, res, {"delimiter": delim}, enabled=history_enabled)
        else:
            res = hex_decode(args.text)
            print(render_box("Hasil Hex", "Hexadecimal (DECODE)", args.text, res))
            log_history("Hex Decode", args.text, res, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_box("Error", "Hex", "", str(err)), file=sys.stderr)
        return 1


def handle_binary(args: Namespace) -> int:
    """Handle binary command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encode":
            delim = getattr(args, "delimiter", " ")
            res = binary_encode(args.text, delimiter=delim)
            print(
                render_box(
                    "Hasil Binary",
                    "Binary 8-Bit (ENCODE)",
                    args.text,
                    res,
                    {"Delimiter": repr(delim)},
                )
            )
            log_history("Binary Encode", args.text, res, {"delimiter": delim}, enabled=history_enabled)
        else:
            res = binary_decode(args.text)
            print(
                render_box(
                    "Hasil Binary", "Binary 8-Bit (DECODE)", args.text, res
                )
            )
            log_history("Binary Decode", args.text, res, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_box("Error", "Binary", "", str(err)), file=sys.stderr)
        return 1