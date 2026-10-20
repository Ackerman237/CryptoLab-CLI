"""AES implementation. Backward compatibility."""

from cryptolab.core.symmetric.aes import aes_encrypt, aes_decrypt, aes_auto_analyze, AesResult

__all__ = ["aes_encrypt", "aes_decrypt", "aes_auto_analyze", "AesResult"]