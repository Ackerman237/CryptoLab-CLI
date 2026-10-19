"""Classical cipher command handlers."""

import sys
from argparse import Namespace

from cryptolab import caesar_encrypt, caesar_decrypt
from cryptolab import vigenere_encrypt, vigenere_decrypt
from cryptolab import playfair_encrypt, playfair_decrypt
from cryptolab import hill_encrypt, hill_decrypt
from cryptolab import affine_encrypt, affine_decrypt, affine_brute_force, VALID_A_VALUES
from cryptolab import railfence_encrypt, railfence_decrypt, railfence_brute_force

from cryptolab import caesar_brute_force, find_best_candidate
from cryptolab import InvalidInputError
from cryptolab import log_history
from cryptolab.cli.formatters import (
    render_box,
    render_error,
    render_brute_force,
)


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def handle_caesar(args: Namespace) -> int:
    """Handle caesar command (encrypt/decrypt/brute-force)."""
    try:
        history_enabled = _get_history_enabled(args)

        if args.action in ("brute-force", "brute"):
            candidates = caesar_brute_force(args.text)
            show_best = getattr(args, "best", False)
            print(render_brute_force(args.text, candidates, show_best_only=show_best))
            best = find_best_candidate(candidates)
            log_history(
                "Caesar Brute Force",
                args.text,
                best.text if best else "",
                {"best_shift": best.shift if best else None},
                enabled=history_enabled,
            )
            return 0

        # Encrypt / Decrypt actions require shift
        if args.shift is None:
            raise InvalidInputError(
                "Operasi encrypt/decrypt Caesar memerlukan parameter --shift / -s."
            )

        if args.action == "encrypt":
            res = caesar_encrypt(args.text, args.shift)
            print(
                render_box(
                    "Hasil Enkripsi",
                    "Caesar Cipher (ENCRYPT)",
                    args.text,
                    res,
                    {"Shift": args.shift},
                )
            )
            log_history("Caesar Encrypt", args.text, res, {"shift": args.shift}, enabled=history_enabled)
        else:
            res = caesar_decrypt(args.text, args.shift)
            print(
                render_box(
                    "Hasil Dekripsi",
                    "Caesar Cipher (DECRYPT)",
                    args.text,
                    res,
                    {"Shift": args.shift},
                )
            )
            log_history("Caesar Decrypt", args.text, res, {"shift": args.shift}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_brute(args: Namespace) -> int:
    """Handle brute command (Caesar brute force shortcut)."""
    try:
        history_enabled = _get_history_enabled(args)
        candidates = caesar_brute_force(args.text)
        show_best = getattr(args, "best", False)
        print(render_brute_force(args.text, candidates, show_best_only=show_best))
        best = find_best_candidate(candidates)
        log_history(
            "Caesar Brute Force",
            args.text,
            best.text if best else "",
            {"best_shift": best.shift if best else None},
            enabled=history_enabled,
        )
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_vigenere(args: Namespace) -> int:
    """Handle vigenere command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encrypt":
            res = vigenere_encrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Enkripsi",
                    "Vigenere Cipher (ENCRYPT)",
                    args.text,
                    res,
                    {"Kunci": args.key},
                )
            )
            log_history("Vigenere Encrypt", args.text, res, {"key_length": len(args.key)}, enabled=history_enabled)
        else:
            res = vigenere_decrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Dekripsi",
                    "Vigenere Cipher (DECRYPT)",
                    args.text,
                    res,
                    {"Kunci": args.key},
                )
            )
            log_history("Vigenere Decrypt", args.text, res, {"key_length": len(args.key)}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_playfair(args: Namespace) -> int:
    """Handle playfair command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encrypt":
            res = playfair_encrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Enkripsi Playfair",
                    "Playfair Cipher (ENCRYPT)",
                    args.text,
                    res.output_text,
                    {"Key": args.key, "Matrix": "5x5 (I=J)"},
                )
            )
            log_history("Playfair Encrypt", args.text, res.output_text, {"key": args.key}, enabled=history_enabled)
        else:
            res = playfair_decrypt(args.text, args.key)
            print(
                render_box(
                    "Hasil Dekripsi Playfair",
                    "Playfair Cipher (DECRYPT)",
                    args.text,
                    res.output_text,
                    {"Key": args.key, "Note": "Mungkin mengandung padding X"},
                )
            )
            log_history("Playfair Decrypt", args.text, res.output_text, {"key": args.key}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_hill(args: Namespace) -> int:
    """Handle hill command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "encrypt":
            res = hill_encrypt(args.text, args.key, args.size)
            print(
                render_box(
                    f"Hasil Enkripsi Hill {args.size}x{args.size}",
                    f"Hill Cipher (ENCRYPT)",
                    args.text,
                    res.output_text,
                    {"Key Matrix": args.key, "Size": f"{args.size}x{args.size}", "Det": res.determinant, "DetInv": res.determinant_inv},
                )
            )
            log_history(f"Hill {args.size}x{args.size} Encrypt", args.text, res.output_text, {"key": args.key, "size": args.size}, enabled=history_enabled)
        else:
            res = hill_decrypt(args.text, args.key, args.size)
            print(
                render_box(
                    f"Hasil Dekripsi Hill {args.size}x{args.size}",
                    f"Hill Cipher (DECRYPT)",
                    args.text,
                    res.output_text,
                    {"Key Matrix": args.key, "Size": f"{args.size}x{args.size}", "Note": "Mungkin mengandung padding X"},
                )
            )
            log_history(f"Hill {args.size}x{args.size} Decrypt", args.text, res.output_text, {"key": args.key, "size": args.size}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_affine(args: Namespace) -> int:
    """Handle affine command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "brute":
            if not args.text:
                raise InvalidInputError("Brute-force memerlukan --text / -t.")
            candidates = affine_brute_force(args.text)
            if not candidates:
                print(render_error("Affine Brute Force", "Tidak ada kandidat valid."))
                return 1
            best = candidates[0]
            print(
                render_box(
                    "Hasil Affine Brute Force",
                    f"Affine (Best: a={best.a}, b={best.b})",
                    args.text,
                    best.output_text,
                    {"Total Candidates": len(candidates), "Top a": best.a, "Top b": best.b},
                )
            )
            log_history("Affine Brute Force", args.text, best.output_text, {"candidates": len(candidates)}, enabled=history_enabled)
            return 0

        if args.mult is None or args.add is None:
            raise InvalidInputError("Operasi encrypt/decrypt memerlukan --mult / -a dan --add / -b.")

        if args.action == "encrypt":
            res = affine_encrypt(args.text, args.mult, args.add)
            print(
                render_box(
                    "Hasil Enkripsi Affine",
                    f"Affine Cipher (ENCRYPT) a={args.mult}, b={args.add}",
                    args.text,
                    res.output_text,
                    {"a": args.mult, "b": args.add, "a_inv": res.a_inv, "Valid a": f"{len(VALID_A_VALUES)} values"},
                )
            )
            log_history("Affine Encrypt", args.text, res.output_text, {"a": args.mult, "b": args.add}, enabled=history_enabled)
        else:
            res = affine_decrypt(args.text, args.mult, args.add)
            print(
                render_box(
                    "Hasil Dekripsi Affine",
                    f"Affine Cipher (DECRYPT) a={args.mult}, b={args.add}",
                    args.text,
                    res.output_text,
                    {"a": args.mult, "b": args.add, "a_inv": res.a_inv},
                )
            )
            log_history("Affine Decrypt", args.text, res.output_text, {"a": args.mult, "b": args.add}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1


def handle_railfence(args: Namespace) -> int:
    """Handle railfence command."""
    try:
        history_enabled = _get_history_enabled(args)
        if args.action == "brute":
            if not args.text:
                raise InvalidInputError("Brute-force memerlukan --text / -t.")
            candidates = railfence_brute_force(args.text, args.max_rails)
            if not candidates:
                print(render_error("Rail Fence Brute Force", "Tidak ada kandidat valid."))
                return 1
            best = candidates[0]
            print(
                render_box(
                    "Hasil Rail Fence Brute Force",
                    f"Rail Fence (Best: {best.rails} rails)",
                    args.text,
                    best.output_text,
                    {"Total Candidates": len(candidates), "Top Rails": best.rails},
                )
            )
            log_history("Rail Fence Brute Force", args.text, best.output_text, {"candidates": len(candidates)}, enabled=history_enabled)
            return 0

        if args.action == "encrypt":
            res = railfence_encrypt(args.text, args.rails)
            pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
            print(
                render_box(
                    f"Hasil Enkripsi Rail Fence",
                    f"Rail Fence (ENCRYPT) {args.rails} rails",
                    args.text,
                    res.output_text,
                    {"Rails": args.rails, "Pattern": "Zig-zag"},
                )
            )
            print(f"\n  Rail Pattern:\n{pattern_str}\n")
            log_history(f"Rail Fence {args.rails} Encrypt", args.text, res.output_text, {"rails": args.rails}, enabled=history_enabled)
        else:
            res = railfence_decrypt(args.text, args.rails)
            pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
            print(
                render_box(
                    f"Hasil Dekripsi Rail Fence",
                    f"Rail Fence (DECRYPT) {args.rails} rails",
                    args.text,
                    res.output_text,
                    {"Rails": args.rails, "Note": "Transposition cipher"},
                )
            )
            print(f"\n  Rail Pattern:\n{pattern_str}\n")
            log_history(f"Rail Fence {args.rails} Decrypt", args.text, res.output_text, {"rails": args.rails}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1