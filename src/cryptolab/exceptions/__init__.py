"""Custom exceptions for CryptoLab. Backward compatibility."""

from cryptolab.core.exceptions import (
    CryptoLabError,
    InvalidInputError,
    InvalidKeyError,
    DecodingError,
)

__all__ = [
    "CryptoLabError",
    "InvalidInputError",
    "InvalidKeyError",
    "DecodingError",
]