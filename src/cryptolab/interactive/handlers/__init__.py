"""Interactive Handlers package - individual feature handlers."""

from cryptolab.interactive.handlers.classical import (
    handle_caesar,
    handle_vigenere,
    handle_playfair,
    handle_hill,
    handle_affine,
    handle_railfence,
)
from cryptolab.interactive.handlers.symmetric import (
    handle_des,
    handle_aes,
    handle_rc2,
)
from cryptolab.interactive.handlers.hashing import (
    handle_hashing,
)
from cryptolab.interactive.handlers.asymmetric import (
    handle_rsa,
    handle_dh,
)
from cryptolab.interactive.handlers.encoding import (
    handle_base64,
    handle_hex,
    handle_binary,
)
from cryptolab.interactive.handlers.analysis import (
    handle_auto_analyze,
)
from cryptolab.interactive.handlers.history import (
    handle_history,
)

__all__ = [
    # Classical
    "handle_caesar",
    "handle_vigenere",
    "handle_playfair",
    "handle_hill",
    "handle_affine",
    "handle_railfence",
    # Symmetric
    "handle_des",
    "handle_aes",
    "handle_rc2",
    # Hashing
    "handle_hashing",
    # Asymmetric
    "handle_rsa",
    "handle_dh",
    # Encoding
    "handle_base64",
    "handle_hex",
    "handle_binary",
    # Analysis
    "handle_auto_analyze",
    # History
    "handle_history",
]