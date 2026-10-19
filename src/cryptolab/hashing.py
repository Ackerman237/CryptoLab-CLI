"""Cryptographic Hashing Module for CryptoLab.

Supports standard hash functions (MD5, SHA-1, SHA-256, SHA-512),
HMAC for message authentication, and password hashing (PBKDF2, bcrypt).
"""

import hashlib
import hmac
import secrets
import binascii
from dataclasses import dataclass, field
from typing import List, Optional, Union

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

from cryptolab.exceptions import (
    CryptoLabError,
    InvalidInputError,
    DecodingError,
)


@dataclass
class HashResult:
    """Result of a hashing operation."""
    algorithm: str
    input_text: str
    output_hash: str
    is_hex: bool = True
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class HMACResult:
    """Result of an HMAC operation."""
    algorithm: str
    message: str
    key_repr: str
    output_hmac: str
    is_hex: bool = True
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


@dataclass
class PasswordHashResult:
    """Result of password hashing operation."""
    algorithm: str
    password_repr: str
    salt: str
    hash_value: str
    iterations: int
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


@dataclass
class VerifyPasswordResult:
    """Result of password verification."""
    algorithm: str
    match: bool
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)


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


def hash_compute(
    data: Union[str, bytes],
    algorithm: str = "SHA256",
    encoding: str = "hex",
) -> HashResult:
    """Compute cryptographic hash of input data.

    Args:
        data: Input string or bytes to hash.
        algorithm: Hash algorithm (MD5, SHA1, SHA256, SHA512).
        encoding: Output encoding: "hex" (default) or "base64".

    Returns:
        HashResult with the computed hash.

    Raises:
        InvalidInputError: If algorithm is not supported.
    """
    data_bytes = _to_bytes(data, "Data")
    algo = algorithm.upper().strip()

    hash_funcs = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
    }

    if algo not in hash_funcs:
        raise InvalidInputError(
            f"Algoritma hash tidak didukung: '{algorithm}'. "
            f"Gunakan: {', '.join(hash_funcs.keys())}"
        )

    hasher = hash_funcs[algo]()
    hasher.update(data_bytes)
    digest = hasher.digest()

    if encoding.lower() == "base64":
        import base64
        output = base64.b64encode(digest).decode("ascii")
        is_hex = False
    else:
        output = digest.hex()
        is_hex = True

    return HashResult(
        algorithm=algo,
        input_text=data_bytes.decode("utf-8", errors="replace")[:100],
        output_hash=output,
        is_hex=is_hex,
        technical_success=True,
        status_message=f"Hash {algo} berhasil dihitung.",
        reasons=[f"Output dalam format {encoding.upper()}"],
        metadata={"encoding": encoding.upper(), "length_bytes": len(digest)},
    )


def hash_file(filepath: str, algorithm: str = "SHA256") -> HashResult:
    """Compute hash of a file."""
    algo = algorithm.upper().strip()
    hash_funcs = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
    }
    if algo not in hash_funcs:
        raise InvalidInputError(f"Algoritma tidak didukung: {algorithm}")

    hasher = hash_funcs[algo]()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
    except OSError as e:
        raise InvalidInputError(f"Gagal membaca file: {e}")

    return HashResult(
        algorithm=algo,
        input_text=f"[FILE] {filepath}",
        output_hash=hasher.hexdigest(),
        is_hex=True,
        technical_success=True,
        status_message=f"Hash file {algo} berhasil.",
        reasons=["File dibaca dalam chunk 8KB"],
        metadata={"filepath": filepath},
    )


def hmac_compute(
    message: Union[str, bytes],
    key: Union[str, bytes],
    algorithm: str = "SHA256",
    encoding: str = "hex",
) -> HMACResult:
    """Compute HMAC (Hash-based Message Authentication Code).

    Args:
        message: Message to authenticate.
        key: Secret key.
        algorithm: Hash algorithm for HMAC (MD5, SHA1, SHA256, SHA512).
        encoding: Output encoding: "hex" (default) or "base64".

    Returns:
        HMACResult with the computed HMAC.
    """
    msg_bytes = _to_bytes(message, "Message")
    key_bytes = _to_bytes(key, "Key")
    algo = algorithm.upper().strip()

    hash_funcs = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
    }

    if algo not in hash_funcs:
        raise InvalidInputError(
            f"Algoritma HMAC tidak didukung: '{algorithm}'. "
            f"Gunakan: {', '.join(hash_funcs.keys())}"
        )

    h = hmac.new(key_bytes, msg_bytes, hash_funcs[algo])
    digest = h.digest()

    if encoding.lower() == "base64":
        import base64
        output = base64.b64encode(digest).decode("ascii")
        is_hex = False
    else:
        output = digest.hex()
        is_hex = True

    return HMACResult(
        algorithm=f"HMAC-{algo}",
        message=msg_bytes.decode("utf-8", errors="replace")[:100],
        key_repr=key_bytes.decode("utf-8", errors="replace")[:50],
        output_hmac=output,
        is_hex=is_hex,
        technical_success=True,
        status_message=f"HMAC-{algo} berhasil dihitung.",
        reasons=[f"Key length: {len(key_bytes)} bytes", f"Output: {encoding.upper()}"],
    )


def hmac_verify(
    message: Union[str, bytes],
    key: Union[str, bytes],
    expected_hmac: str,
    algorithm: str = "SHA256",
    encoding: str = "hex",
) -> bool:
    """Verify HMAC using constant-time comparison."""
    computed = hmac_compute(message, key, algorithm, encoding)
    if encoding.lower() == "base64":
        import base64
        expected_bytes = base64.b64decode(expected_hmac)
        computed_bytes = base64.b64decode(computed.output_hmac)
    else:
        expected_bytes = bytes.fromhex(expected_hmac)
        computed_bytes = bytes.fromhex(computed.output_hmac)
    return hmac.compare_digest(expected_bytes, computed_bytes)


def pbkdf2_hash(
    password: str,
    salt: Optional[Union[str, bytes]] = None,
    iterations: int = 100000,
    algorithm: str = "SHA256",
    dklen: int = 32,
    encoding: str = "hex",
) -> PasswordHashResult:
    """Hash password using PBKDF2 (Password-Based Key Derivation Function 2).

    Args:
        password: Password string to hash.
        salt: Optional salt as raw bytes or hex string (random if not provided).
        iterations: Iteration count (default: 100,000).
        algorithm: Hash algorithm (SHA256, SHA512).
        dklen: Derived key length in bytes (default: 32).
        encoding: Output encoding: "hex" (default) or "base64".

    Returns:
        PasswordHashResult with salt and derived key.
    """
    pwd_bytes = _to_bytes(password, "Password")
    algo = algorithm.upper().strip()

    if algo not in ("SHA256", "SHA512"):
        raise InvalidInputError("PBKDF2 mendukung SHA256 atau SHA512 saja.")

    if salt is None:
        salt_bytes = secrets.token_bytes(16)
    else:
        salt_bytes = _decode_salt(salt, encoding)

    if len(salt_bytes) < 8:
        raise InvalidInputError("Salt minimal 8 bytes.")

    if iterations < 100000:
        raise InvalidInputError("Iterations minimal 100,000 (rekomendasi OWASP 2024).")

    hash_name = "sha256" if algo == "SHA256" else "sha512"
    derived = hashlib.pbkdf2_hmac(hash_name, pwd_bytes, salt_bytes, iterations, dklen=dklen)

    if encoding.lower() == "base64":
        import base64
        hash_output = base64.b64encode(derived).decode("ascii")
        salt_output = base64.b64encode(salt_bytes).decode("ascii")
        is_hex = False
    else:
        hash_output = derived.hex()
        salt_output = salt_bytes.hex()
        is_hex = True

    return PasswordHashResult(
        algorithm=f"PBKDF2-{algo}",
        password_repr="********",
        salt=salt_output,
        hash_value=hash_output,
        iterations=iterations,
        technical_success=True,
        status_message=f"PBKDF2-{algo} hash berhasil dibuat ({iterations:,} iterasi).",
        reasons=[f"Salt: {len(salt_bytes)} bytes", f"DKLen: {dklen} bytes", f"Output: {encoding.upper()}"],
    )


def _decode_salt(salt: Union[str, bytes], encoding: str) -> bytes:
    """Decode salt from hex/base64 string or use raw bytes."""
    if isinstance(salt, bytes):
        return salt
    salt_str = salt.strip()
    if encoding.lower() == "base64":
        import base64
        try:
            return base64.b64decode(salt_str)
        except Exception:
            pass  # Fall through to try as raw bytes
    else:
        # Try hex decode
        if all(c in "0123456789abcdefABCDEF" for c in salt_str) and len(salt_str) % 2 == 0:
            try:
                return bytes.fromhex(salt_str)
            except Exception:
                pass
    # Fallback: treat as raw UTF-8 string
    return salt_str.encode("utf-8")


def pbkdf2_verify(
    password: str,
    salt: Union[str, bytes],
    expected_hash: str,
    iterations: int = 100000,
    algorithm: str = "SHA256",
    dklen: int = 32,
    encoding: str = "hex",
) -> VerifyPasswordResult:
    """Verify a PBKDF2 password hash."""
    if iterations < 100000:
        raise InvalidInputError("Iterations minimal 100,000 (rekomendasi OWASP 2024).")
    
    # Decode salt from hex/base64 if needed
    salt_bytes = _decode_salt(salt, encoding)
    
    pwd_bytes = _to_bytes(password, "Password")
    algo = algorithm.upper().strip()
    hash_name = "sha256" if algo == "SHA256" else "sha512"
    derived = hashlib.pbkdf2_hmac(hash_name, pwd_bytes, salt_bytes, iterations, dklen=dklen)

    if encoding.lower() == "base64":
        import base64
        computed_hash = base64.b64encode(derived).decode("ascii")
        match = hmac.compare_digest(
            base64.b64decode(expected_hash),
            base64.b64decode(computed_hash)
        )
    else:
        computed_hash = derived.hex()
        match = hmac.compare_digest(expected_hash, computed_hash)

    return VerifyPasswordResult(
        algorithm=f"PBKDF2-{algorithm.upper()}",
        match=match,
        technical_success=True,
        status_message="Password cocok." if match else "Password TIDAK cocok.",
        reasons=["Konstanta-time comparison digunakan" if match else "Hash tidak sesuai"],
    )


def bcrypt_hash(
    password: str,
    rounds: int = 12,
) -> PasswordHashResult:
    """Hash password using bcrypt (slow, adaptive hash)."""
    if not BCRYPT_AVAILABLE:
        raise CryptoLabError("bcrypt tidak tersedia. Install: pip install bcrypt")

    pwd_bytes = _to_bytes(password, "Password")
    if rounds < 4 or rounds > 31:
        raise InvalidInputError("Bcrypt rounds harus 4-31.")

    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt(rounds))
    return PasswordHashResult(
        algorithm="BCRYPT",
        password_repr="********",
        salt=hashed[:29].decode("ascii"),
        hash_value=hashed.decode("ascii"),
        iterations=rounds,
        technical_success=True,
        status_message=f"Bcrypt hash berhasil (rounds={rounds}).",
        reasons=["Adaptive hash dengan salt otomatis", "Cocok untuk penyimpanan password"],
    )


def bcrypt_verify(password: str, hashed: str) -> VerifyPasswordResult:
    """Verify a bcrypt password hash."""
    if not BCRYPT_AVAILABLE:
        raise CryptoLabError("bcrypt tidak tersedia. Install: pip install bcrypt")

    pwd_bytes = _to_bytes(password, "Password")
    hashed_bytes = _to_bytes(hashed, "Hash")
    match = bcrypt.checkpw(pwd_bytes, hashed_bytes)

    return VerifyPasswordResult(
        algorithm="BCRYPT",
        match=match,
        technical_success=True,
        status_message="Password cocok." if match else "Password TIDAK cocok.",
        reasons=["Konstanta-time comparison" if match else "Hash tidak sesuai"],
    )


def hash_verify_integrity(
    data: Union[str, bytes],
    expected_hash: str,
    algorithm: str = "SHA256",
    encoding: str = "hex",
) -> VerifyPasswordResult:
    """Verify data integrity against expected hash."""
    computed = hash_compute(data, algorithm, encoding)
    if encoding.lower() == "base64":
        import base64
        match = hmac.compare_digest(
            base64.b64decode(expected_hash),
            base64.b64decode(computed.output_hash)
        )
    else:
        match = hmac.compare_digest(expected_hash, computed.output_hash)

    return VerifyPasswordResult(
        algorithm=algorithm.upper(),
        match=match,
        technical_success=True,
        status_message="Integritas TERVERIFIKASI." if match else "Integritas GAGAL - Data dimodifikasi!",
        reasons=["Hash cocok" if match else "Hash tidak sesuai dengan data"],
    )


def generate_random_bytes(length: int = 32, encoding: str = "hex") -> str:
    """Generate cryptographically secure random bytes."""
    if length < 1 or length > 1024:
        raise InvalidInputError("Panjang 1-1024 bytes.")
    random_bytes = secrets.token_bytes(length)
    if encoding.lower() == "base64":
        import base64
        return base64.b64encode(random_bytes).decode("ascii")
    return random_bytes.hex()


SUPPORTED_HASH_ALGOS = ["MD5", "SHA1", "SHA256", "SHA512"]
SUPPORTED_HMAC_ALGOS = ["HMAC-MD5", "HMAC-SHA1", "HMAC-SHA256", "HMAC-SHA512"]
SUPPORTED_PBKDF2_ALGOS = ["PBKDF2-SHA256", "PBKDF2-SHA512"]
SUPPORTED_PASSWORD_ALGOS = ["PBKDF2-SHA256", "PBKDF2-SHA512"] + (["BCRYPT"] if BCRYPT_AVAILABLE else [])


__all__ = [
    "hash_compute",
    "hash_file",
    "hmac_compute",
    "hmac_verify",
    "pbkdf2_hash",
    "pbkdf2_verify",
    "bcrypt_hash",
    "bcrypt_verify",
    "hash_verify_integrity",
    "generate_random_bytes",
    "HashResult",
    "HMACResult",
    "PasswordHashResult",
    "VerifyPasswordResult",
    "SUPPORTED_HASH_ALGOS",
    "SUPPORTED_HMAC_ALGOS",
    "SUPPORTED_PBKDF2_ALGOS",
    "SUPPORTED_PASSWORD_ALGOS",
    "BCRYPT_AVAILABLE",
]