"""Diffie-Hellman implementation. Backward compatibility."""

from cryptolab.core.asymmetric import dh_key_exchange, dh_derive_key, dh_generate_parameters, DHKeyExchangeResult

__all__ = ["dh_key_exchange", "dh_derive_key", "dh_generate_parameters", "DHKeyExchangeResult"]