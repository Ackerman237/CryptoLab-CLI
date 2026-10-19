"""DES implementation. Backward compatibility."""

from cryptolab.core.symmetric.des import des_encrypt, des_decrypt, des_auto_analyze, DesResult

__all__ = ["des_encrypt", "des_decrypt", "des_auto_analyze", "DesResult"]