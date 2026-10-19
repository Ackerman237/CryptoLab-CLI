"""Asymmetric command handlers (RSA, DH)."""

import sys
from argparse import Namespace

from cryptolab.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
)
from cryptolab.banner import warn_rsa_pkcs1v15, print_warning

from cryptolab import InvalidInputError
from cryptolab import log_history
from cryptolab.cli.formatters import render_box, render_error


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def _clean_hex(s: str) -> str:
    """Clean hex string from whitespace and prefixes."""
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        s = s[2:]
    return s.replace(" ", "").replace("\n", "").replace("\r", "")


def _load_key(key_arg: str, is_private: bool) -> str:
    """Load key from file or use inline."""
    if key_arg is None:
        return None
    if key_arg.startswith("-----BEGIN"):
        return key_arg
    try:
        with open(key_arg, "r") as f:
            return f.read().strip()
    except OSError:
        return key_arg


def handle_rsa(args: Namespace) -> int:
    """Handle rsa command."""
    try:
        history_enabled = _get_history_enabled(args)
        action = args.action
        enc = args.encoding.lower()
        padding = args.padding.upper()
        hash_algo = args.hash.upper()
        sig_padding = args.sigpadding.upper()

        # Warning for PKCS#1 v1.5
        if padding == "PKCS1V15" or sig_padding == "PKCS1V15":
            print_warning(warn_rsa_pkcs1v15())

        if action == "keygen":
            kp = rsa_generate_keypair(args.keysize)
            print(
                render_box(
                    f"RSA {args.keysize}-bit Key Pair",
                    "RSA Key Generation",
                    "",
                    f"PRIVATE KEY:\n{kp.private_key_pem}\n\nPUBLIC KEY:\n{kp.public_key_pem}",
                    {"Key Size": f"{args.keysize} bit"},
                )
            )
            log_history(f"RSA KeyGen {args.keysize}", "", "KEYPAIR GENERATED", {"keysize": args.keysize}, enabled=history_enabled)
            return 0

        elif action == "encrypt":
            if not args.text:
                raise InvalidInputError("Encrypt memerlukan --text / -t.")
            if not args.pubkey:
                raise InvalidInputError("Encrypt memerlukan --pubkey.")
            pubkey = _load_key(args.pubkey, is_private=False)
            res = rsa_encrypt(args.text, pubkey, padding=padding, hash_algo=hash_algo, encoding=enc)
            print(
                render_box(
                    f"Hasil RSA Enkripsi",
                    f"RSA-{res.algorithm} (ENCRYPT)",
                    args.text,
                    res.output_text,
                    {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Encoding": enc.upper()},
                )
            )
            log_history(f"RSA Encrypt", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
            return 0

        elif action == "decrypt":
            if not args.text:
                raise InvalidInputError("Decrypt memerlukan --text / -t (ciphertext).")
            if not args.privkey:
                raise InvalidInputError("Decrypt memerlukan --privkey.")
            privkey = _load_key(args.privkey, is_private=True)
            res = rsa_decrypt(args.text, privkey, padding=padding, hash_algo=hash_algo, encoding=enc)
            print(
                render_box(
                    f"Hasil RSA Dekripsi",
                    f"RSA-{res.algorithm} (DECRYPT)",
                    f"[{len(args.text)} chars ciphertext]",
                    res.output_text,
                    {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": "UTF-8" if not res.is_hex else "Hex"},
                )
            )
            log_history(f"RSA Decrypt", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
            return 0

        elif action == "sign":
            if not args.text:
                raise InvalidInputError("Sign memerlukan --text / -t (message).")
            if not args.privkey:
                raise InvalidInputError("Sign memerlukan --privkey.")
            privkey = _load_key(args.privkey, is_private=True)
            res = rsa_sign(args.text, privkey, padding=sig_padding, hash_algo=hash_algo, encoding=enc)
            print(
                render_box(
                    f"Hasil RSA Sign",
                    f"RSA-{res.algorithm} (SIGN)",
                    args.text,
                    res.output_text,
                    {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Encoding": enc.upper()},
                )
            )
            log_history(f"RSA Sign", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
            return 0

        elif action == "verify":
            if not args.text:
                raise InvalidInputError("Verify memerlukan --text / -t (message).")
            if not args.pubkey:
                raise InvalidInputError("Verify memerlukan --pubkey.")
            if not args.signature:
                raise InvalidInputError("Verify memerlukan --signature.")
            pubkey = _load_key(args.pubkey, is_private=False)
            res = rsa_verify(args.text, args.signature, pubkey, padding=sig_padding, hash_algo=hash_algo, encoding=enc)
            status = "VALID (SAH)" if "VALID" in res.output_text else "INVALID (TIDAK SAH)"
            print(
                render_box(
                    f"Verifikasi RSA Signature",
                    f"RSA-{res.algorithm} (VERIFY)",
                    args.text,
                    res.output_text,
                    {"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": status},
                )
            )
            log_history(f"RSA Verify", args.text, res.output_text, {"algo": res.algorithm}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0


def handle_dh(args: Namespace) -> int:
    """Handle dh command."""
    try:
        history_enabled = _get_history_enabled(args)
        action = args.action
        enc = args.encoding.lower()
        hash_algo = args.hash.upper()

        if action == "exchange":
            alice_priv = None
            bob_priv = None
            if args.alice_priv:
                alice_priv = int(_clean_hex(args.alice_priv), 16)
            if args.bob_priv:
                bob_priv = int(_clean_hex(args.bob_priv), 16)

            res = dh_key_exchange(args.bits, alice_private=alice_priv, bob_private=bob_priv)
            output = (
                f"Prime (p): {res.prime_hex[:64]}... ({len(res.prime_hex)} hex chars)\n"
                f"Generator (g): {res.generator}\n\n"
                f"Alice Private: {res.alice_private_hex}\n"
                f"Alice Public:  {res.alice_public_hex}\n\n"
                f"Bob Private:   {res.bob_private_hex}\n"
                f"Bob Public:    {res.bob_public_hex}\n\n"
                f"SHARED SECRET: {res.shared_secret_hex}"
            )
            print(
                render_box(
                    f"DHKE {args.bits}-bit Exchange",
                    f"Diffie-Hellman Key Exchange",
                    "",
                    output,
                    {"Prime Size": f"{args.bits} bit", "Generator": str(res.generator)},
                )
            )
            log_history(f"DHKE {args.bits}", "", "EXCHANGE COMPLETE", {"bits": args.bits}, enabled=history_enabled)
            return 0

        elif action == "derive":
            if not args.shared:
                raise InvalidInputError("Derive memerlukan --shared (shared secret hex).")
            derived = dh_derive_key(args.shared, key_length=args.keylen, hash_algo=hash_algo)
            print(
                render_box(
                    f"DHKE Key Derivation",
                    f"HKDF-SHA{hash_algo[-3:]} Derive",
                    f"Shared Secret: {args.shared[:32]}...",
                    derived,
                    {"Key Length": f"{args.keylen} bytes", "Hash": hash_algo, "Encoding": enc.upper()},
                )
            )
            log_history(f"DHKE Derive", args.shared, derived, {"keylen": args.keylen, "hash": hash_algo}, enabled=history_enabled)
            return 0

    except InvalidInputError as err:
        print(render_error("Invalid Input", str(err)), file=sys.stderr)
        return 1
    return 0