# CryptoLab CLI - Refactor Progress Checklist

**Berdasarkan:** `docs/audit/REFACTOR_PLAN.md`  
**Tanggal Mulai:** 2026-10-19  
**Status:** Belum dimulai

---

## Legend
- `[ ]` = Belum
- `[~]` = Sedang dikerjakan
- `[x]` = Selesai (test pass, reviewed)
- `[!]` = Blocker/Perlu keputusan

---

## Phase A: Keamanan Critical/High (Security First)

| Step | Task | Status | Verifikasi | Catatan |
|------|------|--------|------------|---------|
| A1 | Tambah warning MD5/SHA-1/ECB/RC2 di UI | `[x]` | Manual test | CLI & Interactive tested |
| A2 | Fix `hmac_verify` & `hash_verify_integrity` pakai `hmac.compare_digest` | `[x]` | Already implemented | All verify functions use constant-time compare |
| A3 | Enforce minimum PBKDF2 iter (100k) & Bcrypt cost range (4-31) | `[x]` | Test edge cases | PBKDF2 min 100k, Bcrypt 4-31 enforced |
| A4 | Hapus/guard key/IV dari history log | `[x]` | Test history | Sanitization with `[REDACTED]` |
| A5 | Deprecation warning RSA PKCS#1 v1.5 | `[x]` | Test CLI & interactive | Warning in reasons for encrypt/decrypt/sign/verify |

---

## Phase B: Characterization Tests (Sebelum Pindah Kode)

| Step | Task | Status | Verifikasi | Catatan |
|------|------|--------|------------|---------|
| B1 | Test snapshot semua CLI command output | `[ ]` | `pytest tests/test_cli_snapshot.py` | New test file |
| B2 | Test snapshot interactive menu rendering | `[ ]` | Mock stdin/stdout | New test file |
| B3 | Test semua crypto primitive (round-trip) | `[ ]` | Encrypt→decrypt = identity | New test file |
| B4 | Test history log format & secrets filtering | `[ ]` | Check no keys in output | New test file |

---

## Phase B (Jalur B): UI Widget Extraction

| Step | Task | Status | Verifikasi | Catatan |
|------|------|--------|------------|---------|
| B1 | Ekstrak `ui/theme.py` (colors, symbols, tokens) | `[ ]` | Snapshot test theme | New package |
| B2 | Widget `Rule` (ganti divider) | `[ ]` | Snapshot width 40/60/80/120 | Replace 52 occurences |
| B3 | Widget `Message` (error/success/warning/info) | `[ ]` | Snapshot test | Replace 45 ANSI raw |
| B4 | Widget `Prompt` (ask/choose/confirm) | `[ ]` | Manual test input flow | Replace safe_input |
| B5 | Widget `KeyValue` & `Table` | `[ ]` | Snapshot test | |
| B6 | Widget `Panel` (ganti render_box, render_card) | `[ ]` | Snapshot test | Replace 2 systems |
| B7 | Widget `Menu` & `Navigation` | `[ ]` | Snapshot test | Core UX |
| B8 | Widget `Header`/`Footer`/`Page` | `[ ]` | Snapshot test | Layout structure |
| B9 | Widget `Task` (spinner/progress/steps) | `[ ]` | Manual test | Progress feedback |
| B10 | Test penjaga: grep larangan pola lama | `[ ]` | CI fail kalau ditemukan | `tests/test_ui_guard.py` |

---

## Phase C (Jalur A): Modularisasi File Terbesar

| Step | Task | Status | Verifikasi | Catatan |
|------|------|--------|------------|---------|
| C1 | Pecah `cli.py` → `cli/commands/` + `cli/formatters/` | `[ ]` | All CLI tests pass | 1,677 lines → package |
| C2 | Pecah `interactive.py` → `interactive/handlers/` + `interactive/menu.py` | `[ ]` | All interactive tests pass | 3,281 lines → package |
| C3 | Ekstrak `core/` package dari module existing | `[ ]` | Import paths updated | Move classical, symmetric, etc |
| C4 | Hapus dead code (LOGO_*, _PIXEL_FONT, fix_*.py) | `[ ]` | No import errors | Cleanup |

---

## Phase D: Pembersihan & Polish

| Step | Task | Status | Verifikasi | Catatan |
|------|------|--------|------------|---------|
| D1 | Hapus duplikasi DIVIDER, center_block, color_*, render_footer | `[ ]` | All tests pass | |
| D2 | Tambah lint, typecheck, format di pyproject.toml | `[ ]` | ruff/mypy/black pass | |
| D3 | Setup CI (GitHub Actions) | `[ ]` | CI green on push | |
| D4 | Update docs & README | `[ ]` | Manual review | |

---

## Quick Wins (<1 Jam)

| # | Task | Status | Catatan |
|---|------|--------|---------|
| Q1 | Hapus 30+ file `fix_*.py` di root | `[ ]` | `rm fix_*.py` |
| Q2 | Hapus dead code LOGO_LARGE, _PIXEL_FONT di interactive.py | `[ ]` | ~50 lines |
| Q3 | Consolidate DIVIDER/THIN_DIVIDER ke theme | `[ ]` | 4 definitions → 1 |
| Q4 | Tambah warning MD5/SHA-1 di hashing.py | `[ ]` | Part of A1 |
| Q5 | Fix hmac.compare_digest di hashing.py | `[ ]` | Part of A2 |
| Q6 | Tambah ruff, mypy, black ke pyproject.toml | `[ ]` | Part of D2 |

---

## Metrik Target Tracking

| Metrik | Baseline | Target | Current | Status |
|--------|----------|--------|---------|--------|
| Max file lines | 3,281 | < 500 | 3,281 | `[ ]` |
| Max function lines | ~200 | < 50 | ~200 | `[ ]` |
| Circular imports | 3+ | 0 | 3+ | `[ ]` |
| UI render systems | 3 | 1 | 3 | `[ ]` |
| Crypto tanpa warning | 4 | 0 | 4 | `[ ]` |
| Test coverage | ~60% | > 85% | ~60% | `[ ]` |
| Non-const-time compare | 2 | 0 | 2 | `[ ]` |
| fix_*.py files | 30+ | 0 | 30+ | `[ ]` |
| Dead code (LOGO_*, etc) | Yes | No | Yes | `[ ]` |

---

## Blocker / Decisions Needed

| # | Issue | Options | Decision | Date |
|---|-------|---------|----------|------|
| 1 | Install OCR CLI (`npm install -g @alibaba-group/open-code-review`)? | Yes/No/Use delegation mode | | |
| 2 | Install radon/vulture/import-linter untuk analisis struktural? | Yes/No/Manual only | | |
| 3 | Buat branch `audit/refactor-plan` untuk audit artifacts? | Yes/No | | |
| 4 | Commit `.agent/` dan `docs/audit/` ke repo? | Yes/No/.gitignore | | |

---

## Log Aktivitas

| Tanggal | Phase | Step | Status | Catatan |
|---------|-------|------|--------|---------|
| 2026-10-19 | 0 | Project Discovery | `[x]` | Completed |
| 2026-10-19 | 0 | File Metrics | `[x]` | 3,281 + 1,677 lines |
| 2026-10-19 | 1-4 | Audit Report | `[x]` | AUDIT_REPORT.md |
| 2026-10-19 | 5 | Refactor Plan | `[x]` | REFACTOR_PLAN.md |
| 2026-10-19 | 4+ | UI Inventory | `[x]` | UI_INVENTORY.md |
| 2026-10-19 | 5 | Progress Checklist | `[x]` | PROGRESS.md (this file) |

---

*Update this file after each completed step. Commit with: `docs/audit/PROGRESS.md: Update step X.Y - description`*