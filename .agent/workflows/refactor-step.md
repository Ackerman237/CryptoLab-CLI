# Workflow: Refactor Step

**Command:** `/refactor-step <nomor langkah>`  
**Contoh:** `/refactor-step A2` atau `/refactor-step B2`

---

## Tujuan
Eksekusi satu langkah roadmap dari `REFACTOR_PLAN.md` dengan guardrails penuh.

---

## Langkah Eksekusi

### 1. Baca Konteks
- Buka `docs/audit/REFACTOR_PLAN.md` → cari langkah `<nomor>`
- Buka `docs/audit/PROGRESS.md` → cek status langkah (harus `[ ]`)
- Baca `docs/audit/AUDIT_REPORT.md` untuk context temuan terkait

### 2. Konfirmasi Lingkup ke User
```
LINGKUP: Step A2 - Fix hmac_verify constant-time compare
FILE: src/cryptolab/hashing.py:280
CHANGES: Replace `==` with `hmac.compare_digest()`
TESTS: Run existing + new characterization test
LANJUTKAN? (y/n)
```
→ Tunggu persetujuan user (`y`)

### 3. Characterization Test First
- Jika belum ada: **tulis test characterization** di `tests/`
- Test harus: capture input→output behavior SAAT INI
- Jalankan test → **harus PASS** sebelum lanjut

### 4. Terapkan Perubahan Minimal
- Edit **hanya** file & fungsi yang tercantum di langkah
- Jangan "sambil bersihkan" kode lain
- Ikuti style existing (import, naming, docstring)

### 5. Jalankan Test & Linter
```bash
pytest tests/ -v -x
ruff check src/
mypy src/
```
→ Semua harus **PASS**. Jika gagal: analisis, fix, re-run.

### 6. OCR Review (Delegation Mode)
```bash
ocr delegate preview
ocr delegate rule <changed_files>
```
→ Review temuan OCR. Jika critical/high → fix dulu. Medium/low → catat.

### 7. Update PROGRESS.md
- Ubah status langkah: `[ ]` → `[x]`
- Tambah catatan: commit hash, test result, OCR findings

### 8. Tampilkan Ringkasan & Stop
```
=== STEP A2 COMPLETE ===
Files changed: src/cryptolab/hashing.py
Tests: 42 passed, 0 failed
OCR: 0 critical, 0 high, 1 medium (false positive), 0 low
Commit suggestion: fix: use hmac.compare_digest in hmac_verify

Status: [x] A2 - Fix hmac constant-time compare
Next: A3 - Enforce PBKDF2/Bcrypt params
```
→ **BERHENTI**. Tunggu perintah berikutnya.

---

## Rollback Plan
Jika regressi:
```bash
git checkout HEAD -- <changed_files>
# atau
git revert <commit-hash>
```