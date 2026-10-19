# CryptoLab CLI - UI Inventory

**Berdasarkan:** Audit manual codebase (read-only)  
**Tanggal:** 2026-10-19  
**Versi:** 1.0.0

---

## Ringkasan Statistik

| Kategori | Jumlah Titik | File Terdampak |
|----------|--------------|----------------|
| **Pembatas (Divider)** | 52 | 3 file |
| **ANSI Mentah / Warna** | 45 | 3 file |
| **Print/Input Langsung di Fitur** | 180+ | 12+ file |
| **Clear/Cls Langsung** | 8 | 2 file |
| **Format Pesan Error/Sukses** | 4 varian | 3 file |
| **Lebar Hard-coded** | 15+ | 4 file |
| **Total Penyimpangan** | ~300 | - |

---

## 1. Pembatas (Divider) - PENYIMPANGAN UTAMA

### Pola Ditemukan

| Pola | Lokasi | Count | Status |
|------|--------|-------|--------|
| `DIVIDER = "=" * 70` | `cli.py:66` | 1 def | **PENYIMPANGAN** |
| `THIN_DIVIDER = "-" * 70` | `cli.py:67` | 1 def | **PENYIMPANGAN** |
| `DIVIDER = "-" * 56` | `interactive.py:65` | 1 def | **PENYIMPANGAN** |
| `THIN_DIVIDER = "." * 56` | `interactive.py:66` | 1 def | **PENYIMPANGAN** |
| `print(DIVIDER)` | `cli.py`, `interactive.py` | 28 | **PENYIMPANGAN** |
| `print(THIN_DIVIDER)` | `cli.py`, `interactive.py` | 15 | **PENYIMPANGAN** |
| `"─" * n` (unicode box) | `banner.py:102` | 1 | **PERBEDAAN SAH** (footer rule) |
| `"─" * max(20, w-2)` | `banner.py:102` | 1 | **PERBEDAAN SAH** (footer rule) |
| `print("=" * 56)` inline | `interactive.py` handlers | 8 | **PENYIMPANGAN** |

### Detail per File

#### `cli.py` (Divider System 1)
```
Line 66: DIVIDER = "=" * 70
Line 67: THIN_DIVIDER = "-" * 70
Usage: render_box(), render_error(), render_brute_force(), render_detection(), 
       render_auto_decode(), render_pipeline_result(), render_history_list()
Count: 28 print calls
```

#### `interactive.py` (Divider System 2)
```
Line 65: DIVIDER = "-" * 56
Line 66: THIN_DIVIDER = "." * 56
Usage: handle_*(), render_card(), post_result_menu(), navigation_menu()
Count: 25 print calls
```

#### `banner.py` (Divider System 3 - Footer Only)
```
Line 102: rule = paint(" " * 2 + "─" * max(w - 4, 0), DIM)
Usage: render_footer() only
Count: 1 implementation
```

### Widget Target: `ui/widgets/rule.py`
- `Rule.heavy(width=70)` → `"=" * 70`
- `Rule.light(width=70)` → `"-" * 70`  
- `Rule.thin(width=56)` → `"." * 56` atau `"─" * 56`
- `Rule.footer(width)` → unicode box drawing untuk footer

---

## 2. ANSI Mentah / Warna - PENYIMPANGAN

### Pola Ditemukan

| Pola | Lokasi | Count | Status |
|------|--------|-------|--------|
| `\033[` raw ANSI | `interactive.py`, `cli.py`, `banner.py` | 45 | **PENYIMPANGAN** |
| `color_text()` helper | `interactive.py:211` | 1 def + 30 uses | **PENYIMPANGAN** (duplikasi) |
| `paint()` helper | `banner.py:36` | 1 def + 15 uses | **PERBEDAAN SAH** (banner only) |
| `bold()`, `cyan()`, `green()`, `red()`, `yellow()`, `emphasis()`, `muted()` | `interactive.py:205-230` | 7 helpers + 50 uses | **PENYIMPANGAN** (duplikasi) |

### Detail Color Systems

#### System 1: `banner.py` - `paint(text, style)`
```python
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
WHITE = "\033[97m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"

def paint(text: str, style: str = "") -> str:
    return f"{style}{text}{RESET}"
```

#### System 2: `interactive.py` - `color_text()` + 7 helpers
```python
USE_COLOR = _supports_color()

def color_text(text: str, code: str) -> str:
    if not USE_COLOR: return text
    return f"\033[{code}m{text}\033[0m"

bold = lambda t: color_text(t, "1")
cyan = lambda t: color_text(t, "36")
green = lambda t: color_text(t, "32")
yellow = lambda t: color_text(t, "33")
red = lambda t: color_text(t, "31")
emphasis = lambda t: color_text(t, "1;97")
muted = lambda t: color_text(t, "90")
```

#### System 3: `cli.py` - ANSI Manual Inline
```python
# Di render_error():
print(f"\033[31m[ERROR]\033[0m {message}")
# Di render_brute_force():
print(f"\033[32m{text}\033[0m")
```

### Widget Target: `ui/theme.py` + `ui/widgets/message.py`
- Theme tokens: `Color.RED`, `Color.GREEN`, `Color.YELLOW`, `Color.CYAN`, `Color.WHITE`, `Color.DIM`, `Color.BOLD`
- Symbol tokens: `Symbol.SUCCESS`, `Symbol.ERROR`, `Symbol.WARNING`, `Symbol.INFO`, `Symbol.POINTER`
- `Message.error(text)`, `Message.success(text)`, `Message.warning(text)`, `Message.info(text)`

---

## 3. Print/Input Langsung di Kode Fitur - PENYIMPANGAN

### Pola Ditemukan

| Pola | Lokasi | Count | Status |
|------|--------|-------|--------|
| `print(...)` di handler | `interactive.py` (14 handlers) | 80+ | **PENYIMPANGAN** |
| `input(...)` / `safe_input()` di handler | `interactive.py` handlers | 40+ | **PENYIMPANGAN** |
| `print(...)` di CLI formatters | `cli.py` (7 formatters) | 30+ | **PENYIMPANGAN** |
| `print(...)` di flow.py | `flow.py` | 5 | **PENYIMPANGAN** |
| `print(...)` di analysis modules | `analysis/*.py` | 10 | **PENYIMPANGAN** |

### Contoh Penyimpangan per Handler

#### `interactive.py` - `handle_caesar()` (lines 649-763)
```python
print("\n" + DIVIDER)
print("  CRYPTOLAB - CAESAR CIPHER")
print(DIVIDER)
choice = navigation_menu(...)  # OK - widget
print("\n" + card)  # PENYIMPANGAN - direct print
if not post_result_menu(card, "hasil_caesar.txt"):  # OK - widget
    break
```

#### `cli.py` - `handle_caesar_cli()` (lines ~400)
```python
print(render_box(...))  # PENYIMPANGAN - formatter returns string, then print
```

#### `flow.py` - `run_interactive_flow()`
```python
print("  Masukkan data:")  # PENYIMPANGAN
data = input("  > ")  # PENYIMPANGAN
```

### Widget Target
- `Prompt.ask(label)`, `Prompt.choose(label, options)`, `Prompt.confirm(label)`
- `Panel.render(...)` returns string, caller prints (OK) ATAUI `Panel.display(...)` writes to stdout
- `Task.run(fn, label="Processing...")` untuk spinner/progress

---

## 4. Clear/Cls Langsung - PENYIMPANGAN

| Pola | Lokasi | Count | Status |
|------|--------|-------|--------|
| `sys.stdout.write("\033[2J\033[H")` | `interactive.py:130`, `interactive.py:313`, `interactive.py:384` | 3 | **PENYIMPANGAN** |
| `clear_screen()` helper | `interactive.py:130` (def), `interactive.py:312` (nested def) | 2 def | **PENYIMPANGAN** (duplikasi) |
| `sys.stdout.write("\033[?1049h\033[2J\033[H")` | `interactive.py:3196` (alt screen) | 1 | **PERBEDAAN SAH** (alt screen enter/exit) |

### Widget Target: `ui/layout.clear_screen()`, `ui/layout.alt_screen_enter()`, `ui/layout.alt_screen_exit()`

---

## 5. Format Pesan Error/Sukses/Peringatan - PENYIMPANGAN

### 4 Varian Berbeda Ditemukan

| Varian | Lokasi | Contoh | Status |
|--------|--------|--------|--------|
| **V1: `[!]` prefix** | `interactive.py` handlers | `print(red(f"\n  [!] Kesalahan: {err}"))` | **PENYIMPANGAN** |
| **V2: `[+]` prefix** | `interactive.py` handlers | `print(green(f"\n  [+] Berhasil: {result}"))` | **PENYIMPANGAN** |
| **V3: `render_error()` box** | `cli.py:150` | Box dengan DIVIDER, "ERROR" title | **PERBEDAAN SAH** (CLI vs Interactive) |
| **V4: `render_box()` success** | `cli.py:70` | Box dengan DIVIDER, "BERHASIL (OK)" | **PERBEDAAN SAH** (CLI vs Interactive) |

### Detail Varian

#### Interactive Style (V1, V2)
```python
# Error
print(red(f"\n  [!] Kesalahan: {err}"))
print(red(f"\n  [!] Gagal menyimpan file: {err}"))

# Success
print(green(f"  [OK] Hasil berhasil disimpan ke: {filepath}"))
print(green(f"  [OK] Riwayat analisis lokal berhasil dibersihkan."))

# Warning
print(yellow("  [!] Input tidak boleh kosong."))
print(yellow(f"  [Perhatian] Panjang key AES-128 harus tepat 16 byte..."))
```

#### CLI Style (V3, V4) - Structured Box
```python
def render_error(message: str) -> str:
    return "\n".join([
        DIVIDER,
        f"  CRYPTOLAB CLI v{__version__} - ERROR",
        DIVIDER,
        f"  {message}",
        DIVIDER,
    ])

def render_box(title, operation, input_text, output_text, params):
    # Returns formatted box with DIVIDER, THIN_DIVIDER
```

### Widget Target: `ui/widgets/message.py`
```python
Message.error("Kesalahan", detail="File tidak ditemukan")  # Interactive style
Message.success("Disimpan", detail=f"File: {path}")        # Interactive style
Message.warning("Perhatian", detail="Key terlalu pendek")  # Interactive style

# CLI style (full box)
Panel.error("ERROR", "File tidak ditemukan")
Panel.result("CAESAR ENCRYPT", "Enkripsi", "BERHASIL (OK)", input, output, params)
```

---

## 6. Lebar Hard-coded - PENYIMPANGAN

| Pola | Lokasi | Count | Status |
|------|--------|-------|--------|
| `width=70` / `70` hardcoded | `cli.py:66,67`, formatters | 10+ | **PENYIMPANGAN** |
| `width=56` hardcoded | `interactive.py:65,66` | 8+ | **PENYIMPANGAN** |
| `max(20, width-2)` | `banner.py:102` | 1 | **PERBEDAAN SAH** (responsive footer) |
| `width - 8`, `width - 11` | `interactive.py:337,352` | 4 | **PENYIMPANGAN** (magic numbers) |
| `offset=-4` | `interactive.py:331,333` | 2 | **PENYIMPANGAN** (magic number) |

---

## 7. Tabel Lengkap: File:Baris | Jenis | Pola Saat Ini | Widget Target | Status

| File | Baris | Jenis | Pola Saat Ini | Widget Target | Status |
|------|-------|-------|---------------|---------------|--------|
| `cli.py` | 66 | Divider | `DIVIDER = "=" * 70` | `Rule.heavy()` | **PENYIMPANGAN** |
| `cli.py` | 67 | Divider | `THIN_DIVIDER = "-" * 70` | `Rule.light()` | **PENYIMPANGAN** |
| `cli.py` | 70-98 | Formatter | `render_box()` + print | `Panel.result()` | **PENYIMPANGAN** |
| `cli.py` | 150-165 | Formatter | `render_error()` + print | `Panel.error()` | **PERBEDAAN SAH** |
| `cli.py` | 200+ | Formatter | `render_brute_force()` | `Table` + `Panel` | **PENYIMPANGAN** |
| `cli.py` | 250+ | Formatter | `render_detection()` | `Panel` + `KeyValue` | **PENYIMPANGAN** |
| `cli.py` | 300+ | Formatter | `render_auto_decode()` | `Panel` + `Table` | **PENYIMPANGAN** |
| `cli.py` | 350+ | Formatter | `render_pipeline_result()` | `Panel` + `Table` | **PENYIMPANGAN** |
| `cli.py` | 400+ | Formatter | `render_history_list()` | `Table` | **PENYIMPANGAN** |
| `interactive.py` | 65 | Divider | `DIVIDER = "-" * 56` | `Rule.heavy()` | **PENYIMPANGAN** |
| `interactive.py` | 66 | Divider | `THIN_DIVIDER = "." * 56` | `Rule.thin()` | **PENYIMPANGAN** |
| `interactive.py` | 205-230 | Color | 7 helper functions | `theme.Color` | **PENYIMPANGAN** |
| `interactive.py` | 211 | Color | `color_text()` | `theme.paint()` | **PENYIMPANGAN** |
| `interactive.py` | 244 | Footer | `render_footer()` v2 | `Footer.render()` | **PENYIMPANGAN** |
| `interactive.py` | 273 | Panel | `render_card()` | `Panel.result()` | **PENYIMPANGAN** |
| `interactive.py` | 319 | Screen | `terminal_width()` | `theme.term_width()` | **PENYIMPANGAN** |
| `interactive.py` | 331 | Layout | `center_block(offset=-4)` | `Header.render()` | **PENYIMPANGAN** |
| `interactive.py` | 358 | Menu | `navigation_menu()` | `Menu.navigate()` | **PENYIMPANGAN** |
| `interactive.py` | 334 | Prompt | `safe_input()` | `Prompt.ask()` | **PENYIMPANGAN** |
| `interactive.py` | 338 | Post | `post_result_menu()` | `Task.confirm()` | **PENYIMPANGAN** |
| `interactive.py` | 320 | Save | `save_result_prompt()` | `Prompt.save()` | **PENYIMPANGAN** |
| `interactive.py` | 649-763 | Handler | `handle_caesar()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 766-834 | Handler | `handle_vigenere()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 837-900 | Handler | `handle_playfair()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 903-978 | Handler | `handle_hill()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 981-1085 | Handler | `handle_affine()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1088-1199 | Handler | `handle_railfence()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1202-1350 | Handler | `handle_des()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1350-1500 | Handler | `handle_aes()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1500-1650 | Handler | `handle_rc2()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1650-1850 | Handler | `handle_hashing()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 1850-2100 | Handler | `handle_rsa()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2100-2250 | Handler | `handle_dh()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2250-2400 | Handler | `handle_base64()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2400-2550 | Handler | `handle_hex()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2550-2700 | Handler | `handle_binary()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2700-2850 | Handler | `handle_history()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `interactive.py` | 2850-3000 | Handler | `handle_auto_analyze()` - print/input | `Handler + Widgets` | **PENYIMPANGAN** |
| `banner.py` | 36 | Color | `paint()` | `theme.paint()` | **PERBEDAAN SAH** (banner only) |
| `banner.py` | 58 | Layout | `center_block()` | `layout.center()` | **PENYIMPANGAN** |
| `banner.py` | 72 | Header | `render_header()` | `Header.render()` | **PENYIMPANGAN** |
| `banner.py` | 96 | Footer | `render_footer()` v1 | `Footer.render()` | **PENYIMPANGAN** |
| `banner.py` | 120 | Terminal | `hide_cursor()`/`show_cursor()` | `Terminal.hide_cursor()` | **PERBEDAAN SAH** |
| `flow.py` | 50-100 | Flow | Direct print/input | `Prompt` + `Panel` | **PENYIMPANGAN** |

---

## 8. Klasifikasi: PENYIMPANGAN vs PERBEDAAN SAH

### PENYIMPANGAN (Harus Disamakan ke Widget)
1. ✅ **Divider systems** (3 sistem berbeda) → `Rule` widget
2. ✅ **Color systems** (3 sistem berbeda) → `theme.Color` + `Message` widget
3. ✅ **Print/input di handler** (14 handlers × ~10 print cada) → `Prompt`, `Panel`, `Table`
4. ✅ **Clear screen manual** (2 def + 3 calls) → `Terminal.clear()`
5. ✅ **Magic numbers** (70, 56, -4, -8, -11) → `theme.Layout` constants
6. ✅ **Error/Success format** (4 varian) → `Message` + `Panel` variants

### PERBEDAAN SAH (Varian Widget, Bukan Duplikat)
1. ✅ **CLI Box vs Interactive Card** → `Panel.cli_result()` vs `Panel.interactive_card()` (same widget, different variant)
2. ✅ **Footer Rule (unicode) vs Divider (ASCII)** → `Rule.footer()` vs `Rule.heavy()` (different purpose)
3. ✅ **Alt Screen Enter/Exit** → `Terminal.alt_screen_enter/exit()` (specialized)
4. ✅ **Banner-only `paint()`** → `theme.paint()` (same function, banner scope)
5. ✅ **Cursor hide/show** → `Terminal.hide_cursor()/show_cursor()` (terminal control)

---

## 9. Rencana Migrasi (Prioritas)

| Urutan | Widget | Target File | Alasan Prioritas |
|--------|--------|-------------|------------------|
| 1 | `Rule` | `cli.py`, `interactive.py`, `banner.py` | Paling banyak duplikasi (52 occurences), aman |
| 2 | `Message` | `interactive.py` handlers, `cli.py` formatters | Error/success format konsisten di seluruh app |
| 3 | `Prompt` | `interactive.py` handlers, `flow.py` | Input handling terpusat, validasi konsisten |
| 4 | `Panel` | `cli.py` formatters, `interactive.py` render_card | Result display terpusat |
| 5 | `KeyValue`/`Table` | `cli.py` formatters, `interactive.py` handlers | Data display terpusat |
| 6 | `Menu`/`Navigation` | `interactive.py` navigation_menu | Core interactive UX |
| 7 | `Header`/`Footer`/`Page` | `banner.py`, `interactive.py` menu_lines | Layout structure |
| 8 | `Task` | `flow.py`, handlers yang butuh spinner | Progress feedback |

---

*Next: Update `docs/audit/PROGRESS.md` with checklist*