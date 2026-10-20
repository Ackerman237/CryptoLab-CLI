"""ui.py - render_menu, render_footer, dan konstanta hint.

Per padanan panduan 'PROMPT_rombak_ui_cryptolab.md' bagian 6.2.

Menu satu kolom: blok dipusatkan sehingga tepi kiri sejajar (bukan tiap baris
di-center sendiri). Ada scroll dengan penanda ``↑ N lagi`` / ``↓ N lagi``
bila tinggi tidak cukup. Footer memakai garis ``─`` ber-margin 2 kolom dan
hint di tengah (tombol putih, label redup).

Semua perhitungan lebar/pemusatan memakai ``vlen`` (panjang terlihat, tanpa
ANSI) dari ``banner``.
"""

from cryptolab.banner import paint, term_width, vlen, WHITE, DIM, BOLD

# Hint sets: (tombol, label). Dipakai bersama oleh menu utama dan submenu.
HINTS_MAIN = [("↑↓", "navigasi"), ("enter", "pilih"), ("q", "keluar"), ("?", "bantuan")]
HINTS_SUB = [("↑↓", "navigasi"), ("enter", "pilih"), ("esc", "kembali"), ("q", "keluar"), ("?", "bantuan")]


def _fit(hints, width, gap=3):
    """Pilih hint yang muat dalam lebar; buang dari belakang bila tidak muat."""
    chosen = list(hints)
    while chosen:
        plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
        if vlen(plain) <= width - 2:
            return chosen
        chosen.pop()
    return []


def render_footer(hints, gap=3):
    """Garis tipis ber-margin 2 kolom + hint di tengah.

    Tombol putih-tebal, label redup. Pemusatan dihitung dari teks polos
    (``vlen``) agar selalu sejajar dengan garis.
    """
    w = term_width()
    chosen = _fit(hints, w, gap)
    plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
    styled = (" " * gap).join(f"{paint(k, BOLD + WHITE)} {paint(l, DIM)}" for k, l in chosen)
    rule = paint(" " * 2 + "─" * max(w - 4, 0), DIM)
    return rule + "\n" + " " * max((w - vlen(plain)) // 2, 0) + styled


def _clip(text, width):
    """Potong teks (dilihat dari vlen) dengan elipsis."""
    return text if vlen(text) <= width else text[: max(width - 1, 0)] + "…"


def render_menu(labels, selected, descs=None, avail_rows=None):
    """Menu satu kolom: blok dipusatkan, tepi kiri SEJAJAR, ada scroll.

    Mengembalikan list baris (menu + baris kosong + deskripsi item terpilih).
    """
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
    if truncated and start:
        lines.append(pad + paint(f"  ↑ {start} lagi", DIM))
    elif truncated:
        lines.append("")
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
    lines.append(" " * max((w - vlen(desc)) // 2, 0) + paint(desc, DIM) if desc else "")
    return lines
