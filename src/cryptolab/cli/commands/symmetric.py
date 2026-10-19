"""Symmetric cipher command handlers (DES, AES, RC2)."""

import sys
from argparse import Namespace

from cryptolab.symmetric.des import des_encrypt, des_decrypt, des_auto_analyze
from cryptolab.symmetric.aes import aes_encrypt, aes_decrypt, aes_auto_analyze
from cryptolab.symmetric.rc2 import rc2_encrypt, rc2_decrypt, rc2_auto_analyze
from cryptolab.banner import warn_ecb_mode, warn_rc2, print_warning

from cryptolab.exceptions import InvalidInputError
from cryptolab.utils.history import log_history
from cryptolab.cli.formatters import render_box, render_error


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def _norm_mode(mode: str) -> str:
    return mode.upper()


def _norm_padding(padding: str) -> str:
    return "PKCS7" if padding.upper() == "PKCS7" else "None"


def handle_des(args: Namespace) -> int:
    """Handle des command."""
    try:
        history_enabled = _get_history_enabled(args)
        norm_mode = _norm_mode(args.mode)
        norm_padding = _norm_padding(args.padding)

        # Warning for ECB mode
        if norm_mode == "ECB":
            print_warning(warn_ecb_mode())

        if args.action == "auto":
            candidates = des_auto_analyze(args.text, key=args.key, iv=args.iv)
            if not candidates:
                print(render_error("DES Auto", "Tidak ada konfigurasi DES yang berhasil didekripsi."))
                return 1
            best_des = candidates[0]
            print(
                render_box(
                    "Hasil DES Auto",
                    f"DES Auto ({best_des.mode}, Padding {best_des.padding})",
                    args.text,
                    best_des.output_text,
                    {"Mode": best_des.mode, "Padding": best_des.padding, "Skor": f"{best_des.score:.1f}/100"},
                )
            )
            log_history("DES Auto", args.text, best_des.output_text, {"mode": best_des.mode, "padding": best_des.padding}, enabled=history_enabled)
            return 0

        if not args.key:
            raise InvalidInputError("Operasi encrypt/decrypt DES memerlukan parameter --key / -k (8 byte).")

        if args.action == "encrypt":
            enc_res = des_encrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
            print(
                render_box(
                    "Hasil Enkripsi DES",
                    f"DES ({norm_mode}) (ENCRYPT)",
                    args.text,
                    enc_res.output_text,
                    {"Mode": norm_mode, "Padding": norm_padding},
                )
            )
            log_history("DES Encrypt", args.text, enc_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
        else:
            dec_res = des_decrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
            print(
                render_box(
                    "Hasil Dekripsi DES",
                    f"DES ({norm_mode}) (DECRYPT)",
                    args.text,
                    dec_res.output_text,
                    {"Mode": norm_mode, "Padding": norm_padding, "UTF-8": "Ya" if dec_res.is_utf8 else "Tidak (Hex)"},
                )
            )
            log_history("DES Decrypt", args.text, dec_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_aes(args: Namespace) -> int:
    """Handle aes command."""
    try:
        history_enabled = _get_history_enabled(args)
        norm_mode = _norm_mode(args.mode)
        norm_padding = _norm_padding(args.padding)

        # Warning for ECB mode
        if norm_mode == "ECB":
            print_warning(warn_ecb_mode())

        if args.action == "auto":
            candidates = aes_auto_analyze(args.text, key=args.key, iv=args.iv)
            if not candidates:
                print(render_error("AES Auto", "Tidak ada konfigurasi AES yang berhasil didekripsi."))
                return 1
            best_aes = candidates[0]
            print(
                render_box(
                    "Hasil AES Auto",
                    f"AES Auto ({best_aes.mode}, Padding {best_aes.padding})",
                    args.text,
                    best_aes.output_text,
                    {"Mode": best_aes.mode, "Padding": best_aes.padding, "Skor": f"{best_aes.score:.1f}/100"},
                )
            )
            log_history("AES Auto", args.text, best_aes.output_text, {"mode": best_aes.mode, "padding": best_aes.padding}, enabled=history_enabled)
            return 0

        if not args.key:
            raise InvalidInputError("Operasi encrypt/decrypt AES memerlukan parameter --key / -k (16 byte).")

        if args.action == "encrypt":
            enc_res = aes_encrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
            print(
                render_box(
                    "Hasil Enkripsi AES",
                    f"AES ({norm_mode}) (ENCRYPT)",
                    args.text,
                    enc_res.output_text,
                    {"Mode": norm_mode, "Padding": norm_padding},
                )
            )
            log_history("AES Encrypt", args.text, enc_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
        else:
            dec_res = aes_decrypt(args.text, key=args.key, mode=norm_mode, iv=args.iv, padding=norm_padding)
            print(
                render_box(
                    "Hasil Dekripsi AES",
                    f"AES ({norm_mode}) (DECRYPT)",
                    args.text,
                    dec_res.output_text,
                    {"Mode": norm_mode, "Padding": norm_padding, "UTF-8": "Ya" if dec_res.is_utf8 else "Tidak (Hex)"},
                )
            )
            log_history("AES Decrypt", args.text, dec_res.output_text, {"mode": norm_mode, "padding": norm_padding}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_rc2(args: Namespace) -> int:
    """Handle rc2 command."""
    try:
        history_enabled = _get_history_enabled(args)
        norm_mode = _norm_mode(args.mode)
        norm_padding = _norm_padding(args.padding)
        effective_keylen = args.effective_keylen

        # Warning for RC2 legacy cipher
        print_warning(warn_rc2())

        # Warning for ECB mode
        if norm_mode == "ECB":
            print_warning(warn_ecb_mode())

        if args.action == "auto":
            candidates = rc2_auto_analyze(
                args.text, key=args.key, iv=args.iv, effective_keylen=effective_keylen
            )
            if not candidates:
                print(render_error("RC2 Auto", "Tidak ada konfigurasi RC2 yang berhasil didekripsi."))
                return 1
            best_rc2 = candidates[0]
            print(
                render_box(
                    "Hasil RC2 Auto", f"RC2 Auto ({best_rc2.mode}, Padding {best_rc2.padding})",
                    args.text, best_rc2.output_text,
                    {"Mode": best_rc2.mode, "Padding": best_rc2.padding,
                     "Effective": f"{effective_keylen} bit", "Skor": f"{best_rc2.score:.1f}/100"},
                )
            )
            log_history("RC2 Auto", args.text, best_rc2.output_text,
                        {"mode": best_rc2.mode, "padding": best_rc2.padding}, enabled=history_enabled)
            return 0

        if not args.key:
            raise InvalidInputError("Operasi encrypt/decrypt RC2 memerlukan parameter --key / -k.")
        params = {"Mode": norm_mode, "Padding": norm_padding, "Effective": f"{effective_keylen} bit"}
        if args.action == "encrypt":
            result = rc2_encrypt(args.text, args.key, norm_mode, args.iv, norm_padding, effective_keylen)
            print(render_box("Hasil Enkripsi RC2", f"RC2 ({norm_mode}) (ENCRYPT)", args.text, result.output_text, params))
            log_history("RC2 Encrypt", args.text, result.output_text, params, enabled=history_enabled)
        else:
            result = rc2_decrypt(args.text, args.key, norm_mode, args.iv, norm_padding, effective_keylen)
            params["UTF-8"] = "Ya" if result.is_utf8 else "Tidak (Hex)"
            print(render_box("Hasil Dekripsi RC2", f"RC2 ({norm_mode}) (DECRYPT)", args.text, result.output_text, params))
            log_history("RC2 Decrypt", args.text, result.output_text, params, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1