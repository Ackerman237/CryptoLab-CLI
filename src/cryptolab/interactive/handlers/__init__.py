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

# ctx API handlers (baru)
from cryptolab.interactive.handlers.ctx_encoding import (
    fn_base64,
    fn_hex,
    fn_binary,
)
from cryptolab.interactive.handlers.ctx_analysis import (
    fn_auto,
)
from cryptolab.interactive.handlers.ctx_history import (
    fn_history,
)
from cryptolab.interactive.handlers.ctx_classical import (
    fn_caesar,
    fn_vigenere,
)
from cryptolab.interactive.handlers.ctx_symmetric import (
    fn_des,
    fn_aes,
    fn_rc2,
)
from cryptolab.interactive.handlers.ctx_hashing import (
    fn_hash,
)
from cryptolab.interactive.handlers.ctx_asymmetric import (
    fn_rsa,
    fn_dh,
)

__all__ = [
    # Classical (legacy)
    "handle_caesar",
    "handle_vigenere",
    "handle_playfair",
    "handle_hill",
    "handle_affine",
    "handle_railfence",
    # Symmetric (legacy)
    "handle_des",
    "handle_aes",
    "handle_rc2",
    # Hashing (legacy)
    "handle_hashing",
    # Asymmetric (legacy)
    "handle_rsa",
    "handle_dh",
    # Encoding (legacy)
    "handle_base64",
    "handle_hex",
    "handle_binary",
    # Analysis (legacy)
    "handle_auto_analyze",
    # History (legacy)
    "handle_history",
    # ctx API (baru)
    "fn_base64",
    "fn_hex",
    "fn_binary",
    "fn_auto",
    "fn_history",
    "fn_caesar",
    "fn_vigenere",
    "fn_des",
    "fn_aes",
    "fn_rc2",
    "fn_hash",
    "fn_rsa",
    "fn_dh",
]