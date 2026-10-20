"""Symmetric cryptography module (RC2, DES, and AES block ciphers)."""

from .des import (
    des_encrypt,
    des_decrypt,
    des_auto_analyze,
    DesResult,
)
from .aes import (
    aes_encrypt,
    aes_decrypt,
    aes_auto_analyze,
    AesResult,
)
from .rc2 import (
    rc2_encrypt,
    rc2_decrypt,
    rc2_auto_analyze,
    Rc2Result,
)

__all__ = [
    "des_encrypt",
    "des_decrypt",
    "des_auto_analyze",
    "DesResult",
    "aes_encrypt",
    "aes_decrypt",
    "aes_auto_analyze",
    "AesResult",
    "rc2_encrypt",
    "rc2_decrypt",
    "rc2_auto_analyze",
    "Rc2Result",
]