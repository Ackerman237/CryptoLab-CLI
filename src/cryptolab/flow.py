"""flow.py: alur layar aksi (input -> proses -> hasil).

Per padanan panduan 'PROMPT_rombak_ui_cryptolab.md' bagian 6.3.

Tiga fase:
1. Input  - prompt berlabel dengan default dan validasi (tanya ulang).
2. Proses - spinner + waktu; Ctrl+C membatalkan dan kembali ke menu.
3. Hasil  - layar bersih, input ditampilkan ulang, hasil rata dan di-wrap,
            error tampil rapi sebagai ``✗ pesan``. Hasil panjang bisa
            digulir dengan ↑↓ / pgup / pgdn.

API:
- ``Ctx.ask(label, default=None, cast=str, secret=False)`` - ambil input.
- ``Ctx.choose(label, options, default=1)`` - pilihan angka, mengembalikan
  teks opsi yang dipilih.
- ``Ctx.work(text, fn)`` - jalankan proses lambat dengan spinner.
- ``raise ValueError("pesan")`` di mana saja menampilkan error rapi.
- ``Result(rows, note)`` - kontainer hasil untuk ditampilkan.
"""

import getpass
import sys
import textwrap
import threading
import time

from cryptolab.banner import paint, term_width, term_height, vlen, WHITE, DIM, BOLD, GREEN, RED

CLEAR = "\033[2J\033[H"
SHOW_CURSOR = "\033[?25h"
HIDE_CURSOR = "\033[?25l"
# Karakter Braille untuk spinner. Fallback ASCII untuk cmd.exe lama: "|/-\\"
FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
MARGIN = 2


class Cancelled(Exception):
    """Pengguna menekan Ctrl+C saat input atau proses."""


class Result:
    """Kontainer hasil untuk ditampilkan di layar hasil.

    ``rows`` adalah list dari tuple ``(label, nilai)``. ``note`` adalah
    catatan tambahan yang ditampilkan setelah baris hasil.
    """

    def __init__(self, rows=None, note=""):
        self.rows = rows or []      # list[(label, nilai)]
        self.note = note


def _rule(w):
    """Garis pemisah ber-margin 2 kolom."""
    return " " * MARGIN + paint("─" * max(w - 2 * MARGIN, 0), DIM)


def header_lines(title, hint="ctrl+c batal"):
    """Header ringkas untuk layar aksi: 'CRYPTOLAB › Judul' + hint kanan + garis."""
    w = term_width()
    room = max(w - 2 * MARGIN - vlen("CRYPTOLAB › ") - vlen(hint) - 1, 4)
    if vlen(title) > room:
        title = title[: room - 1] + "…"
    gap = max(w - 2 * MARGIN - vlen("CRYPTOLAB › " + title) - vlen(hint), 1)
    line = (" " * MARGIN + paint("CRYPTOLAB", BOLD + WHITE) + paint(f" › {title}", DIM)
            + " " * gap + paint(hint, DIM))
    return [line, _rule(w), ""]


class Ctx:
    """Objek yang diterima setiap fungsi fitur (API ctx).

    Menyediakan ``ask``, ``choose``, dan ``work``. Melacak input yang telah
    dikumpulkan untuk ditampilkan ulang di layar hasil.
    """

    def __init__(self, title):
        self.title = title
        self.inputs = []            # list[(label, tampilan)]
        self._started = False

    def _begin(self):
        """Cetak header layar aksi sekali saat input pertama diminta."""
        if not self._started:
            sys.stdout.write(CLEAR + SHOW_CURSOR + "\n".join(header_lines(self.title)) + "\n")
            sys.stdout.flush()
            self._started = True

    def _error(self, msg):
        print(" " * MARGIN + paint(f"✗ {msg}", RED))

    def _read(self, label, default, cast, secret):
        """Baca satu input dengan validasi dan tanya ulang."""
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
        """Ambil input dengan label, nilai default, dan tipe cast.

        - ``secret=True`` menyembunyikan ketikan (getpass).
        - Validasi: ``cast`` yang raise ValueError akan menampilkan pesan
          dan menanya ulang.
        """
        self._begin()
        value = self._read(label, default, cast, secret)
        self.inputs.append((label, "•" * 8 if secret else str(value)))
        return value

    def choose(self, label, options, default=1):
        """Pilihan angka dari daftar opsi. Mengembalikan teks opsi terpilih."""
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
        """Jalankan fn() di thread; tampilkan spinner + waktu.

        Ctrl+C membatalkan dan kembali ke menu (raise Cancelled).
        Error dari fn() diteruskan ke pemanggil (run_action menanganinya).
        """
        self._begin()
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()
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
                sys.stdout.write(
                    f"\r\033[2K{' ' * MARGIN}{paint(FRAMES[i % len(FRAMES)], WHITE)} "
                    f"{text}  {paint(f'{el:.1f}s', DIM)}"
                )
                sys.stdout.flush()
                i += 1
                t.join(0.08)
        except KeyboardInterrupt:
            sys.stdout.write("\r\033[2K" + SHOW_CURSOR)
            sys.stdout.flush()
            raise Cancelled()
        el = time.time() - t0
        mark = paint("✗", RED) if "e" in box else paint("✓", GREEN)
        sys.stdout.write(
            f"\r\033[2K{' ' * MARGIN}{mark} {text}  {paint(f'{el:.2f}s', DIM)}\n"
            + SHOW_CURSOR
        )
        sys.stdout.flush()
        if "e" in box:
            raise box["e"]
        return box.get("v")


# ---------- layar hasil ----------

def _wrap(value, width):
    """Wrap nilai panjang ke list baris sesuai lebar."""
    out = []
    for part in str(value).splitlines() or [""]:
        wrapped = textwrap.wrap(
            part, width=max(width, 8),
            break_long_words=True, break_on_hyphens=False,
        )
        out += wrapped or [""]
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
    """Bangun baris badan layar hasil: input echo + status + hasil + catatan."""
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
    """Gambar layar hasil dengan offset scroll. Kembalikan (offset, max_off)."""
    w, h = term_width(), term_height()
    head = header_lines(ctx.title, hint="")
    body = _body(ctx, result, error, w)
    room = max(h - len(head) - 3, 3)            # 3 = baris kosong + garis + hint
    offset = max(0, min(offset, max(len(body) - room, 0)))
    view = body[offset: offset + room]
    hints = [("enter", "kembali"), ("r", "ulangi"), ("q", "keluar")]
    if len(body) > room:
        hints.insert(0, ("↑↓", "gulir"))
    lines = head + view + [""] * (room - len(view)) + [""] + render_footer_lines(hints)
    # Gunakan \033[H (home) + \033[K per baris + \033[J (clear rest)
    out = "\033[H" + "\n".join(l + "\033[K" for l in lines[:h]) + "\033[J"
    sys.stdout.write(HIDE_CURSOR + out)
    sys.stdout.flush()
    return offset, max(len(body) - room, 0)


def render_footer_lines(hints):
    """Render footer sebagai list baris (untuk dipakai di _draw)."""
    from cryptolab.ui.ui import render_footer
    return render_footer(hints).split("\n")


def show_result(ctx, result, error, read_key):
    """Tampilkan layar hasil. Kembalikan 'back', 'again', atau 'quit'.

    ``read_key`` adalah fungsi yang menerima ``timeout`` dan mengembalikan
    string tombol (``"up"``, ``"down"``, ``"enter"``, ``"r"``, ``"q"``, dll)
    atau ``None`` bila timeout habis.
    """
    sys.stdout.write(CLEAR)
    offset, last_size = 0, (term_width(), term_height())
    offset, max_off = _draw(ctx, result, error, offset)
    while True:
        key = read_key(0.2)
        size = (term_width(), term_height())
        if key is None and size == last_size:
            continue
        if size != last_size:
            sys.stdout.write(CLEAR)
        last_size = size
        if key in ("enter", "esc"):
            return "back"
        if key == "r":
            return "again"
        if key in ("q", "Q"):
            return "quit"
        step = {"up": -1, "down": 1, "pgup": -10, "pgdn": 10}.get(key, 0)
        if step:
            offset += step
        offset, max_off = _draw(ctx, result, error, offset)


def run_action(title, fn, read_key):
    """Jalankan satu fitur dengan alur penuh.

    ``fn`` adalah fungsi fitur yang menerima ``ctx`` dan mengembalikan
    ``Result`` (atau raise ValueError untuk error tampil rapi).

    Kembalikan 'back' atau 'quit'.
    """
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
