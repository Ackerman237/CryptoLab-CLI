"""CLI Argument Parser - builds the command-line argument parser."""

import argparse
from typing import List

from cryptolab import __version__
from cryptolab.core.hashing import BCRYPT_AVAILABLE


def create_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser with all capabilities."""
    parser = argparse.ArgumentParser(
        prog="cryptolab",
        description="CryptoLab CLI - Toolkit Kriptografi Klasik & Encoding untuk Praktikum Keamanan Informasi",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Nonaktifkan pencatatan riwayat operasi ke file lokal",
    )

    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia", required=False)

    # Interactive menu
    subparsers.add_parser("menu", help="Buka antarmuka menu interaktif")

    # Caesar
    caesar_parser = subparsers.add_parser("caesar", help="Caesar Cipher operations")
    caesar_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "brute-force", "brute"],
        help="Aksi: encrypt, decrypt, atau brute-force",
    )
    caesar_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    caesar_parser.add_argument(
        "-s",
        "--shift",
        type=int,
        default=None,
        help="Nilai pergeseran integer (wajib untuk encrypt/decrypt)",
    )
    caesar_parser.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Tampilkan hanya kandidat terbaik berdasarkan skor heuristik",
    )

    # Brute Force Caesar (top-level shortcut)
    brute_parser = subparsers.add_parser(
        "brute", help="Caesar Cipher brute force (26 kandidat)"
    )
    brute_parser.add_argument(
        "-t", "--text", required=True, help="Ciphertext yang akan diuji"
    )
    brute_parser.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Tampilkan hanya kandidat terbaik berdasarkan skor heuristik",
    )

    # Vigenere
    vigenere_parser = subparsers.add_parser(
        "vigenere", help="Vigenere Cipher operations"
    )
    vigenere_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    vigenere_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    vigenere_parser.add_argument(
        "-k", "--key", required=True, help="Kunci alfabet untuk Vigenere"
    )

    # Playfair
    playfair_parser = subparsers.add_parser(
        "playfair", help="Playfair Cipher (Digram substitution 5x5 matrix)"
    )
    playfair_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    playfair_parser.add_argument(
        "-t", "--text", required=True, help="Plaintext (encrypt) atau ciphertext (decrypt)"
    )
    playfair_parser.add_argument(
        "-k", "--key", required=True, help="Kunci kata untuk matrix 5x5 (huruf A-Z)"
    )

    # Hill Cipher
    hill_parser = subparsers.add_parser(
        "hill", help="Hill Cipher (Matrix polygraphic substitution 2x2/3x3)"
    )
    hill_parser.add_argument(
        "action", choices=["encrypt", "decrypt"], help="Aksi: encrypt atau decrypt"
    )
    hill_parser.add_argument(
        "-t", "--text", required=True, help="Plaintext (encrypt) atau ciphertext (decrypt)"
    )
    hill_parser.add_argument(
        "-k", "--key", required=True, help="Key matrix space-separated (0-25). Contoh 2x2: '3 3 2 5'"
    )
    hill_parser.add_argument(
        "-s", "--size", type=int, default=2, choices=[2, 3], help="Ukuran matrix: 2 (2x2) atau 3 (3x3)"
    )

    # Affine Cipher
    affine_parser = subparsers.add_parser(
        "affine", help="Affine Cipher E(x) = (ax + b) mod 26"
    )
    affine_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "brute"], help="Aksi: encrypt, decrypt, atau brute-force"
    )
    affine_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    affine_parser.add_argument(
        "-a", "--mult", type=int, required=False, help="Kunci perkalian 'a' (harus coprime dengan 26: 1,3,5,7,9,11,15,17,19,21,23,25)"
    )
    affine_parser.add_argument(
        "-b", "--add", type=int, required=False, help="Kunci penjumlahan 'b' (0-25)"
    )

    # Rail Fence
    railfence_parser = subparsers.add_parser(
        "railfence", help="Rail Fence / Transposition Cipher (Zig-zag)"
    )
    railfence_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "brute"], help="Aksi: encrypt, decrypt, atau brute-force"
    )
    railfence_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    railfence_parser.add_argument(
        "-r", "--rails", type=int, default=2, help="Jumlah rail (minimal 2)"
    )
    railfence_parser.add_argument(
        "--max-rails", type=int, default=10, help="Maksimal rail untuk brute-force (default: 10)"
    )

    # Base64
    b64_parser = subparsers.add_parser("base64", help="Base64 encode/decode")
    b64_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    b64_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )

    # Hexadecimal
    hex_parser = subparsers.add_parser("hex", help="Hexadecimal encode/decode")
    hex_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    hex_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    hex_parser.add_argument(
        "-d",
        "--delimiter",
        default=" ",
        help="Pemisah byte heksadesimal pada encode (default: spasi)",
    )

    # Binary
    bin_parser = subparsers.add_parser("binary", help="8-bit Binary encode/decode")
    bin_parser.add_argument(
        "action", choices=["encode", "decode"], help="Aksi: encode atau decode"
    )
    bin_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan diproses"
    )
    bin_parser.add_argument(
        "-d",
        "--delimiter",
        default=" ",
        help="Pemisah byte biner pada encode (default: spasi)",
    )

    # Analyze (Fase 2)
    analyze_parser = subparsers.add_parser(
        "analyze", help="Auto detect encoding & analisis format (Binary / Hex / Base64)"
    )
    analyze_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan dianalisis formatnya"
    )

    # Detect (Fase 1 alias)
    detect_parser = subparsers.add_parser(
        "detect", help="Deteksi format (Binary / Hex / Base64)"
    )
    detect_parser.add_argument(
        "-t", "--text", required=True, help="Teks yang akan dianalisis formatnya"
    )

    # Auto-decode
    auto_parser = subparsers.add_parser(
        "auto", help="Multi-stage auto-decode pipeline untuk encoding bertingkat"
    )
    auto_parser.add_argument(
        "-t", "--text", required=True, help="Teks bertingkat yang akan di-decode"
    )
    auto_parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=5,
        help="Batas kedalaman maksimal transformasi (default: 5)",
    )

    # History (Fase 2)
    hist_parser = subparsers.add_parser(
        "history", help="Kelola dan lihat riwayat analisis lokal"
    )
    hist_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=15,
        help="Jumlah entri riwayat terbaru yang ditampilkan (default: 15)",
    )
    hist_parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Hapus seluruh catatan riwayat analisis lokal",
    )

    # DES (CBC / ECB)
    des_parser = subparsers.add_parser(
        "des", help="Operasi DES (Data Encryption Standard) CBC/ECB"
    )
    des_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    des_parser.add_argument(
        "-t",
        "--text",
        required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    des_parser.add_argument(
        "-k",
        "--key",
        default=None,
        help="Kunci DES sepanjang tepat 8 byte/karakter",
    )
    des_parser.add_argument(
        "-m",
        "--mode",
        default="CBC",
        choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode DES: CBC atau ECB (default: CBC)",
    )
    des_parser.add_argument(
        "--iv",
        default=None,
        help="Initialization Vector (IV) untuk mode CBC (tepat 8 byte)",
    )
    des_parser.add_argument(
        "-p",
        "--padding",
        default="PKCS7",
        choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )

    # AES (CBC / ECB)
    aes_parser = subparsers.add_parser(
        "aes", help="Operasi AES (Advanced Encryption Standard) 128-bit CBC/ECB"
    )
    aes_parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    aes_parser.add_argument(
        "-t",
        "--text",
        required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    aes_parser.add_argument(
        "-k",
        "--key",
        default=None,
        help="Kunci AES sepanjang 16 byte/karakter (AES-128)",
    )
    aes_parser.add_argument(
        "-m",
        "--mode",
        default="CBC",
        choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode AES: CBC atau ECB (default: CBC)",
    )
    aes_parser.add_argument(
        "--iv",
        default=None,
        help="Initialization Vector (IV) untuk mode CBC (tepat 16 byte)",
    )
    aes_parser.add_argument(
        "-p",
        "--padding",
        default="PKCS7",
        choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )

    # RC2 / ARC2 (CBC / ECB)
    rc2_parser = subparsers.add_parser(
        "rc2", help="Operasi RC2 (ARC2) CBC/ECB untuk kompatibilitas cipher legacy"
    )
    rc2_parser.add_argument(
        "action", choices=["encrypt", "decrypt", "auto"],
        help="Aksi: encrypt, decrypt, atau auto",
    )
    rc2_parser.add_argument(
        "-t", "--text", required=True,
        help="Plaintext (encrypt) atau ciphertext heksadesimal (decrypt/auto)",
    )
    rc2_parser.add_argument("-k", "--key", default=None, help="Kunci RC2 sepanjang 5-16 byte")
    rc2_parser.add_argument(
        "-m", "--mode", default="CBC", choices=["CBC", "ECB", "cbc", "ecb"],
        help="Mode RC2: CBC atau ECB (default: CBC)",
    )
    rc2_parser.add_argument("--iv", default=None, help="IV CBC sepanjang tepat 8 byte")
    rc2_parser.add_argument(
        "-p", "--padding", default="PKCS7", choices=["PKCS7", "None", "pkcs7", "none"],
        help="Skema padding: PKCS7 (default) atau None",
    )
    rc2_parser.add_argument(
        "--effective-keylen", type=int, default=128,
        help="Effective key length RC2 dalam bit (default: 128; rentang 40-1024)",
    )

    # Hash (MD5, SHA1, SHA256, SHA512)
    hash_parser = subparsers.add_parser("hash", help="Hash kriptografis (MD5, SHA1, SHA256, SHA512)")
    hash_parser.add_argument(
        "action", choices=["compute", "file", "verify"],
        help="Aksi: compute (string), file (hash file), verify (verifikasi integritas)"
    )
    hash_parser.add_argument(
        "-t", "--text", default=None, help="Input string untuk compute/verify"
    )
    hash_parser.add_argument(
        "-f", "--file", default=None, help="Path file untuk hash file"
    )
    hash_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["MD5", "SHA1", "SHA256", "SHA512"],
        help="Algoritma hash (default: SHA256)"
    )
    hash_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    hash_parser.add_argument(
        "--expected", default=None, help="Hash yang diharapkan untuk verify"
    )

    # HMAC
    hmac_parser = subparsers.add_parser("hmac", help="HMAC (Hash-based Message Authentication Code)")
    hmac_parser.add_argument(
        "action", choices=["compute", "verify"],
        help="Aksi: compute atau verify"
    )
    hmac_parser.add_argument(
        "-t", "--text", required=True, help="Pesan untuk HMAC"
    )
    hmac_parser.add_argument(
        "-k", "--key", required=True, help="Kunci rahasia"
    )
    hmac_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["MD5", "SHA1", "SHA256", "SHA512"],
        help="Algoritma HMAC (default: SHA256)"
    )
    hmac_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    hmac_parser.add_argument(
        "--expected", default=None, help="HMAC yang diharapkan untuk verify"
    )

    # PBKDF2
    pbkdf2_parser = subparsers.add_parser("pbkdf2", help="PBKDF2 password hashing")
    pbkdf2_parser.add_argument(
        "action", choices=["hash", "verify"],
        help="Aksi: hash password atau verify password"
    )
    pbkdf2_parser.add_argument(
        "-p", "--password", required=True, help="Password"
    )
    pbkdf2_parser.add_argument(
        "-s", "--salt", default=None, help="Salt (hex atau base64, random jika kosong)"
    )
    pbkdf2_parser.add_argument(
        "-i", "--iterations", type=int, default=100000, help="Jumlah iterasi (default: 100000)"
    )
    pbkdf2_parser.add_argument(
        "-a", "--algorithm", default="SHA256", choices=["SHA256", "SHA512"],
        help="Algoritma PBKDF2 (default: SHA256)"
    )
    pbkdf2_parser.add_argument(
        "--dklen", type=int, default=32, help="Panjang derived key dalam byte (default: 32)"
    )
    pbkdf2_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    pbkdf2_parser.add_argument(
        "--expected", default=None, help="Hash yang diharapkan untuk verify"
    )

    # Bcrypt (if available)
    if BCRYPT_AVAILABLE:
        bcrypt_parser = subparsers.add_parser("bcrypt", help="Bcrypt password hashing (adaptive)")
        bcrypt_parser.add_argument(
            "action", choices=["hash", "verify"],
            help="Aksi: hash password atau verify password"
        )
        bcrypt_parser.add_argument(
            "-p", "--password", required=True, help="Password"
        )
        bcrypt_parser.add_argument(
            "-r", "--rounds", type=int, default=12, help="Cost factor/rounds (4-31, default: 12)"
        )
        bcrypt_parser.add_argument(
            "--expected", default=None, help="Hash bcrypt untuk verify"
        )

    # Random bytes generator
    random_parser = subparsers.add_parser("random", help="Generate cryptographically secure random bytes")
    random_parser.add_argument(
        "-l", "--length", type=int, default=32, help="Panjang byte (default: 32, max: 1024)"
    )
    random_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )

    # RSA (Asymmetric Cryptography)
    rsa_parser = subparsers.add_parser("rsa", help="RSA Asymmetric Cryptography (KeyGen, Encrypt, Decrypt, Sign, Verify)")
    rsa_parser.add_argument(
        "action", choices=["keygen", "encrypt", "decrypt", "sign", "verify"],
        help="Aksi: keygen, encrypt, decrypt, sign, verify"
    )
    rsa_parser.add_argument(
        "-t", "--text", default=None, help="Plaintext (encrypt) / ciphertext (decrypt) / message (sign/verify)"
    )
    rsa_parser.add_argument(
        "--pubkey", default=None, help="Public key PEM (file path atau inline)"
    )
    rsa_parser.add_argument(
        "--privkey", default=None, help="Private key PEM (file path atau inline)"
    )
    rsa_parser.add_argument(
        "-k", "--keysize", type=int, default=2048, choices=[1024, 2048, 3072, 4096],
        help="Key size untuk keygen (default: 2048)"
    )
    rsa_parser.add_argument(
        "-p", "--padding", default="OAEP", choices=["OAEP", "PKCS1v15", "oaep", "pkcs1v15"],
        help="Padding scheme (default: OAEP)"
    )
    rsa_parser.add_argument(
        "--hash", default="SHA256", choices=["SHA256", "SHA512"],
        help="Hash algorithm untuk OAEP/PSS (default: SHA256)"
    )
    rsa_parser.add_argument(
        "--sigpadding", default="PSS", choices=["PSS", "PKCS1v15", "pss", "pkcs1v15"],
        help="Signature padding (default: PSS)"
    )
    rsa_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )
    rsa_parser.add_argument(
        "--signature", default=None, help="Signature untuk verify (hex/base64)"
    )

    # Diffie-Hellman Key Exchange
    dh_parser = subparsers.add_parser("dh", help="Diffie-Hellman Key Exchange (DHKE)")
    dh_parser.add_argument(
        "action", choices=["exchange", "derive"],
        help="Aksi: exchange (simulasi Alice-Bob), derive (derive key dari shared secret)"
    )
    dh_parser.add_argument(
        "-b", "--bits", type=int, default=2048, choices=[2048, 3072, 4096],
        help="Prime size dalam bit (default: 2048)"
    )
    dh_parser.add_argument(
        "--alice-priv", default=None, help="Alice private key (opsional, hex)"
    )
    dh_parser.add_argument(
        "--bob-priv", default=None, help="Bob private key (opsional, hex)"
    )
    dh_parser.add_argument(
        "--shared", default=None, help="Shared secret hex (untuk derive)"
    )
    dh_parser.add_argument(
        "--keylen", type=int, default=32, help="Derived key length dalam byte (default: 32)"
    )
    dh_parser.add_argument(
        "--hash", default="SHA256", choices=["SHA256", "SHA512"],
        help="Hash algorithm untuk key derivation (default: SHA256)"
    )
    dh_parser.add_argument(
        "--encoding", default="hex", choices=["hex", "base64"],
        help="Format output (default: hex)"
    )

    return parser


def _clean_hex(s: str) -> str:
    """Clean hex string from whitespace and prefixes."""
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        s = s[2:]
    return s.replace(" ", "").replace("\n", "").replace("\r", "")