"""Hashing command handlers (hash, hmac, pbkdf2, bcrypt, random)."""

import sys
from argparse import Namespace

from cryptolab import (
    hash_compute,
    hash_file,
    hmac_compute,
    hmac_verify,
    pbkdf2_hash,
    pbkdf2_verify,
    bcrypt_hash,
    bcrypt_verify,
    hash_verify_integrity,
    generate_random_bytes,
    BCRYPT_AVAILABLE,
)
from cryptolab.banner import warn_weak_hash, print_warning

from cryptolab import InvalidInputError
from cryptolab import log_history
from cryptolab.cli.formatters import render_box, render_error


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def handle_hash(args: Namespace) -> int:
    """Handle hash command."""
    try:
        history_enabled = _get_history_enabled(args)
        algo = args.algorithm.upper()
        enc = args.encoding.lower()

        # Show warning for weak hash algorithms
        warning = warn_weak_hash(algo)
        if warning:
            print_warning(warning)

        if args.action == "compute":
            if not args.text:
                raise InvalidInputError("Operasi compute memerlukan parameter --text / -t.")
            res = hash_compute(args.text, algorithm=algo, encoding=enc)
            print(
                render_box(
                    f"Hasil Hash {algo}",
                    f"{algo} Hash (COMPUTE)",
                    args.text,
                    res.output_hash,
                    {"Algorithm": algo, "Encoding": enc.upper()},
                )
            )
            log_history(f"Hash {algo} Compute", args.text, res.output_hash, {"algo": algo, "encoding": enc}, enabled=history_enabled)
            return 0

        elif args.action == "file":
            if not args.file:
                raise InvalidInputError("Operasi file memerlukan parameter --file / -f.")
            res = hash_file(args.file, algorithm=algo)
            print(
                render_box(
                    f"Hasil Hash File {algo}",
                    f"{algo} Hash (FILE)",
                    args.file,
                    res.output_hash,
                    {"Algorithm": algo, "File": args.file},
                )
            )
            log_history(f"Hash {algo} File", args.file, res.output_hash, {"algo": algo, "filepath": args.file}, enabled=history_enabled)
            return 0

        elif args.action == "verify":
            if not args.text or not args.expected:
                raise InvalidInputError("Operasi verify memerlukan --text / -t dan --expected.")
            res = hash_verify_integrity(args.text, args.expected, algorithm=algo, encoding=enc)
            status = "VALID" if res.match else "INVALID"
            print(
                render_box(
                    f"Verifikasi Integritas {algo}",
                    f"{algo} Verify ({status})",
                    args.text,
                    "COCOK" if res.match else "TIDAK COCOK",
                    {"Algorithm": algo, "Expected": args.expected, "Status": status},
                )
            )
            log_history(f"Hash {algo} Verify", args.text, "COCOK" if res.match else "TIDAK COCOK", {"algo": algo, "match": res.match}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0


def handle_hmac(args: Namespace) -> int:
    """Handle hmac command."""
    try:
        history_enabled = _get_history_enabled(args)
        algo = args.algorithm.upper()
        enc = args.encoding.lower()

        if args.action == "compute":
            res = hmac_compute(args.text, args.key, algorithm=algo, encoding=enc)
            print(
                render_box(
                    f"Hasil HMAC-{algo}",
                    f"HMAC-{algo} (COMPUTE)",
                    args.text,
                    res.output_hmac,
                    {"Algorithm": f"HMAC-{algo}", "Key Length": f"{len(args.key)} bytes", "Encoding": enc.upper()},
                )
            )
            log_history(f"HMAC-{algo} Compute", args.text, res.output_hmac, {"algo": algo, "encoding": enc}, enabled=history_enabled)
            return 0

        elif args.action == "verify":
            if not args.expected:
                raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
            match = hmac_verify(args.text, args.key, args.expected, algorithm=algo, encoding=enc)
            status = "VALID" if match else "INVALID"
            print(
                render_box(
                    f"Verifikasi HMAC-{algo}",
                    f"HMAC-{algo} Verify ({status})",
                    args.text,
                    "COCOK" if match else "TIDAK COCOK",
                    {"Algorithm": f"HMAC-{algo}", "Status": status},
                )
            )
            log_history(f"HMAC-{algo} Verify", args.text, "COCOK" if match else "TIDAK COCOK", {"algo": algo, "match": match}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0


def handle_pbkdf2(args: Namespace) -> int:
    """Handle pbkdf2 command."""
    try:
        history_enabled = _get_history_enabled(args)
        algo = args.algorithm.upper()
        enc = args.encoding.lower()

        if args.action == "hash":
            res = pbkdf2_hash(args.password, salt=args.salt, iterations=args.iterations, algorithm=algo, dklen=args.dklen, encoding=enc)
            print(
                render_box(
                    f"Hasil PBKDF2-{algo}",
                    f"PBKDF2-{algo} (HASH)",
                    "********",
                    f"Salt: {res.salt}\nHash: {res.hash_value}",
                    {"Algorithm": f"PBKDF2-{algo}", "Iterations": f"{res.iterations:,}", "DKLen": f"{args.dklen} bytes", "Encoding": enc.upper()},
                )
            )
            log_history(f"PBKDF2-{algo} Hash", "********", res.hash_value, {"algo": algo, "iterations": args.iterations, "salt": res.salt}, enabled=history_enabled)
            return 0

        elif args.action == "verify":
            if not args.expected:
                raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
            res = pbkdf2_verify(args.password, args.salt, args.expected, iterations=args.iterations, algorithm=algo, dklen=args.dklen, encoding=enc)
            status = "COCOK" if res.match else "TIDAK COCOK"
            print(
                render_box(
                    f"Verifikasi PBKDF2-{algo}",
                    f"PBKDF2-{algo} Verify ({status})",
                    "********",
                    status,
                    {"Algorithm": f"PBKDF2-{algo}", "Status": status},
                )
            )
            log_history(f"PBKDF2-{algo} Verify", "********", status, {"algo": algo, "match": res.match}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0


def handle_bcrypt(args: Namespace) -> int:
    """Handle bcrypt command."""
    try:
        if not BCRYPT_AVAILABLE:
            print(render_error("Bcrypt", "Bcrypt tidak tersedia (bcrypt package not installed)."), file=sys.stderr)
            return 1

        history_enabled = _get_history_enabled(args)

        if args.action == "hash":
            res = bcrypt_hash(args.password, rounds=args.rounds)
            print(
                render_box(
                    "Hasil Bcrypt",
                    f"BCRYPT (HASH)",
                    "********",
                    res.hash_value,
                    {"Algorithm": "BCRYPT", "Rounds": res.iterations},
                )
            )
            log_history("Bcrypt Hash", "********", res.hash_value, {"rounds": args.rounds}, enabled=history_enabled)
            return 0

        elif args.action == "verify":
            if not args.expected:
                raise InvalidInputError("Operasi verify memerlukan parameter --expected.")
            res = bcrypt_verify(args.password, args.expected)
            status = "COCOK" if res.match else "TIDAK COCOK"
            print(
                render_box(
                    "Verifikasi Bcrypt",
                    f"BCRYPT Verify ({status})",
                    "********",
                    status,
                    {"Algorithm": "BCRYPT", "Status": status},
                )
            )
            log_history("Bcrypt Verify", "********", status, {"match": res.match}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0


def handle_random(args: Namespace) -> int:
    """Handle random command."""
    try:
        history_enabled = _get_history_enabled(args)
        length = args.length
        enc = args.encoding.lower()
        out = generate_random_bytes(length, encoding=enc)
        print(
            render_box(
                "Random Bytes",
                f"Random ({length} bytes, {enc.upper()})",
                "",
                out,
                {"Length": f"{length} bytes", "Encoding": enc.upper()},
            )
        )
        log_history("Random Bytes", "", out, {"length": length, "encoding": enc}, enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1