# UI Widgets Rule (Always-On)

**Semua output terminal HARUS lewat paket `ui.widgets`. Dilarang pola lama di kode fitur.**

---

## Larangan Keras (Test Penjaga Akan Gagal)

### ❌ Dilarang di `core/`, `cli/commands/`, `interactive/handlers/`, `flow.py`:
```python
# 1. Print/input langsung
print(...)          # → gunakan Panel.display(), Message.show(), Prompt.ask()
input(...)          # → gunakan Prompt.ask(), Prompt.choose(), Prompt.confirm()

# 2. ANSI mentah
"\033[31m"          # → gunakan theme.Color.RED, theme.paint()
"\033[1m"           # → gunakan theme.Color.BOLD
"\033[0m"           # → gunakan theme.Color.RESET

# 3. Pembatas manual
"=" * 70            # → gunakan Rule.heavy()
"-" * 56            # → gunakan Rule.light()
"." * 56            # → gunakan Rule.thin()
"─" * n             # → gunakan Rule.footer() atau Rule.unicode()

# 4. Clear screen manual
sys.stdout.write("\033[2J\033[H")  # → Terminal.clear()
sys.stdout.write("\033[?1049h")    # → Terminal.alt_screen_enter()

# 5. Color helper lama
color_text(), bold(), cyan(), red(), green(), yellow(), emphasis(), muted()
paint() (kecuali di banner.py scope)
```

---

## Pola Benar (Gunakan Widget)

### Output Rendering
```python
from cryptolab.ui.widgets import Panel, Message, Rule, KeyValue, Table
from cryptolab.ui.layout import Header, Footer, Page
from cryptolab.ui.theme import Color, Symbol

# Result panel
Panel.result(title="CAESAR ENCRYPT", operation="Enkripsi", status="OK", 
             input_text="HELLO", output_text="KHOOR", params={"Shift": 3})

# Error/Success/Warning/Info
Message.error("Key invalid", detail="Must be 16 bytes")
Message.success("Saved", detail=f"File: {path}")
Message.warning("Weak key", detail="Consider stronger password")
Message.info("Processing", detail="Analyzing...")

# Divider
Rule.heavy()      # "=" * width
Rule.light()      # "-" * width  
Rule.thin()       # "." * width
Rule.footer()     # unicode box drawing

# Key-value / Table
KeyValue.render({"Shift": 3, "Mode": "CBC"}, width=80)
Table.render(headers=["Shift", "Score"], rows=[[3, 85.2], [5, 42.1]])
```

### Input Prompting
```python
from cryptolab.ui.widgets import Prompt

# Text input
text = Prompt.ask("Masukkan plaintext", validator=non_empty)

# Choose from options
choice = Prompt.choose("Pilih mode", ["Encrypt", "Decrypt", "Brute Force"])

# Confirm yes/no
if Prompt.confirm("Simpan ke file?", default=False):
    save()
```

### Layout & Terminal
```python
from cryptolab.ui.layout import Header, Footer, Page, Terminal
from cryptolab.ui.theme import Color, Symbol

# Full page
Page.render(
    header=Header.render(title="CRYPTOLAB", subtitle="v1.0.0"),
    body=menu_lines,
    footer=Footer.render(hints=HINTS_MAIN)
)

# Terminal control
Terminal.clear()
Terminal.hide_cursor()
Terminal.show_cursor()
Terminal.alt_screen_enter()
Terminal.alt_screen_exit()
```

---

## Variasi Sah (Bukan Pengecualian)

| Varian | Widget | Parameter |
|--------|--------|-----------|
| CLI Box (full) | `Panel.cli_result()` | `variant="cli"` |
| Interactive Card | `Panel.card()` | `variant="interactive"` |
| Error Message | `Message.error()` | `kind="error"` |
| Success Message | `Message.success()` | `kind="success"` |
| Footer Rule | `Rule.footer()` | `variant="footer"` |

**Aturan:** Variasi baru = tambah parameter/variant di widget, **BUKAN** buat fungsi baru di kode fitur.

---

## Test Penjaga (Otomatis di CI)

```python
# tests/test_ui_guard.py
FORBIDDEN_PATTERNS = [
    (r'print\(', "Direct print in feature code"),
    (r'input\(', "Direct input in feature code"),
    (r'\033\[', "Raw ANSI escape code"),
    (r'"=" \* \d+', "Manual heavy divider"),
    (r'"-" \* \d+', "Manual light divider"),
    (r'"\." \* \d+', "Manual thin divider"),
    (r'color_text\(', "Legacy color helper"),
    (r'\bbold\(|\bcyan\(|\bred\(|\bgreen\(|\byellow\(', "Legacy color helpers"),
]

# Scan: src/cryptolab/core/, src/cryptolab/cli/commands/, 
#       src/cryptolab/interactive/handlers/, src/cryptolab/flow.py
```

---

## Dokumentasi Singkat

### Theme Tokens (`ui/theme.py`)
```python
Color = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m", 
    "DIM": "\033[2m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "CYAN": "\033[36m",
    "WHITE": "\033[97m",
}

Symbol = {
    "SUCCESS": "✓",
    "ERROR": "✗", 
    "WARNING": "⚠",
    "INFO": "ℹ",
    "POINTER": "▸",
    "HEAVY": "=",
    "LIGHT": "-",
    "THIN": "·",
    "FOOTER": "─",
}

Layout = {
    "DEFAULT_WIDTH": 80,
    "MIN_WIDTH": 40,
    "MARGIN": 2,
    "PADDING": 1,
}
```

### Widget Import Pattern
```python
# Di kode fitur (handlers, commands, flow)
from cryptolab.ui.widgets import Panel, Message, Rule, Prompt, KeyValue, Table, Task
from cryptolab.ui.layout import Header, Footer, Page, Terminal
from cryptolab.ui.theme import Color, Symbol, Layout
```

---

*Enforced by: `tests/test_ui_guard.py` (Phase B10)*
*Next: See `workflows/ui-migrate.md` for migration process*