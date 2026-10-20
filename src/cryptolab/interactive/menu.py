"""Interactive main menu definition."""

from cryptolab.banner import format_subtitle
from cryptolab.ui import Menu
from cryptolab.interactive.handlers import (
    handle_auto_analyze,
    handle_caesar,
    handle_vigenere,
    handle_des,
    handle_aes,
    handle_rc2,
    handle_hashing,
    handle_rsa,
    handle_dh,
    handle_base64,
    handle_hex,
    handle_binary,
    handle_history,
)

# Main menu labels (for display)
MAIN_MENU_LABELS = [
    "Auto Analyze",
    "Caesar Cipher",
    "Vigenere Cipher",
    "DES",
    "AES",
    "RC2",
    "Hashing & Password",
    "RSA",
    "Diffie-Hellman",
    "Base64",
    "Hex",
    "Binary",
    "Riwayat",
]

# Corresponding handlers
MAIN_MENU_HANDLERS = [
    handle_auto_analyze,
    handle_caesar,
    handle_vigenere,
    handle_des,
    handle_aes,
    handle_rc2,
    handle_hashing,
    handle_rsa,
    handle_dh,
    handle_base64,
    handle_hex,
    handle_binary,
    handle_history,
]


def get_main_menu_labels() -> list:
    """Get the main menu labels."""
    return MAIN_MENU_LABELS


def get_main_menu_handlers() -> list:
    """Get the main menu handlers."""
    return MAIN_MENU_HANDLERS


def get_header_subtitle() -> str:
    """Get the header subtitle."""
    return format_subtitle()