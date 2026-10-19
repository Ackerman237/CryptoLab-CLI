"""Custom exceptions for CryptoLab CLI."""


class CryptoLabError(Exception):
    """Base exception for all CryptoLab errors."""
    pass


class InvalidInputError(CryptoLabError):
    """Raised when user input is empty, null, or malformed."""
    pass


class InvalidKeyError(CryptoLabError):
    """Raised when an encryption/decryption key is invalid or incompatible."""
    pass


class DecodingError(CryptoLabError):
    """Raised when data decoding (Base64, Hex, Binary) fails."""
    pass
