# PROMPT: Rombak Total Tampilan CRYPTOLAB CLI (menu + layar aksi)

Kamu adalah engineer Python senior yang ahli membuat TUI di terminal (ANSI escape, tanpa library UI berat). Tugasmu: **merombak tampilan CRYPTOLAB CLI** yang sekarang, lalu menggantinya dengan desain baru di bawah. Kode referensi lengkap ada di bagian 6. **Jangan ubah logika kriptografi** (DES, AES, RSA, hashing, dll). Yang diubah hanya lapisan tampilan, input, dan alur layar.

Bahasa seluruh teks di UI: **Bahasa Indonesia**. Terminal target: **Windows Terminal** (juga harus aman di Linux/macOS).

---

## 1. Kondisi sekarang (dari screenshot) dan masalahnya

Menu utama berisi 14 item: Auto Analyze, Caesar Cipher, Vigenere Cipher, DES, AES, RC2, Hashing & Password, RSA, Diffie-Hellman, Base64, Hex, Binary, Riwayat, Keluar. Label di menu sudah pendek dan blok menu sudah berada di tengah. Strukturnya benar, tinggal dirapikan. Masalah yang terlihat:

1. **Logo terpotong dan terdorong keluar layar.** Hanya dua baris bawah logo yang kelihatan, dan bentuknya pecah jadi kotak-kotak putih. Penyebabnya: total baris yang dicetak lebih besar dari tinggi window, sehingga terminal scroll dan baris atas hilang. Akibatnya item **"Keluar" juga tidak terlihat**.
2. **Item menu berjarak dua baris** (ada baris kosong di antara tiap item). Ini pemborosan tinggi dan penyebab utama overflow. Jadikan **satu baris per item**.
3. **Logo tidak simetris di tengah.** Posisinya bergeser ke kanan dibanding menu dan subtitle. Pemusatan harus memakai lebar *terlihat* (tanpa kode ANSI) dari baris terlebar, lalu semua baris diberi padding yang sama.
4. **Footer tidak sejajar dengan garis.** Garis pemisah ada di tengah, tetapi teks hint (`↑↓ navigasi  enter pilih ...`) menempel di kiri. Panjang hint harus dihitung dari teks polos (tanpa ANSI), dan garis serta hint harus memakai satu lebar yang sama.
5. **Versi tidak konsisten**: satu tempat menulis `v1.0.0`, tempat lain `v0.1.0`. Buat **satu konstanta `APP_VERSION`** dan pakai di mana-mana. Nilai yang benar untuk proyek ini adalah `0.1.0`, kecuali kamu menemukan versi lain yang sah di `pyproject`/`README`. Kalau menemukannya, ikuti itu dan laporkan.
6. **Subtitle menempel ke logo** tanpa jarak, dan menu menempel ke garis pemisah. Tambahkan baris kosong di antaranya.
7. **Layar aksi (input, proses, hasil) masih polos**: `input()` biasa, `print()` mentah, tidak ada indikator proses, hasil panjang tidak di-wrap, error tampil sebagai teks mentah atau crash.

---

## 2. Target tampilan

### 2.1 Menu utama, layar 80x24 (logo otomatis jadi sedang)

```text
             ▄▀▀▀▀ █▀▀▀▄ █   █ █▀▀▀▄ ▀▀█▀▀ ▄▀▀▀▄ █     ▄▀▀▀▄ █▀▀▀▄
             █     █▀▀█   ▀▄▀  █▀▀▀    █   █   █ █     █▀▀▀█ █▀▀▀▄
              ▀▀▀▀ ▀   ▀   ▀   ▀       ▀    ▀▀▀  ▀▀▀▀▀ ▀   ▀ ▀▀▀▀

             CRYPTOLAB CLI v0.1.0 · TOOLKIT KRIPTOGRAFI & ENCODING

                                   Menu Utama

                                ↑ 2 lagi
                                Vigenere Cipher
                                DES
                                AES
                                RC2
                              ▸ Hashing & Password
                                RSA
                                Diffie-Hellman
                                Base64
                                ↓ 4 lagi

                         MD5, SHA, HMAC, PBKDF2, Bcrypt

  ────────────────────────────────────────────────────────────────────────────
                ↑↓ navigasi   enter pilih   q keluar   ? bantuan
```

### 2.2 Aturan tata letak menu

- **Satu sumbu**: logo, subtitle, judul menu, blok menu, deskripsi, dan footer semuanya dipusatkan. Blok menu dipusatkan *sebagai satu blok* sehingga tepi kirinya sejajar (bukan tiap baris di-center sendiri).
- **Label menu pendek.** Keterangan panjang (misalnya `MD5, SHA, HMAC, PBKDF2, Bcrypt`) tampil **satu baris di bawah menu** untuk item yang sedang dipilih.
- **Ada baris kosong** antara: logo, subtitle, judul menu, menu, deskripsi, garis footer.
- **Garis pemisah** memakai `─` (bukan `-`), margin kiri dan kanan sama 2 kolom.
- **Kursor terminal disembunyikan** selama menu tampil (`\033[?25l`) dan dimunculkan lagi saat keluar atau saat input (`\033[?25h`). Pastikan di-restore juga saat crash (try/finally).
- **Logo adaptif terhadap tinggi window**: besar, lalu sedang, lalu teks. Menu 14 item dengan logo besar muncul utuh di layar tinggi (120x30). Di layar pendek logo mengecil.
- **Menu bisa di-scroll** jika tinggi tidak cukup, dengan penanda `↑ N lagi` dan `↓ N lagi`.
- **Footer selalu terlihat.** Jangan pernah mencetak lebih banyak baris daripada tinggi terminal dan jangan mencetak newline di baris terakhir (itu memicu scroll).

### 2.3 Layar aksi (tiga fase, gaya konsisten)

Header ringkas (tanpa logo besar) supaya ruang hasil luas.

**Fase 1, input:**

```text
  CRYPTOLAB › Hashing & Password                                   ctrl+c batal
  ──────────────────────────────────────────────────────────────────────────────

  Teks › halo
  Algoritma
    1  MD5
    2  SHA-256
    3  HMAC-SHA256
    4  PBKDF2-SHA256
  pilih [1] › 4
  Iterasi [600000] ›
```

**Fase 2, proses:** spinner dengan waktu berjalan, lalu berubah jadi centang.

```text
  ⠹ Menghitung PBKDF2 (600.000 iterasi)  0.3s
  ✓ Menghitung PBKDF2 (600.000 iterasi)  0.31s
```

**Fase 3, hasil:** layar bersih, input yang tadi diketik ditampilkan ulang, hasil rata dan di-wrap sesuai lebar terminal.

```text
  CRYPTOLAB › Hashing & Password
  ──────────────────────────────────────────────────────────────────────────────

  Teks       halo
  Algoritma  PBKDF2-SHA256
  Iterasi    600000

  ✓ Selesai

  Salt     a3f1c9e07b2d4a58e6f01d3c9b7a2e14
  Iterasi  600000
  Hash     9f2c4b7a1e8d03c65f2a9b1d7e4c8a30
           5d6f1b2e9a7c4083d1e5b6a2f9c7d4e8

  ──────────────────────────────────────────────────────────────────────────────
               enter kembali   r ulangi   q keluar
```

Perilaku layar aksi:

| Hal | Perilaku |
|---|---|
| Input | prompt berlabel, nilai default `[600000]`, validasi dengan pesan `✗ ...` lalu tanya ulang |
| Kata sandi | `ctx.ask("Kunci", secret=True)` menyembunyikan ketikan |
| Proses lambat | spinner + waktu; `Ctrl+C` membatalkan dan kembali ke menu |
| Hasil | label rata, nilai panjang di-wrap, hasil sangat panjang (kunci RSA) bisa digulir dengan ↑↓ |
| Error | `raise ValueError("pesan")` di fitur tampil sebagai `✗ pesan` di layar hasil, tidak crash |
| Setelah hasil | `enter` kembali, `r` ulangi dengan input baru, `q` keluar |
| Resize | layar hasil digambar ulang mengikuti lebar |
| Warna | hanya untuk simbol status (✓ hijau, ✗ merah); selebihnya putih dan abu-abu |

---

## 3. Aturan wajib

1. **Jangan sentuh logika kripto.** Hanya bungkus ulang fungsi fitur agar memakai API `ctx` (bagian 5).
2. Semua perhitungan lebar/pemusatan memakai **panjang teks terlihat** (`vlen`, tanpa ANSI). Jangan pernah `len()` pada string yang sudah dibungkus `paint()`.
3. Tidak ada library UI baru (tanpa curses, rich, textual). Hanya standar library.
4. Semua pencetakan layar penuh lewat satu fungsi `screen(lines, full_clear)` yang: memotong ke tinggi terminal, tidak mencetak newline di baris terakhir, menghapus sisa baris dengan `\033[K`, dan menghapus sisa layar dengan `\033[J`.
5. Pastikan terminal selalu kembali normal (kursor tampil, mode normal) saat keluar normal, `Ctrl+C`, maupun exception.
6. Sediakan fallback ASCII untuk spinner (`"|/-\\"`) lewat satu konstanta, karena `cmd.exe` lama bisa menampilkan karakter Braille sebagai kotak.
7. Satu sumber kebenaran: `APP_VERSION`, `HEADER_SUBTITLE`, dan string hint didefinisikan sekali.

---

## 4. Langkah kerja yang harus kamu lakukan

1. **Baca dulu seluruh kode UI yang ada** (`banner.py`, `app.py`, atau nama setara). Catat: cara membaca tombol (`read_key`), cara menggambar layar, struktur `Menu`, dan bagaimana tiap fitur dipanggil. Jangan menebak. Sesuaikan kode referensi di bawah dengan struktur nyata proyek.
2. **Reproduksi masalah di bagian 1** (jalankan di terminal 80x24 dan di window pendek) dan sebutkan penyebab tiap masalah yang kamu temukan di kode.
3. Terapkan perbaikan `banner.py` (bagian 6.1), buat `ui.py` (6.2), buat `flow.py` (6.3), ubah `app.py` (6.4).
4. Konversi **semua fitur** ke API baru (bagian 5). Mulai dari Hashing & Password dan Base64 sebagai pola, lalu sisanya.
5. Jalankan checklist verifikasi (bagian 7) dan perbaiki sampai semuanya lulus.
6. Beri ringkasan akhir (bagian 8).

---

## 5. API fitur baru

Setiap fungsi fitur menerima `ctx` dan mengembalikan `Result`:

```python
def do_rsa_keygen(ctx):
    bits = ctx.choose("Ukuran kunci", ["1024", "2048", "4096"])
    pub, priv = ctx.work("Membuat pasangan kunci RSA", lambda: generate(int(bits)))
    return Result([("Public", pub), ("Private", priv)],
                  note="Simpan kunci privat di tempat aman.")
```

- `ctx.ask("Label", default=None, cast=str, secret=False)` mengambil input, dengan validasi dan tanya ulang.
- `ctx.choose("Label", [...], default=1)` pilihan angka, mengembalikan **teks opsi** yang dipilih.
- `ctx.work("Teks", fungsi)` menjalankan proses lambat dengan spinner, mengembalikan hasil fungsi.
- `raise ValueError("pesan")` di mana saja menampilkan error rapi di layar hasil.
- Item menu berbentuk tuple `(label_pendek, aksi, keterangan)`.

Contoh fitur Hashing & Password (hanya contoh pola; **Bcrypt butuh library `bcrypt`, jangan dihapus dari fitur asli kalau sudah ada**):

```python
import hashlib, hmac, os

def fn_hash(ctx):
    text = ctx.ask("Teks")
    algo = ctx.choose("Algoritma", ["MD5", "SHA-256", "HMAC-SHA256", "PBKDF2-SHA256"], default=2)
    data = text.encode()
    if algo == "MD5":
        return Result([("Hash", hashlib.md5(data).hexdigest())])
    if algo == "SHA-256":
        return Result([("Hash", hashlib.sha256(data).hexdigest())])
    if algo == "HMAC-SHA256":
        key = ctx.ask("Kunci", secret=True)
        return Result([("HMAC", hmac.new(key.encode(), data, "sha256").hexdigest())])
    iters = ctx.ask("Iterasi", default=600000, cast=int)
    if iters < 1:
        raise ValueError("iterasi harus >= 1")
    salt = os.urandom(16)
    dk = ctx.work(f"Menghitung PBKDF2 ({iters:,} iterasi)".replace(",", "."),
                  lambda: hashlib.pbkdf2_hmac("sha256", data, salt, iters))
    return Result([("Salt", salt.hex()), ("Iterasi", str(iters)), ("Hash", dk.hex())])
```

---

## 6. Kode

> Catatan: kode di bawah ditulis berdasarkan struktur yang diasumsikan (modul `banner`, `ui`, `flow`, `app`). Sesuaikan nama dan tanda tangan fungsi dengan kode asli, tanpa mengubah perilaku yang dijelaskan di bagian 2.

### 6.1 `banner.py` (perbaiki / tambahkan bagian ini)

Pertahankan konstanta logo yang sudah ada (`LOGO_LARGE`, `LOGO_MEDIUM`, `LOGO_TINY`), `paint`, `WHITE`, `DIM`, dan `term_width`. Pastikan fungsi-fungsi berikut **seperti ini**:

```python
import re
import shutil

_ANSI = re.compile(r"\033\[[0-9;?]*[A-Za-z]")

APP_VERSION = "0.1.0"
HEADER_SUBTITLE = f"CRYPTOLAB CLI v{APP_VERSION} · TOOLKIT KRIPTOGRAFI & ENCODING"


def vlen(s):
    """Panjang yang terlihat (tanpa kode ANSI)."""
    return len(_ANSI.sub("", s))


def term_width(default=80):
    return shutil.get_terminal_size((default, 24)).columns


def term_height(default=24):
    return shutil.get_terminal_size((80, default)).lines


def _block_width(block):
    return max((vlen(l) for l in block.splitlines()), default=0)


def center_block(block, width):
    """Pusatkan logo SEBAGAI SATU BLOK: semua baris diberi padding yang sama."""
    bw = _block_width(block)
    pad = " " * max((width - bw) // 2, 0)
    return "\n".join(pad + l.ljust(bw) for l in block.splitlines())


def pick_logo(width, max_rows=99):
    """Logo terbesar yang muat di lebar DAN tinggi yang tersedia."""
    for logo in (LOGO_LARGE, LOGO_MEDIUM):
        if _block_width(logo) <= width and len(logo.splitlines()) <= max_rows:
            return logo
    return LOGO_TINY


def render_header(subtitle=HEADER_SUBTITLE, max_logo_rows=99):
    w = term_width()
    logo = paint(center_block(pick_logo(w, max_logo_rows), w), WHITE)
    if len(subtitle) > w:                      # terlalu lebar: buang bagian setelah " · "
        subtitle = subtitle.split(" · ")[0]
    if len(subtitle) > w:
        subtitle = subtitle[: max(w - 1, 0)] + "…"
    sub = paint(subtitle.center(w), DIM)
    return "\n".join(["", logo, "", sub])      # tanpa garis bawah; garisnya cukup di footer
```

Cek juga: `LOGO_TINY` harus 1 baris teks `CRYPTOLAB`. Jika logo besar/sedang memakai karakter blok (`▄▀█`), pastikan tidak ada karakter lebar-ganda yang merusak perhitungan lebar.

### 6.2 `ui.py` (file baru / ganti seluruh isi)

```python
from banner import paint, term_width, WHITE, DIM

BOLD = "\033[1m"

HINTS_MAIN = [("↑↓", "navigasi"), ("enter", "pilih"), ("q", "keluar"), ("?", "bantuan")]
HINTS_SUB = [("↑↓", "navigasi"), ("enter", "pilih"), ("esc", "kembali"), ("q", "keluar"), ("?", "bantuan")]


def _fit(hints, width, gap=3):
    chosen = list(hints)
    while chosen:
        if len((" " * gap).join(f"{k} {l}" for k, l in chosen)) <= width - 2:
            return chosen
        chosen.pop()
    return []


def render_footer(hints, gap=3):
    """Garis tipis ber-margin 2 kolom + hint di tengah (tombol putih, label redup)."""
    w = term_width()
    chosen = _fit(hints, w, gap)
    plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
    styled = (" " * gap).join(f"{paint(k, BOLD + WHITE)} {paint(l, DIM)}" for k, l in chosen)
    rule = paint(" " * 2 + "─" * max(w - 4, 0), DIM)
    return rule + "\n" + " " * max((w - len(plain)) // 2, 0) + styled


def _clip(text, width):
    return text if len(text) <= width else text[: max(width - 1, 0)] + "…"


def render_menu(labels, selected, descs=None, avail_rows=None):
    """Menu satu kolom: blok dipusatkan, tepi kiri SEJAJAR, ada scroll jika layar pendek.
    Mengembalikan list baris (menu + baris kosong + deskripsi item terpilih)."""
    w = term_width()
    n = len(labels)
    label_w = min(max(len(l) for l in labels), max(w - 6, 8))
    pad = " " * max((w - (2 + label_w)) // 2, 0)

    # viewport
    rows = n if avail_rows is None else avail_rows
    if n <= rows:
        start, end, truncated = 0, n, False
    else:
        view = max(rows - 2, 1)  # sisakan 2 baris untuk penanda ↑/↓
        start = min(max(selected - view // 2, 0), n - view)
        end, truncated = start + view, True

    lines = []
    if truncated:
        lines.append(pad + paint(f"  ↑ {start} lagi", DIM) if start else "")
    for i in range(start, end):
        text = _clip(labels[i], label_w)
        if i == selected:
            lines.append(pad + paint(f"▸ {text}", BOLD + WHITE))
        else:
            lines.append(pad + paint(f"  {text}", DIM))
    if truncated:
        left = n - end
        lines.append(pad + paint(f"  ↓ {left} lagi", DIM) if left else "")

    # deskripsi item terpilih (selalu 2 baris: kosong + teks)
    desc = (descs[selected] if descs else "") or ""
    desc = _clip(desc, w - 4)
    lines.append("")
    lines.append(" " * max((w - len(desc)) // 2, 0) + paint(desc, DIM) if desc else "")
    return lines
```

### 6.3 `flow.py` (file baru): alur layar aksi

`run_action` membutuhkan fungsi `read_key(timeout=None)` yang **sudah ada di proyek** (yang dipakai menu). Kontrak yang dipakai: mengembalikan string `"up"`, `"down"`, `"pgup"`, `"pgdn"`, `"enter"`, `"esc"`, atau satu karakter (`"q"`, `"r"`), dan `None` bila timeout habis. Jika `read_key` yang ada tidak punya parameter `timeout`, tambahkan (di Windows pakai `msvcrt.kbhit()` + `time.sleep(0.02)` dalam loop; di POSIX pakai `select`). Sesuaikan nama tombol dengan yang sudah dipakai menu.

```python
"""flow.py: alur layar aksi (input -> proses -> hasil)."""
import getpass
import sys
import textwrap
import threading
import time

from banner import paint, term_width, term_height, WHITE, DIM
from ui import render_footer, BOLD

GREEN = "\033[32m"
RED = "\033[31m"
CLEAR = "\033[2J\033[H"
SHOW_CURSOR = "\033[?25h"
HIDE_CURSOR = "\033[?25l"
FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"        # fallback cmd.exe lama: FRAMES = "|/-\\"
MARGIN = 2


class Cancelled(Exception):
    """Pengguna menekan Ctrl+C saat input atau proses."""


class Result:
    def __init__(self, rows=None, note=""):
        self.rows = rows or []      # list[(label, nilai)]
        self.note = note


def _rule(w):
    return " " * MARGIN + paint("─" * max(w - 2 * MARGIN, 0), DIM)


def header_lines(title, hint="ctrl+c batal"):
    w = term_width()
    room = max(w - 2 * MARGIN - len("CRYPTOLAB › ") - len(hint) - 1, 4)
    if len(title) > room:
        title = title[: room - 1] + "…"
    gap = max(w - 2 * MARGIN - len("CRYPTOLAB › " + title) - len(hint), 1)
    line = (" " * MARGIN + paint("CRYPTOLAB", BOLD + WHITE) + paint(f" › {title}", DIM)
            + " " * gap + paint(hint, DIM))
    return [line, _rule(w), ""]


class Ctx:
    """Objek yang diterima setiap fungsi fitur."""

    def __init__(self, title):
        self.title = title
        self.inputs = []            # list[(label, tampilan)]
        self._started = False

    def _begin(self):
        if not self._started:
            sys.stdout.write(CLEAR + SHOW_CURSOR + "\n".join(header_lines(self.title)) + "\n")
            sys.stdout.flush()
            self._started = True

    def _error(self, msg):
        print(" " * MARGIN + paint(f"✗ {msg}", RED))

    def _read(self, label, default, cast, secret):
        suffix = f" [{default}]" if default is not None else ""
        prompt = " " * MARGIN + f"{label}{suffix} › "
        while True:
            try:
                raw = (getpass.getpass(prompt) if secret else input(prompt)).strip()
            except (KeyboardInterrupt, EOFError):
                raise Cancelled()
            if raw == "":
                if default is None:
                    self._error("tidak boleh kosong")
                    continue
                return default
            try:
                return cast(raw)
            except ValueError as e:
                self._error(str(e) or "format tidak valid")

    def ask(self, label, default=None, cast=str, secret=False):
        self._begin()
        value = self._read(label, default, cast, secret)
        self.inputs.append((label, "•" * 8 if secret else str(value)))
        return value

    def choose(self, label, options, default=1):
        self._begin()
        print(" " * MARGIN + label)
        for i, opt in enumerate(options, 1):
            print(" " * (MARGIN + 2) + paint(str(i), BOLD + WHITE) + "  " + opt)

        def pick(raw):
            n = int(raw)
            if not 1 <= n <= len(options):
                raise ValueError(f"pilih 1-{len(options)}")
            return n

        n = self._read("pilih", default, pick, False)
        self.inputs.append((label, options[n - 1]))
        return options[n - 1]

    def work(self, text, fn):
        """Jalankan fn() di thread; tampilkan spinner + waktu. Ctrl+C membatalkan."""
        self._begin()
        sys.stdout.write(HIDE_CURSOR)
        box = {}

        def run():
            try:
                box["v"] = fn()
            except BaseException as e:      # diteruskan ke thread utama
                box["e"] = e

        t = threading.Thread(target=run, daemon=True)
        t.start()
        t0, i = time.time(), 0
        try:
            while t.is_alive():
                el = time.time() - t0
                sys.stdout.write(f"\r\033[2K{' ' * MARGIN}{paint(FRAMES[i % len(FRAMES)], WHITE)} "
                                 f"{text}  {paint(f'{el:.1f}s', DIM)}")
                sys.stdout.flush()
                i += 1
                t.join(0.08)
        except KeyboardInterrupt:
            sys.stdout.write("\r\033[2K" + SHOW_CURSOR)
            raise Cancelled()
        el = time.time() - t0
        mark = paint("✗", RED) if "e" in box else paint("✓", GREEN)
        sys.stdout.write(f"\r\033[2K{' ' * MARGIN}{mark} {text}  {paint(f'{el:.2f}s', DIM)}\n"
                         + SHOW_CURSOR)
        sys.stdout.flush()
        if "e" in box:
            raise box["e"]
        return box.get("v")


# ---------- layar hasil ----------

def _wrap(value, width):
    out = []
    for part in str(value).splitlines() or [""]:
        out += textwrap.wrap(part, width=max(width, 8), break_long_words=True,
                             break_on_hyphens=False) or [""]
    return out


def _kv_lines(pairs, w):
    """Label rata kiri, nilai di-wrap dengan indent yang sama."""
    if not pairs:
        return []
    lw = max(len(k) for k, _ in pairs)
    vw = w - 2 * MARGIN - lw - 2
    lines = []
    for k, v in pairs:
        wrapped = _wrap(v, vw)
        for j, chunk in enumerate(wrapped):
            label = paint(k.ljust(lw), DIM) if j == 0 else " " * lw
            lines.append(" " * MARGIN + label + "  " + chunk)
    return lines


def _body(ctx, result, error, w):
    body = _kv_lines(ctx.inputs, w)
    if body:
        body.append("")
    if error:
        body.append(" " * MARGIN + paint(f"✗ {error}", RED))
    else:
        body.append(" " * MARGIN + paint("✓", GREEN) + " Selesai")
        body.append("")
        body += _kv_lines(result.rows, w)
        if result.note:
            body += ["", " " * MARGIN + paint(result.note, DIM)]
    return body


def _draw(ctx, result, error, offset):
    w, h = term_width(), term_height()
    head = header_lines(ctx.title, hint="")
    body = _body(ctx, result, error, w)
    room = max(h - len(head) - 3, 3)            # 3 = baris kosong + garis + hint
    offset = max(0, min(offset, max(len(body) - room, 0)))
    view = body[offset: offset + room]
    hints = [("enter", "kembali"), ("r", "ulangi"), ("q", "keluar")]
    if len(body) > room:
        hints.insert(0, ("↑↓", "gulir"))
    lines = head + view + [""] * (room - len(view)) + [""] + render_footer(hints).split("\n")
    out = "\033[H" + "\n".join(l + "\033[K" for l in lines[:h]) + "\033[J"
    sys.stdout.write(HIDE_CURSOR + out)
    sys.stdout.flush()
    return offset, max(len(body) - room, 0)


def show_result(ctx, result, error, read_key):
    """Kembalikan 'back', 'again', atau 'quit'."""
    sys.stdout.write(CLEAR)
    offset, last_size = 0, (term_width(), term_height())
    offset, max_off = _draw(ctx, result, error, offset)
    while True:
        key = read_key(0.2)
        size = (term_width(), term_height())
        if key is None and size == last_size:
            continue
        last_size = size
        if key in ("enter", "esc"):
            return "back"
        if key == "r":
            return "again"
        if key in ("q", "Q"):
            return "quit"
        step = {"up": -1, "down": 1, "pgup": -10, "pgdn": 10}.get(key, 0)
        offset += step
        if size != last_size:
            sys.stdout.write(CLEAR)
        offset, max_off = _draw(ctx, result, error, offset)


def run_action(title, fn, read_key):
    """Jalankan satu fitur dengan alur penuh. Kembalikan 'back' atau 'quit'."""
    while True:
        ctx = Ctx(title)
        result, error = Result(), None
        try:
            result = fn(ctx) or Result()
        except Cancelled:
            return "back"
        except ValueError as e:
            error = str(e) or "input tidak valid"
        except Exception as e:                  # tampilkan rapi, jangan crash
            error = f"{type(e).__name__}: {e}"
        action = show_result(ctx, result, error, read_key)
        if action != "again":
            return action
```

Catatan untuk `flow.py`: sebelum memanggil `run_action`, `app.py` harus keluar dari mode tombol-mentah (raw/cbreak, kalau dipakai di POSIX) agar `input()` bekerja normal, lalu masuk lagi setelahnya. Di Windows dengan `msvcrt` biasanya tidak perlu. Setelah kembali ke menu, panggil `screen(..., full_clear=True)`.

### 6.4 `app.py` (perubahan)

Ganti import dan fungsi menggambar menu, dan tambahkan helper `center`:

```python
from banner import (render_header, term_width, term_height, paint, WHITE, DIM,
                    HEADER_SUBTITLE)
from ui import render_menu, render_footer, HINTS_MAIN, HINTS_SUB
from flow import run_action, Result


def center(text):
    return text.center(term_width())


def menu_lines(menu, sel, depth):
    h = term_height()
    labels = [it[0] for it in menu.items]
    descs = [it[2] if len(it) > 2 else "" for it in menu.items]
    hints = HINTS_SUB if depth > 0 else HINTS_MAIN

    # Total baris = header (logo+3) + 3 (kosong, judul, kosong) + menu + 2 (kosong, deskripsi)
    #               + 3 (kosong, garis, hint) = logo + menu + 11
    want_menu = min(len(labels), 10)
    logo_rows = max(h - 11 - want_menu, 1)
    header = render_header(HEADER_SUBTITLE, max_logo_rows=logo_rows).split("\n")

    avail = max(h - len(header) - 8, 3)
    body = render_menu(labels, sel, descs, avail_rows=avail)
    lines = header + ["", paint(center(menu.title), DIM), ""] + body + ["", render_footer(hints)]
    return "\n".join(lines).split("\n")[:h]


def draw_menu(menu, sel, depth, full_clear):
    screen(menu_lines(menu, sel, depth), full_clear)
```

Di `run_menu` dan `page_lines`, ubah dua hal ini (item sekarang boleh 3 elemen):

```python
label, target = menu.items[sel][:2]
lines = render_header(HEADER_SUBTITLE).split("\n")      # di page_lines
```

Saat item dipilih dan `target` adalah fungsi fitur, panggil:

```python
result = run_action(label, target, read_key)            # 'back' atau 'quit'
if result == "quit":
    return
screen(menu_lines(menu, sel, depth), True)              # gambar ulang menu
```

Definisi menu utama (label pendek, aksi, keterangan):

```python
MAIN = Menu("Menu Utama", [
    ("Auto Analyze",       fn_auto,    "Deteksi otomatis jenis cipher / encoding dari teks"),
    ("Caesar Cipher",      fn_caesar,  "Cipher klasik: geser huruf"),
    ("Vigenere Cipher",    fn_vig,     "Cipher klasik: kunci berulang"),
    ("DES",                fn_des,     "Data Encryption Standard · 64 bit"),
    ("AES",                fn_aes,     "Advanced Encryption Standard · 128 bit"),
    ("RC2",                fn_rc2,     "ARC2 · legacy 64 bit"),
    ("Hashing & Password", fn_hash,    "MD5, SHA, HMAC, PBKDF2, Bcrypt"),
    ("RSA",                fn_rsa,     "KeyGen, Encrypt, Decrypt, Sign, Verify"),
    ("Diffie-Hellman",     fn_dh,      "Pertukaran kunci (DHKE)"),
    ("Base64",             fn_b64,     "Encode / decode Base64"),
    ("Hex",                fn_hex,     "Encode / decode Hex"),
    ("Binary",             fn_bin,     "Encode / decode Binary"),
    ("Riwayat",            fn_history, "Lihat riwayat operasi"),
    ("Keluar",             EXIT,       "Tutup aplikasi"),
])
```

Jika di proyek, menu `Hashing`, `RSA`, `AES`, dll. adalah **submenu** (punya pilihan Encrypt/Decrypt/dst.), pertahankan struktur itu dan terapkan tampilan yang sama pada submenu (judul submenu di tengah, `HINTS_SUB` dengan `esc kembali`).

Di `main()` pastikan:

```python
sys.stdout.write("\033[?1049h\033[?25l")        # layar alternatif + sembunyikan kursor
try:
    ...                                          # loop utama
finally:
    sys.stdout.write("\033[?25h\033[?1049l")     # pulihkan kursor + layar normal
    sys.stdout.flush()
```

Layar alternatif (`?1049h`) mencegah sisa tampilan menumpuk di scrollback terminal.

---

## 7. Checklist verifikasi (wajib dijalankan)

Uji dengan terminal tiruan (misalnya `pty` + ukuran yang diatur) atau jalankan langsung dan ubah ukuran window. Untuk tiap ukuran, **hitung jumlah baris keluaran: tidak boleh melebihi tinggi terminal, dan footer harus terlihat.**

| Ukuran | Yang harus terjadi |
|---|---|
| 120x30 | logo besar + 14 item semua tampil tanpa scroll, footer terlihat |
| 80x24 | logo sedang, menu scroll dengan `↑ N lagi` / `↓ N lagi`, footer terlihat |
| 50x14 | logo teks, menu scroll, tampilan tetap utuh |
| 40x12 | tidak crash, footer tetap ada (boleh dipotong lebar hint) |

Perilaku yang harus lulus:

- Logo, subtitle, judul menu, blok menu, deskripsi, dan hint footer **semuanya sejajar di tengah**; garis `─` memiliki margin kiri dan kanan 2 kolom yang sama.
- Item "Keluar" selalu bisa dicapai (scroll ke bawah) dan terlihat saat dipilih.
- Navigasi ↑↓ dengan wrap-around, `enter` memilih, `q` keluar, `?` bantuan, `esc` kembali dari submenu, `esc` di menu utama tidak crash.
- Resize saat di menu dan di layar hasil menggambar ulang tanpa sisa karakter.
- Aksi Hashing PBKDF2: spinner tampil dengan waktu, berubah jadi `✓`, hasil muncul, hash panjang ter-wrap, `r` mengulang dengan input baru, `Ctrl+C` saat input atau saat spinner kembali ke menu.
- Fitur dengan `raise ValueError("...")` menampilkan `✗ ...` di layar hasil, tidak crash.
- Hasil panjang (kunci RSA 4096) bisa digulir dengan ↑↓ dan `pgup`/`pgdn`.
- Kursor kembali tampil setelah program keluar, baik keluar normal maupun akibat `Ctrl+C`/exception.
- Semua fitur lama masih menghasilkan output kriptografi yang **identik** dengan sebelum perombakan (bandingkan beberapa vektor uji: MD5/SHA-256 string `halo`, Base64/Hex/Binary roundtrip, AES/DES encrypt-decrypt roundtrip, RSA keygen-sign-verify).
- Tidak ada `print()` mentah atau `input()` polos tersisa di luar `flow.py`.

---

## 8. Format laporan akhir

Setelah selesai, balas dengan:

1. Daftar file yang diubah atau dibuat.
2. Penyebab tiap masalah di bagian 1 yang kamu temukan di kode asli.
3. Hasil checklist (tabel lulus/gagal per ukuran terminal).
4. Hal yang tidak bisa kamu verifikasi atau asumsi yang kamu ambil (misalnya bentuk `read_key`, versi aplikasi yang dipilih, submenu).
5. Daftar fitur yang sudah dikonversi ke API `ctx`, dan yang belum (dengan alasannya).

Kerjakan bertahap dan commit per tahap bila memakai git: (a) perbaikan `banner.py` + `ui.py` + menu, (b) `flow.py` + konversi fitur, (c) pembersihan dan verifikasi.
