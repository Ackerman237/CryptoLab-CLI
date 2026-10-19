# Workflow: Review Changes

**Command:** `/review-changes`  
**Scope:** Workspace changes since last review

---

## Tujuan
Menjalankan OCR review pada perubahan workspace, triase temuan, laporan. **Tidak mengubah kode.**

---

## Langkah Eksekusi

### 1. OCR Review (Delegation Mode)
```bash
ocr delegate preview
ocr delegate rule <changed_files_or_all>
```
- Gunakan `ocr delegate` karena belum ada LLM provider terkonfigurasi
- Review seluruh workspace atau file yang berubah saja

### 2. Triase Temuan
| Severity | Action |
|----------|--------|
| Critical/High | **Block merge** - harus difix sebelum lanjut |
| Medium | Review manual - fix jika valid, catat jika false positive |
| Low | Catat - fix di phase D (polish) |

### 3. Laporan ke User
```
=== OCR REVIEW RESULT ===
Files scanned: 5
Findings:
  CRITICAL: 0
  HIGH: 0
  MEDIUM: 2 (1 valid: hardcoded width in ui/theme.py, 1 FP: test fixture)
  LOW: 3 (style suggestions)

Valid findings to fix:
1. ui/theme.py:45 - Hardcoded width 80 → use theme.Layout.DEFAULT_WIDTH
2. tests/test_ui_guard.py:12 - Regex pattern too broad

False positives:
1. tests/fixtures/test_data.py - Not production code

Recommendation: Fix 1 valid medium, document 1 FP in PROGRESS.md
```

### 4. Update PROGRESS.md
- Catat OCR findings di langkah yang relevan
- Update status jika ada blocker

---

## Output Format
Selalu tampilkan:
1. Summary counts per severity
2. Valid findings detail (file:line, explanation, fix suggestion)
3. False positives dengan alasan
4. Recommendation (block/continue with fixes)