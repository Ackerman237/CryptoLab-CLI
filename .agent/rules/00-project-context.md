# Project Context - CryptoLab CLI

**Project:** CryptoLab CLI - Toolkit Kriptografi & Encoding untuk Praktikum Keamanan Informasi  
**Versi:** 1.0.0  
**Stack:** Python 3.9+, pycryptodome, readchar  
**Entry Point:** `cryptolab` (src/cryptolab/main.py)  
**Test:** `pytest tests/` (pythonpath=src)

---

## Struktur Folder Saat Ini

```
src/cryptolab/
├── main.py                 # Entry point (31 lines)
├── cli.py                  # CLI commands + UI (1,677 lines) ⚠️
├── interactive.py          # Interactive menu + handlers (3,281 lines) ⚠️
├── banner.py               # Logo, terminal utils (147 lines)
├── flow.py                 # Three-phase flow (298 lines)
├── asymmetric.py           # RSA, DH (576 lines)
├── hashing.py              # Hash, HMAC, PBKDF2, Bcrypt (504 lines)
├── classical/              # 6 classical ciphers
├── symmetric/              # DES, AES, RC2
├── encoding/               # Base64, Hex, Binary
├── analysis/               # Auto detect, pipeline, brute force
├── utils/                  # History, exceptions
└── exceptions.py           # Custom exceptions
```

---

## Target Architecture (lihat REFACTOR_PLAN.md)

```
src/cryptolab/
├── ui/                     # Design system (widgets, theme, layout)
├── cli/                    # CLI commands package
├── interactive/            # Interactive menu package
├── core/                   # Crypto core logic (extracted)
├── shared/                 # Config, exceptions, utils
└── flow.py                 # Refactored flow
```

---

## Sumber Kebenaran
- **Audit Report:** `docs/audit/AUDIT_REPORT.md`
- **Refactor Plan:** `docs/audit/REFACTOR_PLAN.md`
- **UI Inventory:** `docs/audit/UI_INVENTORY.md`
- **Progress:** `docs/audit/PROGRESS.md`

---

## Cara Menjalankan

```bash
# Development
pip install -e ".[dev]"
cryptolab menu              # Interactive mode
cryptolab caesar --help     # CLI mode

# Test
pytest tests/ -v

# Lint (after D2)
ruff check src/
mypy src/
black --check src/
```

---

## Catatan Penting
- File `interactive.py` (3,281 lines) dan `cli.py` (1,677 lines) adalah **god files** yang perlu dipecah
- 3 sistem UI terpisah (cli, interactive, banner) → konsolidasi ke `ui/`
- 4 algoritma crypto tanpa warning: MD5, SHA-1, ECB mode, RC2
- 30+ file `fix_*.py` di root = legacy cleanup scripts, boleh dihapus