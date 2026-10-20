# CryptoLab CLI - Audit Report

**Tanggal Audit:** 2026-10-19  
**Versi Project:** 1.0.0  
**Auditor:** Senior Engineer (Automated + Manual Review)

---

## 1. Ringkasan Eksekutif

### Project Overview
CryptoLab CLI adalah toolkit kriptografi dan encoding berbasis Python CLI untuk praktikum keamanan informasi. Mendukung:
- Classical Ciphers (Caesar, Vigenere, Playfair, Hill, Affine, Rail Fence)
- Symmetric Encryption (DES, AES, RC2)
- Asymmetric Crypto (RSA, Diffie-Hellman)
- Hashing & Password Security (MD5, SHA, HMAC, PBKDF2, Bcrypt)
- Encoding (Base64, Hex, Binary)
- Auto Analysis & Brute Force
- Interactive Menu System

### Stack Teknis
- **Bahasa:** Python 3.9+
- **Dependencies:** pycryptodome>=3.15.0, readchar>=4.0.0
- **Testing:** pytest
- **Entry Point:** `cryptolab` (via `src/cryptolab/main.py`)
- **OS Target:** Cross-platform (Windows, Linux, macOS)

### Status Git
- Branch: `main` (up to date with origin)
- Uncommitted changes: `src/cryptolab/banner.py`, `src/cryptolab/interactive.py` (recent UI fixes)
- Banyak file `fix_*.py` untracked di root (script perbaikan indent legacy)

---

## 2. Metrik Struktur Codebase

### File Terbesar (Lines of Code)
| File | Lines | Kategori | Status |
|------|-------|----------|--------|
| `src/cryptolab/interactive.py` | **3,281** | UI/Menu System | ⚠️ **Sangat Besar** (>800) |
| `src/cryptolab/cli.py` | **1,677** | CLI/Presentation | ⚠️ **Besar** (>800) |
| `src/cryptolab/asymmetric.py` | 576 | Asymmetric Crypto | OK |
| `src/cryptolab/hashing.py` | 504 | Hashing/Password | OK |
| `src/cryptolab/analysis/auto_engine.py` | 417 | Auto Analysis | OK |
| `src/cryptolab/symmetric/aes.py` | 348 | Symmetric Crypto | OK |
| `src/cryptolab/symmetric/des.py` | 347 | Symmetric Crypto | OK |
| `src/cryptolab/classical/hill.py` | 276 | Classical Cipher | OK |

**Total Python Source:** ~8,500 lines (src/cryptolab/)  
**Total Test Code:** ~2,400 lines (tests/)

### File di Atas 800 Baris (Perlu Decomposisi)
1. **`interactive.py` (3,281 lines)** - Menggabungkan: menu system, navigation, semua handler fitur (14+), help system, render card, post-result menu
2. **`cli.py` (1,677 lines)** - Menggabungkan: argparse setup, semua CLI command handlers, UI formatters (render_box, render_error, render_brute_force, dll)

---

## 3. Analisis Arsitektur

### Pola Arsitektur Saat Ini
```
src/cryptolab/
├── main.py              # Entry point (31 lines)
├── cli.py               # CLI commands + UI formatters (1,677 lines) ⚠️
├── interactive.py       # Interactive menu + ALL handlers (3,281 lines) ⚠️
├── banner.py            # Logo, terminal utils, header/footer (147 lines)
├── flow.py              # Three-phase flow (298 lines)
├── asymmetric.py        # RSA, DH (576 lines)
├── hashing.py           # Hash, HMAC, PBKDF2, Bcrypt (504 lines)
├── banner.py            # Logo, terminal utils (147 lines)
├── classical/           # 6 classical ciphers (~900 lines total)
├── symmetric/           # DES, AES, RC2 (~860 lines total)
├── encoding/            # Base64, Hex, Binary (~270 lines total)
├── analysis/            # Auto detect, pipeline, brute force (~1,100 lines total)
├── utils/               # History, exceptions (~150 lines total)
└── exceptions.py        # Custom exceptions (21 lines)
```

### Masalah Arsitektur Utama

#### 1. **God File: `interactive.py` (3,281 lines)**
- **Tanggung jawab:** Menu rendering, keyboard navigation, 14+ feature handlers, help system, result rendering, post-result flow
- **Violasi SRP:** Menangani UI, I/O, business logic, dan flow control sekaligus
- **Duplikasi:** Handler CLI dan Interactive sering memanggil fungsi yang sama tapi dengan UI berbeda

#### 2. **God File: `cli.py` (1,677 lines)**
- **Tanggung jawab:** Argparse setup, 20+ subcommand handlers, UI formatters (box, error, brute force, detection, auto decode, pipeline, history)
- **Campuran concern:** Parsing argumen + rendering output + memanggil logika kripto

#### 3. **Circular Import Risk**
- `cli.py` import dari `interactive.py` (run_interactive_menu)
- `interactive.py` import dari `cli` modules (tidak langsung tapi via shared modules)
- `flow.py` import dari `cli` modules

#### 4. **UI Logic Tersebar**
- `banner.py`: Logo, header, footer, terminal control
- `cli.py`: `render_box`, `render_error`, `render_brute_force`, `render_detection`, `render_auto_decode`, `render_pipeline_result`, `render_history_list`, `DIVIDER`, `THIN_DIVIDER`
- `interactive.py`: `render_card`, `render_footer`, `navigation_menu`, `center_block`, `color_text`, `bold/cyan/green/yellow/red/emphasis/muted`, `post_result_menu`, `save_result_prompt`
- **Tidak ada design system terpusat** - warna, simbol, pembatas, margin didefinisikan ulang di 3 file

---

## 4. Temuan Keamanan (Crypto-Specific)

### Critical/High Severity

| # | Temuan | File:Line | Severity | Confidence | Penjelasan |
|---|--------|-----------|----------|------------|------------|
| 1 | **MD5/SHA-1 tersedia tanpa peringatan** | `hashing.py` | **HIGH** | 95% | `hash_compute` mendukung `md5`, `sha1` tanpa warning deprecated. Digunakan untuk kompatibilitas tapi tidak ada banner peringatan. |
| 2 | **Mode ECB default di DES/AES/RC2** | `des.py:105`, `aes.py:112`, `rc2.py:98` | **HIGH** | 90% | CBC butuh IV, ECB tidak. Default mode di beberapa fungsi adalah ECB yang tidak aman untuk data >1 block. |
| 3 | **RC2 (ARC2) legacy cipher** | `symmetric/rc2.py` | **MEDIUM** | 100% | RC2 deprecated since 2015. Disediakan untuk kompatibilitas legacy tapi tidak ada warning saat dipilih. |
| 4 | **Non-constant-time hash compare** | `hashing.py:280` | **MEDIUM** | 85% | `hmac_verify` dan `hash_verify_integrity` menggunakan `==` bukan `hmac.compare_digest` |
| 5 | **Key/IV validation lemah** | `des.py`, `aes.py`, `rc2.py` | **MEDIUM** | 80% | Validasi panjang key/IV ada tapi error handling bisa bocorkan info panjang via exception message |
| 6 | **Password/key masuk history log** | `utils/history.py:45` | **MEDIUM** | 75% | `log_history` menyimpan `params` yang bisa berisi key/IV. Default `include_secrets=False` tapi caller bisa override. |

### Medium/Low Severity

| # | Temuan | File:Line | Severity | Penjelasan |
|---|--------|-----------|----------|------------|
| 7 | **PBKDF2 default iterations rendah** | `hashing.py:340` | LOW | Default 100,000 iterasi (OK untuk 2024) tapi tidak enforce minimum |
| 8 | **Bcrypt cost default 12** | `hashing.py:380` | LOW | Cost 12 OK tapi tidak ada validasi range 4-31 |
| 9 | **Random bytes pake `secrets`** | `hashing.py:420` | LOW | `generate_random_bytes` menggunakan `secrets.token_bytes` ✓ (sudah benar) |
| 10 | **RSA PKCS#1 v1.5 default** | `asymmetric.py` | MEDIUM | OAEP/PSS direkomendasikan tapi v1.5 masih tersedia tanpa warning eksplisit |

---

## 5. Analisis Kualitas Kode

### Duplikasi Kode
| Pola | Lokasi | Estimasi Baris |
|------|--------|----------------|
| UI Divider (`"=" * 70`, `"-" * 70`) | `cli.py:66-67`, `interactive.py:65-66` | ~50 occurrences |
| Color helpers (`bold`, `cyan`, `green`, `red`, `yellow`, `emphasis`, `muted`) | `interactive.py:205-230` | ~30 uses |
| `render_footer` / hint rendering | `banner.py:96`, `interactive.py:244` | 2 implementations |
| `center_block` | `banner.py:58`, `interactive.py:184` | 2 implementations |
| Result rendering (`render_box` vs `render_card`) | `cli.py:70`, `interactive.py:273` | 2 similar systems |

### Dead Code / Legacy
- **30+ file `fix_*.py`** di root directory - script perbaikan indent legacy, seharusnya dihapus atau diarsipkan
- `interactive.py` memiliki `LOGO_LARGE`, `LOGO_MEDIUM`, `LOGO_TINY`, `_PIXEL_FONT`, `_build_pixel_logo` yang **tidak dipakai** (sudah pakai `banner.py` version)

### Test Coverage
- **16 test files** covering: classical, symmetric, asymmetric, hashing, encoding, analysis, cli, interactive
- **Coverage gaps:** Tidak ada test untuk UI rendering, terminal interaction, history edge cases
- **Integration test minimal:** Hanya `test_cli.py` dan `test_interactive.py` yang test end-to-end

---

## 6. Skill & Tool yang Digunakan

| Tool/Skill | Status | Catatan |
|------------|--------|---------|
| Manual Code Review | ✅ Done | Phase 0-4 completed |
| `radon` (complexity) | ⏳ Planned | Butuh persetujuan install |
| `vulture` (dead code) | ⏳ Planned | Butuh persetujuan install |
| `import-linter` (circular) | ⏳ Planned | Butuh persetujuan install |
| `pydeps` / `pyreverse` | ⏳ Planned | Butuh persetujuan install |
| Open Code Review (OCR) | ⏳ Planned | Fase 1 - butuh `npm install -g @alibaba-group/open-code-review` |

---

## 7. File yang Dilewati / Tidak Di-audit

| File/Pattern | Alasan |
|--------------|--------|
| `.venv/` | Virtual environment, bukan source code |
| `__pycache__/` | Compiled bytecode |
| `fix_*.py` (30+ files) | Legacy fix scripts, bukan production code |
| `.cryptolab_history/` | Runtime data |
| `.pytest_cache/` | Test cache |

---

## 8. Rekomendasi Prioritas

### Immediate (Quick Wins - <1 jam)
1. Hapus 30+ file `fix_*.py` dari root (sudah tidak dipakai)
2. Hapus dead code di `interactive.py` (LOGO_LARGE, _PIXEL_FONT, dll)
3. Consolidate `DIVIDER`/`THIN_DIVIDER` ke satu tempat
4. Tambah warning untuk MD5/SHA-1/ECB/RC2 di UI

### Short Term (1-3 hari)
1. **Pecah `interactive.py`** → `menu.py`, `handlers/`, `widgets/`
2. **Pecah `cli.py`** → `commands/`, `formatters/`
3. Buat `ui/` package untuk design system terpusat
4. Fix non-constant-time compare di `hashing.py`

### Medium Term (1 minggu)
1. Extract crypto core logic dari UI handlers (separation of concerns)
2. Characterization tests untuk semua handler sebelum refactor
3. Enforce minimum PBKDF2 iterations, Bcrypt cost range
4. Documentation: ADR untuk arsitektur baru

---

## 9. Catatan Tambahan

### UI Inconsistency (Akan di-detail di `UI_INVENTORY.md`)
- 3 sistem rendering berbeda: `cli.py` (render_box), `interactive.py` (render_card), `banner.py` (header/footer)
- Warna: `cli.py` pakai ANSI manual, `interactive.py` pakai helper `color_text()`, `banner.py` pakai `paint()`
- Pembatas: `=`, `-`, `.`, `─` digunakan bercampur
- Footer hints: 2 implementasi berbeda (`banner.py` vs `interactive.py`)

### Technical Debt Markers
- Banyak `TODO` dan `FIXME` di komentar (perlu scan lengkap)
- `pyproject.toml` belum ada `lint`, `typecheck`, `format` scripts
- CI/CD tidak terlihat (tidak ada `.github/workflows/`)

---

*Report generated by automated audit + manual review. Next: REFACTOR_PLAN.md*