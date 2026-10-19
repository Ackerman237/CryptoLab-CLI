"""Asymmetric cryptography module (RSA, DH). Backward compatibility."""

from cryptolab.core.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
    RSAKeyPair,
    RSAResult,
    DHKeyExchangeResult,
)

__all__ = [
    "rsa_generate_keypair",
    "rsa_encrypt",
    "rsa_decrypt",
    "rsa_sign",
    "rsa_verify",
    "dh_key_exchange",
    "dh_derive_key",
    "RSAKeyPair",
    "RSAResult",
    "DHKeyExchangeResult",
]