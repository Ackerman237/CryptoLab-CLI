"""RSA implementation. Backward compatibility."""

from cryptolab.core.asymmetric import (
    rsa_generate_keypair,
    rsa_load_private_key,
    rsa_load_public_key,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    RSAKeyPair,
    RSAResult,
)

__all__ = [
    "rsa_generate_keypair",
    "rsa_load_private_key",
    "rsa_load_public_key",
    "rsa_encrypt",
    "rsa_decrypt",
    "rsa_sign",
    "rsa_verify",
    "RSAKeyPair",
    "RSAResult",
]