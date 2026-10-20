"""Symmetric cipher command handlers (DES, AES, RC2)."""

import sys
from argparse import Namespace

from cryptolab import des_encrypt, des_decrypt, des_auto_analyze, aes_encrypt, aes_decrypt, aes_auto_analyze, rc2_encrypt, rc2_decrypt, rc2_auto_analyze
from cryptolab.core.symmetric.aes import aes_gcm_encrypt, aes_gcm_decrypt
from cryptolab.banner import warn_ecb_mode, warn_rc2, print_warning
from cryptolab import InvalidInputError, InvalidKeyError, DecodingError, log_history
from cryptolab.cli.formatters import render_box, render_error
from cryptolab.cli import input as fin


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


# ---------------------------------------------------------------------------
# F1 — Mode file untuk AES-CBC (dipakai handle_aes) & AES-GCM
# ---------------------------------------------------------------------------


def _emit_decrypted(raw_bytes: bytes, out_path, force: bool):
    """Emit a decrypted payload.

    Without ``--out``: valid UTF-8 is printed as text; binary raises the D10
    error WITHOUT writing a single byte to stdout.
    With ``--out``: bytes are written to disk and a summary is returned.
    Returns ``(exit_code, summary_text)``.
    """
    if out_path is None:
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise InvalidInputError(
                "Hasil dekripsi biner (bukan UTF-8). Gunakan --out untuk menyimpan ke berkas."
            )
        return 0, text
    fin.write_output(out_path, raw_bytes, force=force)
    return 0, f"Ditulis ke {out_path} ({len(raw_bytes)} byte)"


def _print_file_result(title: str, source: str, output: str, params: dict) -> None:
    print(render_box(title, source, source, output, params))


def handle_aes_gcm(args: Namespace) -> int:
    """Handle aes-gcm command (CLI wrapper over the AEAD core)."""
    try:
        history_enabled = _get_history_enabled(args)

        # F1: mode file — hanya bila -f/--file dipakai.
        if getattr(args, "file", None) is not None:
            return _handle_gcm_file(args, history_enabled)
        if getattr(args, "out", None) is not None:
            raise InvalidInputError("--out hanya berlaku bersama --file (mode file).")

        if args.action == "encrypt":
            enc_res = aes_gcm_encrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Enkripsi AES-GCM",
                    "AES-GCM (AEAD) (ENCRYPT)",
                    args.text,
                    enc_res.payload,
                    {"Nonce (12 byte)": enc_res.nonce_hex},
                )
            )
            log_history("AES-GCM Encrypt", args.text, enc_res.payload, {"mode": "GCM"}, enabled=history_enabled)
        else:
            dec_res = aes_gcm_decrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Dekripsi AES-GCM",
                    "AES-GCM (AEAD) (DECRYPT)",
                    args.text,
                    dec_res.output_text,
                    {"Tag": "VALID", "UTF-8": "Ya" if dec_res.is_utf8 else "Tidak (Hex)"},
                )
            )
            log_history("AES-GCM Decrypt", args.text, dec_res.output_text, {"mode": "GCM"}, enabled=history_enabled)
        return 0
    except (InvalidInputError, InvalidKeyError, DecodingError) as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def _handle_gcm_file(args: Namespace, history_enabled: bool) -> int:
    try:
        return _gcm_file(args, history_enabled)
    except (InvalidInputError, InvalidKeyError, DecodingError) as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def _gcm_file(args: Namespace, history_enabled: bool) -> int:
    """AES-GCM file mode (encrypt/decrypt)."""
    fmt = args.format

    if args.action == "encrypt":
        data = fin.read_file_bytes(args.file, fin.LIMIT_PLAINTEXT_BYTES)
        enc_res = aes_gcm_encrypt(data, args.key)
        out = fin.encode_ciphertext(enc_res.payload, fmt, "GCM")
        if args.out is None:
            if fmt == "raw":
                raise InvalidInputError("Format raw butuh --out; byte mentah tidak dicetak ke terminal.")
            print(out.decode("ascii", errors="replace"))
        else:
            fin.write_output(args.out, out, force=args.force, source_path=args.file)
            print(f"Ditulis ke {args.out} ({len(out)} byte)")
        log_history("AES-GCM File Encrypt", args.file, str(len(out)), {"mode": "GCM", "format": fmt}, enabled=history_enabled)
        return 0

    raw = fin.read_decrypt_bytes(args.file, fmt, "GCM")
    parsed = fin.decode_ciphertext(raw, fmt, "GCM")
    payload = f"{parsed['nonce_hex']}:{parsed['ct_hex']}:{parsed['tag_hex']}"
    try:
        dec_res = aes_gcm_decrypt(payload, args.key)
    except (DecodingError, InvalidInputError):
        raise InvalidInputError("Autentikasi gagal: kunci salah, tag rusak, atau data berubah.")
    code, summary = _emit_decrypted(dec_res.raw_bytes, args.out, args.force)
    _print_file_result("Hasil Dekripsi AES-GCM (File)", args.file, summary, {"Format": fmt})
    log_history("AES-GCM File Decrypt", args.file, summary, {"mode": "GCM", "format": fmt}, enabled=history_enabled)
    return code