# Spesifikasi Upgrade CLI Keamanan Informasi

## Aturan utama (wajib)

1. **Jangan ubah logika** enkripsi, dekripsi, hash, dan encoding yang sudah ada. Output lama harus identik.
2. **Jangan ubah tampilan yang sudah ada.** UI baru hanya tambahan/variasi, dan menu lama tetap bisa dipakai sebagai fallback.
3. Pekerjaan ini hanya **menambah**: opsi pemisah, navigasi tab, dan mode baru.
4. **Kode di dokumen ini hanya ilustrasi** (Python + Rich + readchar). Bahasa, library, nama fungsi, dan struktur folder proyek aslinya bisa berbeda.
   - Baca kode yang ada lebih dulu, lalu sesuaikan snippet ke gaya, library, dan struktur yang sudah dipakai.
   - Kalau proyek sudah punya library menu/input (mis. questionary, inquirer, prompt_toolkit), pakai itu. Jangan tambah dependensi baru tanpa alasan.
   - Yang harus dipertahankan adalah **perilakunya**, bukan kodenya. Kalau snippet bentrok dengan kode yang ada, ikuti kode yang ada dan laporkan.

## Urutan kerja

Berhenti dan verifikasi di akhir setiap tahap.

| Tahap | Isi |
|---|---|
| 0 | Simpan output lama sebagai patokan regresi |
| 1 | Pemisah Binary dan Hex |
| 2 | Menu tab kategori (kiri/kanan) + daftar algoritma (atas/bawah) |
| 3 | Mode baru, satu per satu |

---

## Tahap 0: patokan regresi

Sebelum mengubah apa pun, jalankan fungsi yang ada dan simpan hasilnya sebagai tes. Isi nilai dari **output tool saat ini**; contoh di bawah hanya gambaran.

```python
def test_output_lama_tidak_berubah():
    assert to_binary("Hi") == "01001000 01101001"   # default lama: spasi
    assert caesar_encrypt("HELLO", 3) == "KHOOR"
    assert b64_encode("Hello") == "SGVsbG8="
    # tambahkan Hex, Vigenere, dll. dari output aktual
```

Tes ini harus tetap hijau setelah setiap tahap.

---

## Tahap 1: pemisah Binary dan Hex

### Perilaku

- Prompt pemisah muncul setelah memilih **Encode** pada Binary dan Hex.
- Baris pertama (Spasi) sudah terpilih, jadi **Enter = spasi** (sama dengan perilaku lama).
- Navigasi pilihan dengan ▲ ▼ + Enter.

| Mode | Pilihan |
|---|---|
| Binary | Spasi (default), Tanpa pemisah, Koma, Strip, Kustom |
| Hex | Spasi (default), Tanpa pemisah, Titik dua, Strip, Prefix `0x`, Kustom |

- **Kustom**: 1 sampai 3 karakter. Tidak boleh memuat karakter data:
  - Binary: `0`, `1`
  - Hex: `0-9`, `A-F`, `X`
  - Input kosong = spasi. Input tidak valid = pesan singkat lalu ulangi.
- **Decode tidak perlu memilih pemisah.** Deteksi otomatis dengan membuang semua karakter non-data. Ini aman karena pemisah kustom tidak boleh memuat karakter data.
- Validasi decode dengan pesan error jelas (tanpa crash):
  - Binary: jumlah bit harus kelipatan 8
  - Hex: jumlah digit harus genap

### Snippet

Tambahkan parameter `sep` dengan **default yang sama dengan perilaku lama**, sehingga pemanggilan lama tidak berubah.

```python
import re

def to_binary(text, sep=" "):
    return sep.join(f"{b:08b}" for b in text.encode("utf-8"))

def from_binary(s):
    bits = re.sub(r"[^01]", "", s)
    if len(bits) % 8:
        raise ValueError("Jumlah bit harus kelipatan 8")
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)).decode("utf-8")

def to_hex(text, sep=" ", prefix=""):
    return sep.join(f"{prefix}{b:02x}" for b in text.encode("utf-8"))

def from_hex(s):
    s = re.sub(r"0x", "", s, flags=re.I)
    h = re.sub(r"[^0-9a-fA-F]", "", s)
    if len(h) % 2:
        raise ValueError("Jumlah digit hex harus genap")
    return bytes.fromhex(h).decode("utf-8")
```

> Pertahankan huruf besar/kecil hex dan format lain yang dipakai tool sekarang. Snippet hanya menunjukkan struktur.

Prompt pemisah (satu komponen dipakai Binary dan Hex):

```python
BIN_OPTS = [("Spasi", " "), ("Tanpa pemisah", ""), ("Koma", ","),
            ("Strip", "-"), ("Kustom...", None)]
HEX_OPTS = [("Spasi", " "), ("Tanpa pemisah", ""), ("Titik dua", ":"),
            ("Strip", "-"), ("Prefix 0x", "0x"), ("Kustom...", None)]
BIN_FORBID = set("01")
HEX_FORBID = set("0123456789ABCDEFX")

def pick_delimiter(options, forbid):
    value = select(options)              # ▲ ▼ + Enter, item pertama = default
    if value is not None:
        return value
    while True:                          # Kustom
        raw = console.input("Pemisah kustom (Enter = spasi): ")
        if not raw:
            return " "
        if len(raw) <= 3 and not (set(raw.upper()) & forbid):
            return raw
        console.print("[red]Maks 3 karakter dan tidak boleh memuat karakter data[/red]")

# di pemanggil Hex:
sep = pick_delimiter(HEX_OPTS, HEX_FORBID)
prefix = ""
if sep == "0x":
    sep, prefix = " ", "0x"
```

`select(options)` adalah loop ▲ ▼ + Enter yang sama dengan menu di Tahap 2 (hanya vertikal). Pakai `Live(..., screen=False)` agar redraw terjadi di tempat tanpa menghapus layar.

---

## Tahap 2: menu tab kategori

### Tampilan target (Opsi A)

```
┌──────────────────────────────────────────────────────────┐
│  ◀  Klasik │ [Simetris] │ Asimetris │ Hash │ Encoding  ▶ │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    ▸ AES                                                 │
│      AES-GCM                                      baru   │
│      DES                                      ⚠ usang    │
│      RC2                                      ⚠ usang    │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ◀ ▶ kategori   ▲ ▼ algoritma   Enter pilih   Q keluar   │
└──────────────────────────────────────────────────────────┘
```

### Perilaku

- ◀ ▶ pindah kategori (wrap-around), posisi algoritma kembali ke item pertama.
- ▲ ▼ pindah algoritma (wrap-around). Enter memilih. `Q` atau `Esc` keluar.
- Tombol angka `1` sampai `5` melompat ke kategori.
- Tanda `baru` (hijau) dan `⚠ usang` (kuning) dipertahankan.
- Terminal sempit: kalau seluruh tab tidak muat, tampilkan hanya tab aktif dengan `◀ [Simetris] (2/5) ▶`.
- **Fallback ke menu lama** bila:
  - `stdin`/`stdout` bukan TTY (pipe atau script), atau
  - terminal tidak mendukung karakter kotak: pakai border ASCII (`+ - |`).
- Opsional: flag seperti `--classic-menu` untuk memaksa menu lama.

### Pemetaan kategori

Handler tetap **fungsi lama apa adanya**; nama `run_*` di bawah hanya placeholder. Label item yang sudah ada dipertahankan seperti sekarang.

| Kategori | Isi |
|---|---|
| Klasik | Caesar, Vigenère |
| Simetris | AES, AES-GCM (baru), DES (usang), RC2 (usang) |
| Asimetris | RSA, Diffie-Hellman, Digital Signature (baru) |
| Hash | Hashing & Password (lama), SHA-3, SHA-512, HMAC-SHA-256, Argon2id/bcrypt (baru) |
| Encoding | Base64, Hex, Binary |

### Snippet

```python
import sys, readchar
from readchar import key
from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

console = Console()
BOX = box.SQUARE if (console.encoding or "").lower().startswith("utf") else box.ASCII

# (label, handler_lama, tag)  tag: "", "baru", "usang"
CATEGORIES = {
    "Klasik":    [("Caesar", run_caesar, ""), ("Vigenère", run_vigenere, "")],
    "Simetris":  [("AES", run_aes, ""), ("AES-GCM", run_aes_gcm, "baru"),
                  ("DES", run_des, "usang"), ("RC2", run_rc2, "usang")],
    "Asimetris": [("RSA", run_rsa, ""), ("Diffie-Hellman", run_dh, ""),
                  ("Digital Signature", run_sign, "baru")],
    "Hash":      [("Hashing & Password", run_hash, ""), ("SHA-3", run_sha3, "baru"),
                  ("SHA-512", run_sha512, "baru"), ("HMAC-SHA-256", run_hmac, "baru"),
                  ("Argon2id / bcrypt", run_pwd, "baru")],
    "Encoding":  [("Base64", run_b64, ""), ("Hex", run_hex, ""), ("Binary", run_bin, "")],
}

def render(names, ci, ai):
    items = CATEGORIES[names[ci]]
    tabs = Text("◀  ")
    for i, n in enumerate(names):
        active = i == ci
        tabs.append(f"[{n}]" if active else f" {n} ", style="bold cyan" if active else "dim")
        tabs.append(" │ " if i < len(names) - 1 else "  ")
    tabs.append("▶")

    body = Text()
    for i, (label, _, tag) in enumerate(items):
        body.append(("▸ " if i == ai else "  ") + label, style="bold" if i == ai else "")
        if tag == "usang": body.append("   ⚠ usang", style="yellow")
        if tag == "baru":  body.append("   baru", style="green")
        body.append("\n")

    foot = Text("◀ ▶ kategori   ▲ ▼ algoritma   Enter pilih   Q keluar", style="dim")
    return Panel(Group(tabs, Rule(style="dim"), body, Rule(style="dim"), foot), box=BOX)

def pick_algorithm():
    names, ci, ai, choice = list(CATEGORIES), 0, 0, None
    with Live(render(names, ci, ai), console=console, screen=True, auto_refresh=False) as live:
        while True:
            k = readchar.readkey()
            n = len(CATEGORIES[names[ci]])
            if   k == key.LEFT:  ci, ai = (ci - 1) % len(names), 0
            elif k == key.RIGHT: ci, ai = (ci + 1) % len(names), 0
            elif k == key.UP:    ai = (ai - 1) % n
            elif k == key.DOWN:  ai = (ai + 1) % n
            elif k.isdigit() and 1 <= int(k) <= len(names): ci, ai = int(k) - 1, 0
            elif k == key.ENTER: choice = CATEGORIES[names[ci]][ai]; break
            elif k in (key.ESC, "q", "Q"): break
            live.update(render(names, ci, ai), refresh=True)
    return choice

# titik masuk
if sys.stdin.isatty() and sys.stdout.isatty():
    choice = pick_algorithm()
    if choice:
        choice[1]()          # jalankan handler lama
else:
    legacy_menu()            # menu lama, tidak diubah
```

Catatan: `screen=True` memakai layar alternatif, jadi tampilan terminal sebelumnya kembali utuh setelah keluar dari menu.

---

## Tahap 3: mode baru (konsep, tanpa kode)

Tambahkan satu per satu sebagai item baru di kategori yang sesuai. Setelah tiap mode, jalankan tes regresi Tahap 0.

| Mode | Kategori | Perilaku | Library yang disarankan |
|---|---|---|---|
| SHA-3, SHA-512 | Hash | Hash teks dan file, sebagai pembanding SHA-256 | `hashlib` |
| Argon2id / bcrypt | Hash | Hash password dengan salt otomatis, plus verifikasi | `argon2-cffi`, `bcrypt` |
| HMAC-SHA-256 | Hash | Buat MAC dan verifikasi dengan kunci rahasia | `hmac` (pakai `compare_digest`) |
| Digital Signature | Asimetris | Buat pasangan kunci, tanda tangan, verifikasi (RSA-PSS atau Ed25519) | `cryptography` |
| AES-GCM | Simetris | Nonce acak 12 byte, pesan error jelas bila tag autentikasi tidak valid | `cryptography` (`AESGCM`) |
| Mode file | Umum | Input/output dari file untuk hash dan enkripsi yang relevan, dibaca per chunk | stdlib |
| Generate key | Umum | Kunci acak aman secara kriptografis | `secrets` |

Aturan keamanan:
- Bandingkan hash/MAC dengan perbandingan waktu-konstan.
- Jangan mencetak atau menyimpan kunci ke log.
- Gunakan library tepercaya, bukan implementasi sendiri, untuk algoritma modern.
- DES dan RC2 tetap ditandai `⚠ usang`; jangan menurunkan keamanan konfigurasi lain demi mengaktifkannya.

---

## Checklist selesai

- [ ] Tes regresi Tahap 0 hijau di setiap tahap
- [ ] Enter pada prompt pemisah menghasilkan spasi (sama dengan perilaku lama)
- [ ] Decode Binary/Hex berhasil dengan semua pemisah, dan error jelas untuk input tidak valid
- [ ] Menu tab bisa dinavigasi penuh dengan panah; fallback ke menu lama berfungsi
- [ ] Tampilan dan perilaku fitur lama tidak berubah
- [ ] Mode baru masuk di kategori yang benar dengan tag `baru`
