"""Asymmetric Cryptography Module for CryptoLab.

Supports RSA (key generation, encryption, decryption, signing, verification)
and Diffie-Hellman Key Exchange (DHKE).
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256, SHA512

from cryptolab.core.exceptions import (
    CryptoLabError,
    InvalidInputError,
    DecodingError,
)


@dataclass
class RSAKeyPair:
    """RSA key pair container."""
    private_key_pem: str
    public_key_pem: str
    key_size: int
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


@dataclass
class RSAResult:
    """Result of RSA operation."""
    operation: str  # "encrypt", "decrypt", "sign", "verify"
    algorithm: str  # "RSA-OAEP", "RSA-PKCS1v15", "RSA-PSS"
    input_text: str
    output_text: str
    key_size: int
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)
    is_hex: bool = True


@dataclass
class DHKeyExchangeResult:
    """Result of Diffie-Hellman Key Exchange."""
    prime_hex: str
    generator: int
    alice_private_hex: str
    alice_public_hex: str
    bob_private_hex: str
    bob_public_hex: str
    shared_secret_hex: str
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)

    # Properties for backward compatibility with tests
    @property
    def alice_shared(self) -> str:
        return self.shared_secret_hex

    @property
    def bob_shared(self) -> str:
        return self.shared_secret_hex


def _to_bytes(data: Union[str, bytes], name: str) -> bytes:
    """Safely convert a string or bytes input to bytes."""
    if data is None:
        raise InvalidInputError(f"{name} tidak boleh None.")
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    raise InvalidInputError(f"{name} harus berupa string atau bytes.")


def _clean_hex(hex_str: str) -> str:
    """Clean and validate hexadecimal string."""
    if hex_str is None or not isinstance(hex_str, str):
        raise InvalidInputError("Input heksadesimal tidak valid.")

    cleaned = hex_str.strip()
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    cleaned = cleaned.replace(" ", "").replace(":", "").replace("-", "")

    if len(cleaned) == 0:
        raise InvalidInputError("Input heksadesimal tidak boleh kosong.")

    if not all(c in "0123456789abcdefABCDEF" for c in cleaned):
        raise DecodingError("Input mengandung karakter bukan heksadesimal.")

    if len(cleaned) % 2 != 0:
        raise DecodingError(f"Panjang heksadesimal ganjil ({len(cleaned)}). Harus genap.")

    return cleaned


def rsa_generate_keypair(key_size: int = 2048) -> RSAKeyPair:
    """Generate RSA key pair.

    Args:
        key_size: Key size in bits (1024, 2048, 3072, 4096).

    Returns:
        RSAKeyPair with private and public keys in PEM format.
    """
    if key_size not in (1024, 2048, 3072, 4096):
        raise InvalidInputError("Key size harus 1024, 2048, 3072, atau 4096 bit.")

    key = RSA.generate(key_size)
    private_pem = key.export_key("PEM").decode("ascii")
    public_pem = key.publickey().export_key("PEM").decode("ascii")

    return RSAKeyPair(
        private_key_pem=private_pem,
        public_key_pem=public_pem,
        key_size=key_size,
        technical_success=True,
        status_message=f"RSA {key_size}-bit key pair berhasil dibuat.",
        reasons=["Private key: simpan dengan aman", "Public key: bisa dibagikan"],
    )


def rsa_load_private_key(pem_data: str) -> RSA.RsaKey:
    """Load RSA private key from PEM string."""
    try:
        return RSA.import_key(pem_data)
    except Exception as e:
        raise InvalidInputError(f"Gagal memuat private key: {e}")


def rsa_load_public_key(pem_data: str) -> RSA.RsaKey:
    """Load RSA public key from PEM string."""
    try:
        return RSA.import_key(pem_data)
    except Exception as e:
        raise InvalidInputError(f"Gagal memuat public key: {e}")


def _warn_pkcs1v15(operation: str) -> str:
    """Return warning for PKCS1v15 padding."""
    return f"PERINGATAN: RSA-PKCS1v15 {operation} rentan terhadap padding oracle attacks. Gunakan OAEP (encrypt) / PSS (sign) untuk keamanan."

def rsa_encrypt(
    plaintext: Union[str, bytes],
    public_key_pem: str,
    padding: str = "OAEP",
    hash_algo: str = "SHA256",
    encoding: str = "hex",
) -> RSAResult:
    """Encrypt data using RSA public key.

    Args:
        plaintext: Data to encrypt.
        public_key_pem: Public key in PEM format.
        padding: Padding scheme "OAEP" (default) or "PKCS1v15".
        hash_algo: Hash algorithm for OAEP (SHA256, SHA512).
        encoding: Output encoding "hex" (default) or "base64".

    Returns:
        RSAResult with ciphertext.
    """
    data = _to_bytes(plaintext, "Plaintext")
    public_key = rsa_load_public_key(public_key_pem)

    max_size = public_key.size_in_bytes()
    if padding.upper() == "OAEP":
        # OAEP overhead: 2 * hash_len + 2
        hash_len = 32 if hash_algo.upper() == "SHA256" else 64
        max_data = max_size - 2 * hash_len - 2
    else:
        # PKCS1v15 overhead: 11 bytes
        max_data = max_size - 11

    if len(data) > max_data:
        raise InvalidInputError(
            f"Plaintext terlalu panjang ({len(data)} bytes). "
            f"Maksimal untuk {padding} dengan {hash_algo}: {max_data} bytes. "
            f"Gunakan hybrid encryption untuk data besar."
        )

    if padding.upper() == "OAEP":
        hash_obj = SHA256.new() if hash_algo.upper() == "SHA256" else SHA512.new()
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=hash_obj)
        algo_name = f"RSA-OAEP-{hash_algo.upper()}"
    else:
        cipher = PKCS1_v1_5.new(public_key)
        algo_name = "RSA-PKCS1v15"

    ciphertext = cipher.encrypt(data)

    if encoding.lower() == "base64":
        import base64
        output = base64.b64encode(ciphertext).decode("ascii")
        is_hex = False
    else:
        output = ciphertext.hex()
        is_hex = True

    reasons = [f"Key size: {public_key.size_in_bits()} bit", f"Padding: {padding}", f"Output: {encoding.upper()}"]
    if padding.upper() != "OAEP":
        reasons.append("PERINGATAN: PKCS1v15 rentan terhadap padding oracle. Gunakan OAEP.")

    return RSAResult(
        operation="encrypt",
        algorithm=algo_name,
        input_text=plaintext if isinstance(plaintext, str) else f"[{len(data)} bytes]",
        output_text=output,
        key_size=public_key.size_in_bits(),
        technical_success=True,
        status_message=f"Enkripsi {algo_name} berhasil.",
        reasons=reasons,
        is_hex=is_hex,
    )


def rsa_decrypt(
    ciphertext: str,
    private_key_pem: str,
    padding: str = "OAEP",
    hash_algo: str = "SHA256",
    encoding: str = "hex",
) -> RSAResult:
    """Decrypt data using RSA private key.

    Args:
        ciphertext: Ciphertext in hex or base64.
        private_key_pem: Private key in PEM format.
        padding: Padding scheme "OAEP" (default) or "PKCS1v15".
        hash_algo: Hash algorithm for OAEP (SHA256, SHA512).
        encoding: Input encoding "hex" (default) or "base64".

    Returns:
        RSAResult with plaintext.
    """
    # Decode ciphertext based on encoding
    if encoding.lower() == "base64":
        import base64
        try:
            ct_bytes = base64.b64decode(ciphertext)
        except Exception as e:
            raise DecodingError(f"Invalid base64 ciphertext: {e}")
    else:
        clean_hex = _clean_hex(ciphertext)
        ct_bytes = bytes.fromhex(clean_hex)

    private_key = rsa_load_private_key(private_key_pem)

    if padding.upper() == "OAEP":
        hash_obj = SHA256.new() if hash_algo.upper() == "SHA256" else SHA512.new()
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=hash_obj)
        algo_name = f"RSA-OAEP-{hash_algo.upper()}"
    else:
        cipher = PKCS1_v1_5.new(private_key)
        algo_name = "RSA-PKCS1v15"

    try:
        if padding.upper() == "OAEP":
            plaintext = cipher.decrypt(ct_bytes)
        else:
            # PKCS1_v1_5 requires a sentinel for decrypt
            sentinel = b"DECRYPTION_FAILED"
            plaintext = cipher.decrypt(ct_bytes, sentinel)
            if plaintext == sentinel:
                raise ValueError("Decryption failed")
    except ValueError as e:
        raise DecodingError(f"Dekripsi gagal: {e}. Periksa key dan padding.")

    try:
        output = plaintext.decode("utf-8")
        is_utf8 = True
    except UnicodeDecodeError:
        output = plaintext.hex()
        is_utf8 = False

    reasons = [f"Key size: {private_key.size_in_bits()} bit", f"Padding: {padding}", "UTF-8 valid" if is_utf8 else "Output hex"]
    if padding.upper() != "OAEP":
        reasons.append("PERINGATAN: PKCS1v15 rentan terhadap padding oracle. Gunakan OAEP.")

    return RSAResult(
        operation="decrypt",
        algorithm=algo_name,
        input_text=f"[{len(ct_bytes)} bytes ciphertext]",
        output_text=output,
        key_size=private_key.size_in_bits(),
        technical_success=True,
        status_message=f"Dekripsi {algo_name} berhasil." + ("" if is_utf8 else " (Output bukan UTF-8, ditampilkan hex)"),
        reasons=reasons,
        is_hex=not is_utf8,
    )


def rsa_sign(
    message: Union[str, bytes],
    private_key_pem: str,
    padding: str = "PSS",
    hash_algo: str = "SHA256",
    encoding: str = "hex",
) -> RSAResult:
    """Sign message using RSA private key.

    Args:
        message: Message to sign.
        private_key_pem: Private key in PEM format.
        padding: Signature padding "PSS" (default) or "PKCS1v15".
        hash_algo: Hash algorithm (SHA256, SHA512).
        encoding: Output encoding "hex" (default) or "base64".

    Returns:
        RSAResult with signature.
    """
    data = _to_bytes(message, "Message")
    private_key = rsa_load_private_key(private_key_pem)

    hash_obj = SHA256.new(data) if hash_algo.upper() == "SHA256" else SHA512.new(data)

    if padding.upper() == "PSS":
        from Crypto.Signature import pss
        signer = pss.new(private_key)
        algo_name = f"RSA-PSS-{hash_algo.upper()}"
    else:
        signer = pkcs1_15.new(private_key)
        algo_name = f"RSA-PKCS1v15-{hash_algo.upper()}"

    signature = signer.sign(hash_obj)

    if encoding.lower() == "base64":
        import base64
        output = base64.b64encode(signature).decode("ascii")
        is_hex = False
    else:
        output = signature.hex()
        is_hex = True

    reasons = [f"Key size: {private_key.size_in_bits()} bit", f"Hash: {hash_algo}", f"Padding: {padding}"]
    if padding.upper() != "PSS":
        reasons.append("PERINGATAN: PKCS1v15 signature rentan terhadap forgery. Gunakan PSS.")

    return RSAResult(
        operation="sign",
        algorithm=algo_name,
        input_text=message if isinstance(message, str) else f"[{len(data)} bytes]",
        output_text=output,
        key_size=private_key.size_in_bits(),
        technical_success=True,
        status_message=f"Tanda tangan {algo_name} berhasil dibuat.",
        reasons=reasons,
        is_hex=is_hex,
    )


def rsa_verify(
    message: Union[str, bytes],
    signature_hex: str,
    public_key_pem: str,
    padding: str = "PSS",
    hash_algo: str = "SHA256",
    encoding: str = "hex",
) -> RSAResult:
    """Verify RSA signature.

    Args:
        message: Original message.
        signature_hex: Signature in hex or base64.
        public_key_pem: Public key in PEM format.
        padding: Signature padding "PSS" (default) or "PKCS1v15".
        hash_algo: Hash algorithm (SHA256, SHA512).
        encoding: Input encoding "hex" (default) or "base64".

    Returns:
        RSAResult with verification result.
    """
    data = _to_bytes(message, "Message")
    public_key = rsa_load_public_key(public_key_pem)

    if encoding.lower() == "base64":
        import base64
        try:
            signature = base64.b64decode(signature_hex)
        except Exception as e:
            raise DecodingError(f"Invalid base64 signature: {e}")
    else:
        clean_sig = _clean_hex(signature_hex)
        try:
            signature = bytes.fromhex(clean_sig)
        except ValueError as e:
            raise DecodingError(f"Invalid hex signature: {e}")

    hash_obj = SHA256.new(data) if hash_algo.upper() == "SHA256" else SHA512.new(data)

    if padding.upper() == "PSS":
        from Crypto.Signature import pss
        verifier = pss.new(public_key)
        algo_name = f"RSA-PSS-{hash_algo.upper()}"
    else:
        verifier = pkcs1_15.new(public_key)
        algo_name = f"RSA-PKCS1v15-{hash_algo.upper()}"

    try:
        verifier.verify(hash_obj, signature)
        valid = True
        status = "VALID (Tanda tangan SAH)"
    except (ValueError, TypeError):
        valid = False
        status = "INVALID (Tanda tangan TIDAK SAH)"

    reasons = ["Verifikasi berhasil" if valid else "Tanda tangan tidak cocok"]
    if padding.upper() != "PSS":
        reasons.append("PERINGATAN: PKCS1v15 signature rentan terhadap forgery. Gunakan PSS.")

    return RSAResult(
        operation="verify",
        algorithm=algo_name,
        input_text=message if isinstance(message, str) else f"[{len(data)} bytes]",
        output_text=status,
        key_size=public_key.size_in_bits(),
        technical_success=True,
        status_message=status,
        reasons=reasons,
        is_hex=False,
    )


def dh_generate_parameters(key_size: int = 2048) -> Tuple[int, int]:
    """Generate DH parameters (prime p, generator g).

    Args:
        key_size: Size of prime in bits (2048, 3072, 4096).

    Returns:
        Tuple of (prime, generator).
    """
    # Use standard RFC 3526 groups
    if key_size == 2048:
        # RFC 3526 Group 14 (2048-bit)
        p = int(
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
            "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
            "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
            "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)
        g = 2
    elif key_size == 3072:
        # RFC 3526 Group 15 (3072-bit)
        p = int(
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
            "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
            "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
            "15728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64"
            "ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7"
            "ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6B"
            "F12FFA06D98A0864D87602733EC86A64521F2B18177B200C"
            "BBE117577A615D6C770988C0BAD946E208E24FA074E5AB31"
            "43DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF", 16)
        g = 2
    else:
        # 4096-bit (RFC 3526 Group 16)
        p = int(
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
            "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
            "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
            "15728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64"
            "ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7"
            "ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6B"
            "F12FFA06D98A0864D87602733EC86A64521F2B18177B200C"
            "BBE117577A615D6C770988C0BAD946E208E24FA074E5AB31"
            "43DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF", 16)
        g = 2
    return p, g


def dh_key_exchange(
    prime_bits: int = 2048,
    alice_private: Optional[int] = None,
    bob_private: Optional[int] = None,
) -> DHKeyExchangeResult:
    """Simulate Diffie-Hellman Key Exchange between Alice and Bob.

    Args:
        prime_bits: Size of prime (2048, 3072, 4096).
        alice_private: Alice's private key (random if None).
        bob_private: Bob's private key (random if None).

    Returns:
        DHKeyExchangeResult with all parameters and shared secret.
    """
    p, g = dh_generate_parameters(prime_bits)

    # Generate private keys
    if alice_private is None:
        alice_private = secrets.randbelow(p - 2) + 2
    if bob_private is None:
        bob_private = secrets.randbelow(p - 2) + 2

    # Compute public keys: g^private mod p
    alice_public = pow(g, alice_private, p)
    bob_public = pow(g, bob_private, p)

    # Compute shared secrets
    alice_shared = pow(bob_public, alice_private, p)
    bob_shared = pow(alice_public, bob_private, p)

    assert alice_shared == bob_shared, "Shared secret mismatch!"

    shared = alice_shared

    # Ensure hex strings have even length (pad with leading zero if needed)
    def to_even_hex(n: int) -> str:
        h = hex(n)[2:]
        return h if len(h) % 2 == 0 else "0" + h

    return DHKeyExchangeResult(
        prime_hex=to_even_hex(p),
        generator=g,
        alice_private_hex=to_even_hex(alice_private),
        alice_public_hex=to_even_hex(alice_public),
        bob_private_hex=to_even_hex(bob_private),
        bob_public_hex=to_even_hex(bob_public),
        shared_secret_hex=to_even_hex(shared),
        technical_success=True,
        status_message=f"DHKE {prime_bits}-bit berhasil. Shared secret: {len(to_even_hex(shared))} hex chars.",
        reasons=[
            f"Prime: {prime_bits} bit (RFC 3526 Group)",
            f"Generator: {g}",
            "Alice & Bob shared secret MATCH",
        ],
    )


def dh_derive_key(
    shared_secret_hex: str,
    key_length: int = 32,
    hash_algo: str = "SHA256",
) -> str:
    """Derive symmetric key from DH shared secret using HKDF-like approach.

    Args:
        shared_secret_hex: Shared secret from DHKE.
        key_length: Desired key length in bytes.
        hash_algo: Hash algorithm (SHA256, SHA512).

    Returns:
        Derived key as hex string.
    """
    secret_bytes = bytes.fromhex(_clean_hex(shared_secret_hex))
    
    # Simple key derivation: hash the shared secret
    if hash_algo.upper() == "SHA256":
        hasher = hashlib.sha256
    else:
        hasher = hashlib.sha512

    derived = b""
    counter = 1
    while len(derived) < key_length:
        h = hasher()
        h.update(secret_bytes + counter.to_bytes(4, "big"))
        derived += h.digest()
        counter += 1

    return derived[:key_length].hex()


__all__ = [
    "rsa_generate_keypair",
    "rsa_load_private_key",
    "rsa_load_public_key",
    "rsa_encrypt",
    "rsa_decrypt",
    "rsa_sign",
    "rsa_verify",
    "dh_generate_parameters",
    "dh_key_exchange",
    "dh_derive_key",
    "RSAKeyPair",
    "RSAResult",
    "DHKeyExchangeResult",
]