# Workflow: UI Migrasi

**Command:** `/ui-migrate <file atau fungsi>`  
**Contoh:** `/ui-migrate src/cryptolab/interactive.py:handle_caesar` atau `/ui-migrate src/cryptolab/cli.py:render_box`

---

## Tujuan
Migrasi satu file/fungsi dari pola UI lama ke widget baru tanpa mengubah logika.

---

## Prasyarat
- Widget target sudah ada di `ui/widgets/` (Phase B complete)
- `UI_INVENTORY.md` updated untuk titik yang akan dimigrasi
- Characterization test sudah ada untuk fungsi tersebut

---

## Langkah Eksekusi

### 1. Baca Inventaris
- Buka `docs/audit/UI_INVENTORY.md`
- Cari `file:fungsi` target
- Catat: `jenis`, `pola saat ini`, `widget target`

### 2. Daftar Titik yang Akan Diganti
Tampilkan ke user:
```
MIGRASI: src/cryptolab/interactive.py:handle_caesar
TITIK YANG DIGANTI:
  - Line 652: print(DIVIDER) → Rule.heavy()
  - Line 653: print("  CRYPTOLAB - CAESAR CIPHER") → Header.render()
  - Line 654: print(DIVIDER) → Rule.heavy()
  - Line 670: print(yellow(...)) → Message.warning()
  - Line 684: print(red(...)) → Message.error()
  - Line 707: print("\n" + card) → Panel.display()
  - Line 708: post_result_menu() → Task.confirm()

WIDGET TARGET: Rule, Header, Message, Panel, Task
LOGIKA TIDAK BERUBAH: cipher operation, input validation, flow
LANJUTKAN? (y/n)
```

### 3. Ganti Tanpa Ubah Logika
- Import widget dari `ui.widgets`
- Replace pola lama dengan widget call
- **Jangan** ubah: variable names, control flow, crypto calls, error handling logic
- Hanya ubah: rendering output, input prompting

### 4. Jalankan Test
```bash
# Characterization test untuk fungsi ini
pytest tests/test_characterization.py::test_handle_caesar -v

# Full test suite
pytest tests/ -x -q
```

### 5. Smoke Test Manual
```
# Test interaktif
cryptolab menu
→ Pilih "Caesar Cipher"
→ Test encrypt/decrypt/brute
→ Verify output visual sama (hanya rapih)

# Test CLI
cryptolab caesar --encrypt "HELLO" --shift 3
→ Verify box output sama struktur
```

### 6. Update Inventaris & Progress
- `UI_INVENTORY.md`: Ubah status titik → `MIGRATED`
- `PROGRESS.md`: Update step status

### 7. Tampilkan Diff & Stop
```
=== UI MIGRATE COMPLETE ===
File: src/cryptolab/interactive.py:handle_caesar
Lines changed: 15
Widgets used: Rule, Header, Message, Panel, Task
Tests: 5/5 passed
Visual: Verified match at width 80, 120

UI_INVENTORY.md: 7 points → MIGRATED
PROGRESS.md: B8 step updated

Commit suggestion: ui: migrate handle_caesar to widgets (Rule, Header, Message, Panel, Task)
```
→ **BERHENTI**. Tunggu perintah berikutnya.