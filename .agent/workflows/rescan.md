# Workflow: Rescan

**Command:** `/rescan [path]`  
**Contoh:** `/rescan src/cryptolab/ui` atau `/rescan` (full repo)

---

## Tujuan
Jalankan OCR scan ulang, bandingkan dengan baseline `docs/audit/ocr-scan.json`, laporkan delta.

---

## Langkah Eksekusi

### 1. Baseline Check
- Cek `docs/audit/ocr-scan.json` exists
- Jika tidak: run full scan first → save baseline

### 2. Run Scan
```bash
# Full repo
ocr scan --output docs/audit/ocr-scan-new.json

# Atau specific path
ocr scan --path src/cryptolab/ui --output docs/audit/ocr-scan-new.json
```

### 3. Compare dengan Baseline
```bash
# Manual diff atau script
diff docs/audit/ocr-scan.json docs/audit/ocr-scan-new.json
# atau python script untuk parse JSON
```

### 4. Kategorikan Delta
| Kategori | Action |
|----------|--------|
| **New Critical/High** | Immediate block - investigate |
| **Fixed Critical/High** | ✅ Progress - update PROGRESS.md |
| **New Medium/Low** | Triase - fix atau accept |
| **Fixed Medium/Low** | ✅ Progress |
| **Unchanged** | Ignore |

### 5. Laporan ke User
```
=== RESCAN RESULT ===
Baseline: docs/audit/ocr-scan.json (2026-10-19)
Current:  docs/audit/ocr-scan-new.json

Delta:
  FIXED:     3 High (A2, A3, A5 done)
  FIXED:     5 Medium (B2, B3 done)
  NEW:       1 Medium (ui/theme.py:45 hardcoded width)
  UNCHANGED: 12 Low

Action Required:
1. Fix ui/theme.py:45 (from B1 extraction)
2. Update baseline after fix

Progress Update:
- A1-A5: ✅ Complete
- B1-B10: 2/10 Complete
```

### 6. Update Files
- Replace baseline: `mv ocr-scan-new.json ocr-scan.json`
- Update `PROGRESS.md` dengan status terbaru
- Catat temuan baru di `AUDIT_REPORT.md` jika critical/high