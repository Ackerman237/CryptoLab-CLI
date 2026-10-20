"""CLI Commands package - individual command handlers."""

from cryptolab.cli.commands.classical import (
    handle_caesar,
    handle_brute,
    handle_vigenere,
    handle_playfair,
    handle_hill,
    handle_affine,
    handle_railfence,
)
from cryptolab.cli.commands.encoding import (
    handle_base64,
    handle_hex,
    handle_binary,
)
from cryptolab.cli.commands.analysis import (
    handle_analyze,
    handle_detect,
    handle_auto,
)
from cryptolab.cli.commands.history import handle_history
from cryptolab.cli.commands.symmetric import (
    handle_des,
    handle_aes,
    handle_aes_gcm,
    handle_rc2,
)
from cryptolab.cli.commands.hashing import (
    handle_hash,
    handle_hmac,
    handle_pbkdf2,
    handle_bcrypt,
    handle_random,
)
from cryptolab.cli.commands.asymmetric import (
    handle_rsa,
    handle_dh,
)

__all__ = [
    # Classical
    "handle_caesar",
    "handle_brute",
    "handle_vigenere",
    "handle_playfair",
    "handle_hill",
    "handle_affine",
    "handle_railfence",
    # Encoding
    "handle_base64",
    "handle_hex",
    "handle_binary",
    # Analysis
    "handle_analyze",
    "handle_detect",
    "handle_auto",
    # History
    "handle_history",
    # Symmetric
    "handle_des",
    "handle_aes",
    "handle_aes_gcm",
    "handle_rc2",
    # Hashing
    "handle_hash",
    "handle_hmac",
    "handle_pbkdf2",
    "handle_bcrypt",
    "handle_random",
    # Asymmetric
    "handle_rsa",
    "handle_dh",
]