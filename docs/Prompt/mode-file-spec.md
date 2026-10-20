# Spec: Mode File (Enkripsi/Dekripsi/Hash Berkas)

**Status:** DRAFT — label APPROVED dipasang **saat merge** (lihat §10)
**Tanggal:** 2026-10-20 (revisi 7)
**Target:** `main` pasca-PR #3 (`abe1e4f`)
**Prinsip:** 1 step = 1 commit · scope = spec ini saja · no behavior change untuk jalur teks (kecuali yang dinyatakan) · no new deps (stdlib only) · `core/` **tidak disentuh** kecuali penambahan field D11 (`raw_bytes` di `AesGcmResult`, §3.1)

---

## 0. Riwayat Revisi

| Rev | Perubahan |
|-----|-----------|
| 1 | Draf awal |
| 2 | Menutup 4 celah wajib (dekripsi biner, batas ukuran per-format, konflik F2/X2/D5, `argparse` vs runtime) + 7 perbaikan; tambah `--format hex\|base64\|raw` (D3′); verifikasi signature core (§1.1). |
| 3 | Koreksi klaim salah (§5.0: pesan argparse **memang berubah** → snapshot diperbarui sengaja); tambah **D11** (`raw_bytes` di `AesGcmResult`, opsi 1 disetujui) + tabel kasus GCM UTF-8/hex; geser status APPROVED ke saat merge. |
| 4 | Tegaskan **posisi field** D11 (Opsi B: sebelum `status_message`, jika tidak → `TypeError`); selaraskan §4 + prinsip kepala dokumen dengan pengecualian D11; tambah tes regresi `output_text`/`is_utf8`/`payload` + kasus kosong & 1 byte di F0b; tambah §6.3 (catatan snapshot parser: `COLUMNS`, versi Python, `-t`+`-f`). |
| 5 | Perkuat bukti pemanggilan (§3.1): `git grep -rn "AesGcmResult(" -- src tests` (cakupan `src` **dan** `tests`), bukan regex lokal; catat batas bukti skrip (*dataclass tiruan*). Tes F0b pakai **konstanta** (bukan snapshot dinamis). Hapus item tes "cek via review kode" (tak eksekutabel; kasus `"deadbeef"` sudah menjaganya). Nyatakan status `verify_*.py` (bukan dikoleksi pytest). |
| 6 | Rapikan sisa rev-3 di header/§3 (kini rev-6); hapus ambiguitas **F2 vs F3** di §6; koreksi panjang hex F0b (`os.urandom(64)` → **128** char, bukan 62+); catat hasil cek `pyproject.toml` (`python_files` tidak diubah → `verify_*.py` tetap tidak dikoleksi); tandai `verify_field_placement.py` sebagai bukti semantik saja, dilipat/hapus setelah F0b. |
| 7 | Koreksi §6.3 butir 3: kasus `-t` + `-f` bersama **tidak mungkin** direkam di F0 (opsi `-f` belum ada → pesan saat ini `unrecognized arguments`). F0 merekam perilaku apa adanya; `-t` + `-f` + pembaruan snapshot dipindah ke F1. |

**Verifikasi core (diminta reviewer):** dicek langsung, lihat §1.1, §1.2, dan
`tests/file_mode/verify_core_bytes.py` (skrip pembuktian yang bisa dijalankan).

> **Status skrip di `tests/file_mode/`.** Kedua berkas bernama `verify_*.py`, **bukan**
> `test_*.py`, sehingga **tidak dikoleksi pytest**. Ini disengaja: PR ini adalah PR
> dokumen, dan skrip-skrip tersebut hanyalah alat bukti manual (dijalankan dengan
> `python tests/file_mode/verify_*.py`), bukan bagian dari suite tes. Keduanya akan
> digantikan/ dilengkapi oleh `tests/test_file_mode.py` pada F0/F0b.
>
> **Sudah diverifikasi (bukan asumsi):** `pyproject.toml` hanya menetapkan
> `[tool.pytest.ini_options] testpaths = ["tests"]` dan `pythonpath = ["src"]` —
> **tidak** mengubah `python_files`. Tidak ada `pytest.ini`/`setup.cfg`/`tox.ini`.
> Dicek dengan `pytest --collect-only tests/file_mode/` → **`no tests collected`**.
>
> **`verify_field_placement.py` = bukti semantik, bukan bukti D11.** Ia memakai
> dataclass tiruan (semantik Python). Pengecekan pada kelas nyata ("tidak ada field
> non-default setelah default") **tidak membuktikan apa-apa** sebelum F0b: kelas yang
> sudah bisa di-import pasti lolos karena `dataclass` sendiri sudah menolaknya. Bukti
> nyata untuk D11 adalah tes F0b. Setelah F0b selesai, skrip ini **dihapus** atau
> **dilipat** ke `tests/test_file_mode.py`.

---

## 1. Latar Belakang

Saat ini CryptoLab hanya bisa memproses **teks** yang diketik/ditempel di terminal.
Opsi `-t/--text` bersifat `required=True` di hampir semua sub-perintah
(`src/cryptolab/cli/parser.py`), dan menu interaktif selalu meminta input teks.

Akibatnya, berkas nyata (foto, dokumen, arsip) tidak bisa diproses. Tujuan utama
fitur ini: **berkas biner bisa dienkripsi lalu didekripsi kembali ke byte yang identik.**

### 1.1 Temuan Verifikasi: Core Sudah Mendukung Bytes ✅

Diperiksa langsung (bukan asumsi):

| Fakta | Bukti |
|---|---|
| `aes_encrypt(plaintext: Union[str, bytes], ...)` | `core/symmetric/aes.py:81-87` |
| `aes_decrypt(ciphertext_hex: str, ...)` — argumen **hex**, bukan bytes | `core/symmetric/aes.py:169-175` |
| `AesResult.raw_bytes: bytes` berisi **byte asli** (plaintext pada dekripsi, ciphertext pada enkripsi) | `core/symmetric/aes.py:34, 159, 277` |
| `AesGcmResult` **tidak** punya `raw_bytes` — hanya `output_text`, yang **berisi teks saat UTF-8 dan hex saat non-UTF8** (lihat §1.2) | `core/symmetric/aes.py:358-370` |
| `_to_bytes` menerima `str` maupun `bytes` | `core/symmetric/aes.py:43-51` |
| `_clean_hex` sudah `strip()` + buang `0x`/`:`, `-`, whitespace internal | `core/symmetric/aes.py:54-78` |

**Hasil uji nyata** (64 byte `os.urandom`, bukan UTF-8):
```
AES-CBC: aes_encrypt(binary) -> raw_bytes=80B ; aes_decrypt(...).raw_bytes == binary  →  True
AES-GCM: aes_gcm_encrypt(binary) -> payload "nonce:cipher:tag" ; is_utf8=False
```

### 1.2 Temuan Kritis: `output_text` GCM Bukan Selalu Hex ⚠️

Diuji ulang dengan tiga plaintext (menutup celah yang benar ditandai reviewer):

| Plaintext | `is_utf8` | `output_text` | `bytes.fromhex(output_text)` |
|---|---|---|---|
| `"halo"` | `True` | `'halo'` (teks) | **GAGAL** (`ValueError`) |
| `"deadbeef"` | `True` | `'deadbeef'` (teks) | **berhasil tapi SALAH** — mengembalikan `b'\xde\xad\xbe\xef'`, bukan `b"deadbeef"` |
| `os.urandom(64)` | `False` | hex string | benar |

Kasus kedua adalah jenis terburuk: **berhasil tanpa galat, tapi hasil salah.** Ini
membuktikan `output_text` **tidak boleh** dipakai mentah untuk jalur berkas.

**Penanda yang tersedia:** `is_utf8`. Implementasi core membentuk keduanya dalam satu
`try/except` (`aes.py:476-486`), jadi `is_utf8` konsisten dengan bentuk `output_text`.
Jalur aman tanpa mengubah core:

```python
pt = result.output_text.encode("utf-8") if result.is_utf8 \
     else bytes.fromhex(result.output_text)
```

Namun ketergantungan implisit ini **rapuh** (tidak ada batas tipe yang menegakkannya).
Karena itu **D11** memutuskan menambah `raw_bytes` (§3.1) agar penyamaan dengan
`AesResult` eksplisit dan asimetri API hilang.

**Kesimpulan:** tujuan fitur (round-trip biner) tercapai. Pola yang dipakai:

- **Enkripsi:** teruskan `bytes` langsung ke `aes_encrypt` / `aes_gcm_encrypt`.
- **Dekripsi CBC:** ambil `result.raw_bytes` (byte asli).
- **Dekripsi GCM:** dengan **D11**, ambil `result.raw_bytes` (sama seperti CBC).
  Sebelum D11 diimplementasi, pakai jalur `is_utf8` di atas — **jangan** `output_text` mentah.
  Perbedaan ini **wajib** ditangani di `cli/input.py`, bukan diseragamkan di core.

---

## 2. Ruang Lingkup

### Termasuk (in-scope)

| No | Item |
|----|------|
| S1 | Opsi CLI `-f/--file PATH` sebagai alternatif `-t/--text` |
| S2 | Opsi CLI `-o/--out PATH` untuk menulis hasil ke berkas |
| S3 | Mode **read-all** (baca seluruh isi → proses → tulis) |
| S4 | Algoritma: **AES-CBC** dan **AES-GCM** (AEAD) |
| S5 | `--format hex\|base64\|raw` (lihat D3′) |
| S6 | **Dekripsi ke berkas biner** — inti tujuan fitur |
| S7 | Menu interaktif "Mode File" (D8) |
| S8 | Pesan galat berkas yang ramah |
| S9 | `hash --file` (memakai `hash_file` yang sudah ada, **tanpa batas 10 MB**) |

### Tidak termasuk (out-of-scope, sengaja ditunda)

| No | Item | Alasan |
|----|------|--------|
| X1 | Mode **chunked/streaming** | butuh format ber-header antar-blok; fase 2 |
| X2 | Mode file untuk **DES, RC2, RSA, klasik** | tidak AEAD / kunci pendek / lambat untuk berkas besar |
| X3 | Format berkas ber-header (magic bytes, metadata) | keputusan fase 2 bersama X1 |
| X4 | Integritas otomatis untuk AES-CBC | GCM sudah AEAD; CBC ditunda (lihat §7.4) |
| X5 | Kompresi (`--compress`) | gunakan `tar czf` / `gzip` di luar tool untuk sekarang; fase 2 (lihat §7.7) |
| X6 | Progres bar | baru berguna bersama X1 |

**Catatan konsistensi (menutup konflik rev-1):** X2 melarang DES/RC2.
Karena itu **F2 hanya memperluas ke AES-CBC** — DES/RC2 **tidak** muncul di manapun
dalam tahapan, termasuk F2. D5 tidak lagi punya opsi "semua simetris".

---

## 3. Keputusan Desain (DISETUJUI)

| Kode | Keputusan | Nilai final |
|------|-----------|-------------|
| D1 | Sumber input | `-f/--file PATH`, mutually exclusive dengan `-t/--text` (lihat §5.0) |
| D2 | Tujuan output | `-o/--out PATH`; tanpa `--out` → stdout |
| D3′ | Format output | `--format hex\|base64\|raw`, **default `hex`**; `raw` **wajib** `--out` |
| D4 | Batas ukuran | Batas pada **ukuran plaintext**; limit per-format di §5.3 |
| D5 | Algoritma fase 1 | **AES-GCM + AES-CBC** (DES/RC2 ❌) |
| D6 | Payload GCM | `nonce_hex:ciphertext_hex:tag_hex` (format `aes_gcm_encrypt` apa adanya) |
| D6b | Payload CBC | `iv_hex:ciphertext_hex` (format baru di lapisan CLI, lihat §5.2) |
| D7 | Berkas output sudah ada | **tolak**, perlu `--force`; tulis atomik (§5.4) |
| D8 | Menu interaktif | ya — "Mode File" di tab Simetris & Hash |

**Keputusan tambahan (rev-2):**
- **D9** Dekripsi menerima `--format` yang sama dengan enkripsi. **Tidak ada auto-detect.**
- **D10** Dekripsi tanpa `--out` yang menghasilkan non-UTF8 → **galat jelas**, bukan dump byte.

**Keputusan tambahan (rev-3):**
- **D11** Tambah field `raw_bytes: bytes` ke `AesGcmResult` (**opsi 1** yang disarankan
  reviewer), dengan pengecualian tertulis "core beku". Lihat §3.1.

### 3.1 D11 — `raw_bytes` pada `AesGcmResult`

**Masalah (§1.2):** `AesGcmResult.output_text` berisi teks untuk UTF-8 dan hex untuk
non-UTF8. `bytes.fromhex()` pada kasus UTF-8 bisa **gagal** atau, lebih buruk,
**berhasil dengan hasil salah** (`"deadbeef"` → `b'\xde\xad\xbe\xef'`).
`AesResult` (CBC) sudah punya `raw_bytes`; `AesGcmResult` belum → asimetri.

**Keputusan:** tambah field `raw_bytes: bytes` ke `AesGcmResult`, berisi:
- enkripsi → ciphertext bytes; dekripsi → plaintext bytes **apa adanya**.

**Penilaian dampak (untuk pengecualian "core beku"):**
| Aspek | Temuan |
|---|---|
| Bentuk | `@dataclass`, field diakses **by-name** (tidak ada positional unpacking) |
| Konstruktor | hanya 2 tempat: `aes.py:407` (encrypt), `aes.py:488` (decrypt) |
| Pemakai `raw_bytes` GCM | **tidak ada** — aman ditambah |
| Pemakai `output_text`/`is_utf8` | tetap berfungsi; field baru aditif |
| Tes terdampak | tidak ada yang mengharapkan signature berubah |

**Penyesuaian field — WAJIB, jika tidak `import` langsung gagal.** Struktur saat ini:

```python
@dataclass
class AesGcmResult:
    operation: str
    key_repr: str
    nonce_hex: str
    payload: str
    output_text: str
    is_utf8: bool
    technical_success: bool          # batas terakhir field TANPA default
    status_message: str = ""         # <-- mulai ada default
    reasons: List[str] = field(default_factory=list)
```

`raw_bytes: bytes` **tanpa default** tidak boleh ditaruh setelah `status_message`
→ `TypeError: non-default argument 'raw_bytes' follows default argument`
(diverifikasi: lihat `tests/file_mode/verify_field_placement.py`).

**Pilihan (diputuskan): Opsi B — selipkan sebelum field berdefault**, sejajar dengan
`AesResult` yang juga menaruh `raw_bytes` di antara field non-default:

```python
    technical_success: bool
    raw_bytes: bytes                 # <-- di sini (non-default)
    status_message: str = ""
    reasons: List[str] = field(default_factory=list)
```

Alasan: menyamakan posisi dengan `AesResult`, dan tidak menciptakan default palsu
`b""` yang bisa menyembunyikan lupa-isi.

**Bukti pemanggilan (definitif, bukan heuristik):** `git grep -rn "AesGcmResult(" -- src tests`
menghasilkan **tepat dua** pemanggil, keduanya di `aes.py` (`:407`, `:488`), dan keduanya
memakai **keyword murni** — setiap argumen berbentuk `nama=...` (dibaca langsung, bukan
regex `"=" in body`). Karena itu penempatan field baru **tidak** menggeser pemanggilan,
dan **kedua** konstruktor wajib menambahkan `raw_bytes=...`
(`:407` encrypt → `ct_bytes`; `:488` decrypt → `pt_bytes`).

> Cakupan bukti: grep mencakup seluruh `src/` **dan** `tests/`, sehingga pemanggil di
> luar `aes.py` (termasuk tes) ikut terperiksa. Bila kelak muncul pemanggil baru, ia
> akan terlihat di grep yang sama.

> **Batas bukti `verify_field_placement.py`.** Skrip itu memakai **dataclass tiruan**,
> bukan `AesGcmResult` asli. Tujuannya membuktikan **semantik Python** (aturan urutan
> field dataclass), bukan menguji kelas nyata. Bukti atas kelas nyata berasal dari grep
> di atas + tes F0b. Jangan memperlakukan skrip ini sebagai bukti perilaku `AesGcmResult`.

> Alternatif bila ingin tanpa menyentuh urutan: Opsi C — `raw_bytes: bytes = b""`
> di paling belakang. Tidak dipilih karena default kosong menutupi lupa-isi.

**Penyesuaian:** `raw_bytes` diletakkan sebelum `status_message` (Opsi B). Perubahan
bersifat **aditif saja**; perilaku `output_text`/`is_utf8` tidak diubah dan harus
dibuktikan tidak berubah (tes regresi F0b).

**Pengecualian tertulis "core beku":** D11 adalah satu-satunya perubahan yang diizinkan
menyentuh `core/symmetric/aes.py`, dan hanya penambahan field. Logika kripto
(tag, nonce, payload) **tidak** berubah. Bila pemilik proyek memilih **opsi 2/3**
(panggil primitif di `cli/input.py`, atau jangan pernah pakai `output_text`), spec
§3.1 diganti dengan catatan itu dan core tetap tidak disentuh — tetapi **opsi 1
disetujui** karena menyamakan asimetri dan mencegah kelas bug §1.2.

---

## 4. Perubahan yang Direncanakan (per berkas)

> Belum ada kode diubah. Prediksi ini akan dikoreksi saat implementasi.

| Berkas | Perubahan |
|--------|-----------|
| `src/cryptolab/cli/parser.py` | Ganti `required=True` pada `-t` dengan `add_mutually_exclusive_group(required=True)`; tambah `-f`, `-o`, `--force`, `--format` |
| `src/cryptolab/cli/input.py` **(baru)** | `read_input`, `read_file_bytes`, `write_output`, konversi format, `payload` CBC/GCM |
| `src/cryptolab/core/symmetric/aes.py` | **HANYA D11**: selipkan field `raw_bytes: bytes` sebelum `status_message` (Opsi B, §3.1) + isi di 2 konstruktor (`:407`, `:488`). Tidak ada perubahan logika kripto, `output_text`, atau `is_utf8`. |
| `src/cryptolab/cli/commands/symmetric.py` | Pakai `cli/input.py`; jalur `--text` tetap identik |
| `src/cryptolab/cli/commands/hashing.py` | `hash --file` → **`hash_file()` langsung** (bukan `read_input`) |
| `src/cryptolab/interactive/handlers/ctx_symmetric.py` | Handler "Mode File" |
| `src/cryptolab/interactive/handlers/ctx_hashing.py` | Handler "Hash File" |
| `src/cryptolab/interactive/tab_menu.py` | Item baru di `CATEGORIES` |
| `tests/test_file_mode.py` **(baru)** | Karakterisasi + round-trip + batas + galat (lihat §6) |
| `tests/test_tahap3_modes.py` | Tambah tes GCM: UTF-8 biasa, `"deadbeef"`, `os.urandom`, kosong, 1 byte, regresi `output_text`/`is_utf8`, dan `raw_bytes` == asli |

**Tidak disentuh:** `core/hashing.py` dan `core/encoding/*.py`.
`core/symmetric/*.py` **hanya** `aes.py` untuk penambahan field D11 (§3.1) —
`des.py`, `rc2.py`, dan `__init__.py` tidak disentuh.

---

## 5. Kontrak Perilaku

### 5.0 Parsing argumen (menutup masalah 4) — **KOREKSI rev-3**

**Opsi terpilih: `add_mutually_exclusive_group(required=True)`.** Tetap yang terbersih:
validasi di parse-time (exit code 2) dan "keduanya sekaligus" ditolak argparse tanpa
kode manual.

> ⚠️ **Koreksi klaim rev-2.** Rev-2 menulis "pesan galat 'tanpa input' tidak berubah".
> **Itu salah.** Group memang menjaga parse-time & exit code, tetapi teksnya berubah:

| | Sebelum | Sesudah |
|---|---|---|
| Tanpa input | `the following arguments are required: -t/--text` | `one of the arguments -t/--text -f/--file is required` |
| Baris usage `--help` | `-t TEXT` | `[-t TEXT \| -f FILE]` |

Jadi bila `tests/test_cli_snapshot.py` mengunci pesan galat atau blok usage `--help`
untuk sub-perintah terkait, tes itu **akan gagal** dan **harus diperbarui**.

**Keputusan:** **terima perubahannya** dan nyatakan sebagai **pengecualian tertulis**
"no behavior change" (sama seperti F4):

> **Pengecualian #2 (parser).** `-t/--text` menjadi bagian mutually-exclusive group,
> sehingga pesan galat "tanpa input" dan baris usage `--help` berubah. Perubahan ini
> **disengaja**. Snapshot yang terkait diperbarui di F0/F1 dengan alasan tertulis di
> commit. Tidak ada perubahan pada hasil operasi untuk `--text` yang valid.

**Karakterisasi wajib (F0):** snapshot **harus** mencakup, untuk **setiap sub-perintah**:
1. teks galat argparse saat tidak ada `-t`/`-f`,
2. baris usage dari `--help`,
3. teks galat saat `-t` **dan** `-f` diberikan bersamaan.

Ketiganya direkam **sebelum** F1, supaya diff-nya terlihat dan disetujui, bukan
ditemukan setelah tes merah.

Akibatnya `InvalidInputError` di §5.1 **hanya** untuk galat runtime berkas
(tidak ada, bukan berkas, terlalu besar, izin), bukan untuk "tidak ada input".

```python
grup = parser.add_mutually_exclusive_group(required=True)
grup.add_argument("-t", "--text")
grup.add_argument("-f", "--file")
```

### 5.1 Membaca input

```
read_input(args) -> bytes
  args.file  -> bytes isi berkas (baca read(limit+1), lihat §5.3)
  args.text  -> args.text.encode("utf-8")
```
Galat runtime → `InvalidInputError`:

| Kondisi | Pesan |
|---|---|
| Berkas tidak ada | `Berkas tidak ditemukan: <path>` |
| Bukan berkas (direktori) | `<path> bukan berkas biasa.` |
| Melebihi batas (§5.3) | `Berkas <N> MB melebihi batas <limit> MB untuk format <fmt>. Gunakan --format raw atau berkas lebih kecil.` |
| Izin ditolak | `Tidak bisa membaca berkas: <alasan singkat>` |

### 5.2 Konversi format & payload

**Enkripsi:**
1. `bytes` → core (`aes_encrypt` / `aes_gcm_encrypt`).
2. Ambil ciphertext: CBC → `result.output_text` (hex); GCM → `result.payload`.
3. Bungkus sesuai `--format`:

| Format | Enkripsi (tulis) |
|--------|------------------|
| `hex` | CBC: `iv_hex:ciphertext_hex`; GCM: `nonce:cipher:tag` |
| `base64` | base64 dari **bytes** payload: CBC `iv ‖ ct`; GCM `nonce ‖ ct ‖ tag` |
| `raw` | bytes mentah: CBC `iv(16) ‖ ct`; GCM `nonce(12) ‖ ct ‖ tag(16)` |

**Dekripsi** (harus `--format` sama; **tanpa auto-detect**, D9):
1. Baca bytes/teks.
2. `hex` → `strip()` lalu toleransi newline internal (lihat §5.5).
3. Rekonstruksi `ciphertext_hex` + `iv`/`nonce`/`tag` → panggil core.
4. Ambil plaintext **selalu dari `result.raw_bytes`** (CBC dan GCM sama, setelah D11):
   - CBC → `result.raw_bytes` (bytes asli) ✅
   - GCM → `result.raw_bytes` (bytes asli) ✅ — **jangan** pakai `output_text` mentah

> **Aturan wajib (D11):** `cli/input.py` **tidak boleh** memanggil `bytes.fromhex(result.output_text)`
> pada hasil GCM. `output_text` berisi teks saat UTF-8 dan hex saat non-UTF8 (§1.2),
> sehingga pemakaian mentah bisa **gagal** atau **berhasil dengan hasil salah**.
> Selalu pakai `raw_bytes`.

**Bila D11 belum diimplementasi (urutan kerja):** jalur sementara yang benar adalah
`result.output_text.encode("utf-8") if result.is_utf8 else bytes.fromhex(result.output_text)`.
Jalur ini **tetap** diuji ketiga kasus §1.2 dan dihapus setelah D11 masuk.

### 5.3 Batas ukuran (menutup masalah 2 — asimetri hex)

Batas didefinisikan pada **ukuran plaintext**. Untuk dekripsi, batas berkas input
dihitung dari limit × faktor format + overhead:

| Format | Faktor | Overhead | Batas berkas dekripsi (limit=10 MB) |
|--------|--------|----------|-------------------------------------|
| `raw`  | 1×     | +28 B (GCM) / +16 B (CBC) | 10 MB + 32 B |
| `hex`  | 2×     | +28×2 kar + 1 pemisah | 20 MB + ~64 B |
| `base64` | 1,34× | +40 B | ~13,4 MB + 48 B |

**Aturan:**
- `LIMIT_PLAINTEXT = 10 * 1024 * 1024` (konstanta `cli/input.py`).
- Baca dengan `f.read(LIMIT + 1)`; tolak bila `len > LIMIT` (aman terhadap berkas
  yang berubah ukuran antara `stat()` dan baca).
- Untuk dekripsi, limit input = `LIMIT_PLAINTEXT * faktor + overhead`.
- **Tes di `limit` tepat dan `limit + 1`, untuk tiap format.**

### 5.4 Menulis output

```
write_output(path, data: bytes, force=False)
```
- Tanpa `--out`:
  - `--format hex|base64` → cetak ke stdout (aman).
  - `--format raw` → **galat**: `Format raw butuh --out; byte mentah tidak dicetak ke terminal.`
  - Dekripsi non-UTF8 (`--format hex`) → tetap hex, aman dicetak.
  - Dekripsi non-UTF8 **dengan** `--out` → tulis `raw_bytes` biner (inti S6).
- Dengan `--out`:
  - Tolak bila `--out == --file` (jalur sama) → `--out tidak boleh sama dengan --file.`
  - Tanpa `--force`: buka dengan mode **`xb`** (create-exclusive) — bukan cek `exists()`
    lalu tulis. Bila ada → `Berkas <path> sudah ada. Pakai --force untuk menimpa.`
  - Tulis **biner** (`"wb"`)/`"xb"` selalu, agar Windows tidak menerjemahkan newline.
  - `--force`: tulis ke berkas sementara `.tmp` di direktori yang sama, lalu
    `os.replace()` → atomik, berkas asli tidak rusak bila proses gagal di tengah.
  - Direktori tujuan tidak ada → galat ramah `Direktori tujuan tidak ada: <dir>`.
  - Bila `--out` dipakai, kotak hasil tetap dicetak tetapi `output_text` diganti
    ringkasan `Ditulis ke <path> (<N> byte)`.

### 5.5 Dekripsi toleran whitespace

- `--format hex`: `strip()` dulu; **toleransi newline di tengah** (konversi
  `\r\n`/`\n` → buang sebelum `bytes.fromhex`).
  Alasan: `cmd > out.hex` menambah newline; editor sering menambah juga.
- `--format base64`: gunakan `base64.b64decode(data, validate=False)` + buang whitespace.
- Tes: input dengan newline akhir, CRLF, dan newline di tengah.

---

## 6. Rencana Tahapan (1 step = 1 commit)

| Step | Isi | Tes | Catatan |
|------|-----|-----|---------|
| **F0** | Karakterisasi jalur `--text`, **teks galat argparse & `--help`**, `--format` parsing | `tests/test_file_mode.py` | Belum ada fitur menu. **Snapshot parser diperbarui sengaja** (§5.0) |
| **F0b** | **D11**: selipkan `raw_bytes` sebelum `status_message` (Opsi B, §3.1) + isi di 2 konstruktor | `tests/test_tahap3_modes.py` (kasus §6.1 GCM + regresi `output_text`/`is_utf8`/`payload`) | Satu-satunya sentuhan ke `core/` (§3.1) |
| **F1** | `cli/input.py` + `--file`/`--out`/`--force`/`--format` untuk **AES-GCM & AES-CBC** | §6.1 | Termasuk round-trip biner |
| **F2** | `hash --file` → `hash_file` **langsung** (streaming 8 KB, **tanpa** batas 10 MB) | hash berkas besar (>10 MB) lolos | Lihat §6.2. Berisi satu perintah saja (hash) |
| **F3** | Perluas `--file`/`--format` ke perintah lain yang relevan + dokumentasi `--format` | round-trip per perintah | **Tanpa DES/RC2** (X2) |
| **F4** | Menu interaktif "Mode File" (+ Hash File) | snapshot menu | **PR terpisah** (lihat §12) |
| **F5** | Docs: `docs/USAGE.md` + README | — | — |

> F0b ditulis sebelum F1 agar `cli/input.py` langsung memakai `raw_bytes` untuk
> **kedua** algoritma — tidak perlu jalur sementara `is_utf8` sama sekali.

### 6.1 Daftar tes F1 (wajib, menutup permintaan reviewer)

- [ ] Round-trip biner: `os.urandom` (non-UTF8) → encrypt → decrypt == asli
- [ ] **Berkas kosong** (0 byte)
- [ ] **1 byte**
- [ ] Non-UTF8 (`os.urandom`)
- [ ] **Kunci salah** → galat ramah (bukan traceback)
- [ ] **Tag GCM dirusak** → `DecodingError` generik
- [ ] **Direktori `--out` tidak ada** → galat ramah
- [ ] Batas tepat `limit` dan `limit + 1`, **per format** (hex/base64/raw)
- [ ] Dekripsi hex dengan: newline akhir, CRLF, **newline di tengah**
- [ ] `--format raw` tanpa `--out` → galat
- [ ] `--out` sama dengan `--file` → galat
- [ ] `--out` ada tanpa `--force` → galat; dengan `--force` → tertimpa (atomik)
- [ ] `--text` dan `--file` bersama → argparse exit 2
- [ ] Tanpa `--text`/`--file` → argparse exit 2, **pesan baru direkam** (§5.0, bukan diklaim sama)

**Tes khusus GCM (mencegah bug §1.2) — wajib, di F0b dan diulang di F1:**

- [ ] GCM plaintext `"halo"` (UTF-8 biasa) → round-trip byte == `b"halo"`
- [ ] GCM plaintext `"deadbeef"` (UTF-8 **dan** hex valid) → round-trip byte ==
      `b"deadbeef"` (**bukan** `b'\xde\xad\xbe\xef'`)
- [ ] GCM plaintext `os.urandom(64)` (non-UTF8) → round-trip byte == asli
- [ ] GCM plaintext **kosong** (`b""`) → `raw_bytes == b""`
- [ ] GCM plaintext **1 byte** (`b"A"` dan 1 byte non-UTF8 `b"\xff"`) → `raw_bytes` == asli
- [ ] `AesGcmResult.raw_bytes` == plaintext asli untuk **semua** kasus di atas

> Item "pastikan tidak memakai `bytes.fromhex(output_text)`" **dihapus** — ia tidak
> dapat dieksekusi sebagai tes. Kasus `"deadbeef"` sudah menjaga perilaku itu
> (jalur `output_text` akan menghasilkan `b'\xde\xad\xbe\xef'` dan gagal).

**Tes regresi F0b (perilaku lama tidak boleh berubah) — pakai konstanta, bukan snapshot dinamis:**

- [ ] `output_text` dan `is_utf8` **identik** dengan konstanta yang sudah diketahui
      (tidak perlu merekam secara dinamis — nilainya sudah pasti):
      | plaintext | `output_text` | `is_utf8` |
      |---|---|---|
      | `"halo"` | `"halo"` | `True` |
      | `"deadbeef"` | `"deadbeef"` | `True` |
      | `os.urandom(64)` | hex dari plaintext (**2 × panjang byte** = 128 char) | `False` |

      > Untuk kasus non-UTF8, `output_text` = `plaintext.hex()`, jadi panjangnya
      > **selalu 2 × jumlah byte** (64 byte → **128 char**, bukan 62+). Tes tidak
      > boleh menyalin angka tetap; bandingkan dengan `plaintext.hex()`.
- [ ] `aes_gcm_encrypt(...).payload` **identik** formatnya (masih `nonce:ct:tag` hex)
- [ ] `tests/test_tahap3_modes.py` lama **tetap hijau tanpa diubah** (selain penambahan tes)
- [ ] `import cryptolab` dan `AesGcmResult(...)` **tidak** TypeError (verifikasi posisi field §3.1)

### 6.3 Catatan penting untuk F0 (snapshot parser — rapuh)

Snapshot `--help` dan teks galat argparse mudah rapuh. Aturan saat merekam:

1. **Lebar terminal:** set `COLUMNS=80` (atau nilai tetap) di fixture sebelum memanggil
   `--help`. Tanpa itu, lebar baris usage bergantung pada ukuran terminal.
2. **Versi Python:** format pesan argparse dapat berbeda antar versi (mis. heading
   `options:` vs `optional arguments:` yang berubah di 3.10). Pilih salah satu:
   - catat versi Python (mis. 3.12.10) dan pakai `requires-python` minimum sebagai acuan, atau
   - **normalisasi** sebelum membandingkan (mis. samakan heading, lipat whitespace).
   Rekomendasi: normalisasi + tes yang hanya mengunci **substring stabil**
   (`is required`, `not allowed with argument`), bukan seluruh blok usage.
3. **Pembagian F0 vs F1 untuk kasus `-t` + `-f` bersama (koreksi rev-6 → rev-7):**
   - **F0 merekam perilaku APA ADANYA pada kode yang belum berubah.** Karena `-f`
     belum ada, `-t` + `-f` saat ini menghasilkan `unrecognized arguments: -f`.
     Jadi F0 **tidak** merekam pesan `not allowed with argument` (tidak mungkin).
     F0 merekam: (a) tanpa `-t`, (b) `--help`, (c) `-t` saja → **semua hijau**.
   - **F1** menambahkan kasus `-t` + `-f` (pesan `argument -f/--file: not allowed with
     argument -t/--text`) **dan** memperbarui secara sengaja snapshot "tanpa input"
     serta baris usage. **Diff snapshot di commit F1 itulah dokumentasi perubahan**
     yang disetujui di §5.0.
4. Untuk tiap sub-perintah, F0 rekam: (a) tanpa `-t`, (b) `--help`, (c) `-t` saja.
   Kasus `-t` + `-f` ditambahkan di F1 (lihat butir 3).

### 6.2 `hash --file` (perbaikan rev-2)

- `hash --file` memanggil `hash_file(filepath, algorithm)` **langsung**
  (`core/hashing.py:169`) — **bukan** lewat `read_input`.
- Karena `hash_file` sudah streaming 8 KB, **tidak ada batas 10 MB** untuk hash.
- Ini dinyatakan eksplisit agar wiring tidak salah memakai batas read-all.
- Jalur `hash --text` tetap identik.

---

## 7. Catatan Teknis Pendukung

### 7.1 Format payload AES-CBC (menutup celah rev-2)
Format resmi di lapisan CLI: **`iv_hex:ciphertext_hex`**.
`aes_encrypt` mengembalikan `iv_repr` dan `output_text`; `aes_decrypt` menerima
`iv` terpisah. Untuk `raw`: `iv(16) ‖ ciphertext`. Untuk `base64`: base64 dari bytes itu.

### 7.2 Dekripsi GCM vs CBC (asimetri API) — diselesaikan D11
`AesResult.raw_bytes` ada; `AesGcmResult` **belum** (D11 menambahkannya). Ditangani di
`cli/input.py` (§5.2): setelah D11, **kedua** algoritma memakai `result.raw_bytes`.
Ditambah tes khusus (§6.1) yang memastikan kedua jalur menghasilkan byte identik, plus
tiga kasus plaintext GCM (UTF-8 biasa, `"deadbeef"`, `os.urandom`) untuk mencegah
regresi bug §1.2.

### 7.3 Galat dekripsi AES-CBC tanpa integritas
- `unpad` gagal → core sudah memberi `DecodingError` "Padding PKCS#7 tidak valid
  (...)". Diteruskan apa adanya tetapi **dibungkus pesan ramah**:
  `Dekripsi gagal: kunci salah atau berkas rusak.` (tanpa detail padding → no oracle).
- Docs menyatakan **GCM disarankan** untuk berkas (AEAD).
- X4 tetap ditunda.

### 7.4 CheckNow: integritas
X4: CBC tidak punya tag. Tidak ada perubahan; hanya pesan + docs (§7.3).

### 7.5 Kesesuaian dengan fase 2
`--format raw` tanpa header tidak bertentangan dengan X1/X3: saat chunked dikerjakan,
format ber-header menggantikan layout raw polos. Sekarang raw polos cukup.

### 7.6 Prinsip "no behavior change" — pengecualian tertulis
- Jalur `--text` **tanpa** `--out`: byte keluaran operasi identik (dikunci snapshot lama).
- **Pengecualian #1 — F4 (menu interaktif):** menambah item, sehingga snapshot menu
  berubah. Disengaja dan disetujui.
- **Pengecualian #2 — parser (§5.0):** `-t` masuk mutually-exclusive group, sehingga
  pesan galat "tanpa input" **berubah** (`the following arguments are required: -t/--text`
  → `one of the arguments -t/--text -f/--file is required`) dan usage `--help` menjadi
  `[-t TEXT | -f FILE]`. Disengaja; snapshot terkait diperbarui di F0/F1.
- **Pengecualian #3 — D11 (§3.1):** satu-satunya perubahan pada `core/symmetric/aes.py`,
  yaitu penambahan field `raw_bytes` ke `AesGcmResult`. Aditif; logika kripto tidak berubah.

### 7.7 Kompresi
Tetap X5 untuk fase 1. Cara tanpa ubah kode: `tar czf data.tar.gz folder/` lalu
`cryptolab ... --file data.tar.gz`. Bila kelak jadi fitur: urutan **kompres → enkripsi**
(kompres setelah enkripsi tidak berguna), `--compress` eksplisit (tanpa auto-detect),
batas hasil dekompresi via `zlib.decompressobj().decompress(data, limit+1)` untuk
mencegah decompression bomb, dan catat kebocoran panjang (rendah untuk tool offline).

---

## 8. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Ciphertext biner tumpah ke terminal | `raw` wajib `--out`; default hex |
| Dekripsi non-UTF8 gagal ditulis | `raw_bytes` ditulis biner (§5.4, S6) |
| Round-trip gagal di batas | Batas pada plaintext + limit per-format (§5.3) + tes batas |
| Berkas besar menghabiskan memori | Limit 10 MB + `read(limit+1)`; chunked fase 2 |
| Menimpa berkas pengguna | `xb` + `--force` + tulis atomik (`os.replace`) |
| Snapshot parser berubah | Disengaja (§5.0); teks galat & `--help` **direkam di F0** lalu diperbarui |
| Wiring hash salah kena limit | §6.2 eksplisit: `hash_file` langsung |
| `--out` = `--file` merusak data | Ditolak eksplisit (§5.4) |
| **GCM `output_text` disalahartikan sebagai hex** | **D11** (`raw_bytes`) + aturan wajib §5.2 + tes 3 kasus §6.1 |

---

## 9. Definisi Selesai (DoD)

- [ ] Semua tes §6.1 lolos (termasuk 5 tes khusus GCM), plus regresi penuh (`pytest tests/ -q`) hijau
- [ ] `--text` tanpa `--out`: hasil operasi byte-identik; snapshot keluaran operasi hijau
- [ ] Snapshot parser (§5.0) **diperbarui dengan sengaja** dan alasan tertulis di commit
- [ ] `cli/input.py` **tidak pernah** memakai `result.output_text` GCM sebagai sumber byte
- [ ] README + `docs/USAGE.md` punya contoh: enkripsi foto → dekripsi → byte identik
- [ ] Tidak ada dependensi baru (hanya cek `pyproject.toml` tidak berubah)
- [ ] `core/` hanya berubah untuk D11: `git diff src/cryptolab/core/` **hanya** field `raw_bytes` di `aes.py`

---

## 10. Keputusan §3 — Status

Disetujui pemilik proyek: **D1, D2, D3′ (default hex), D5 (GCM+CBC), D6, D7, D8**,
**D4** disetujui bersyarat — syarat "batas simetris per-format" dipenuhi §5.3.
Rev-2: **D9** (tanpa auto-detect), **D10** (dekripsi non-UTF8 tanpa `--out` = galat).
Rev-3: **D11** (`raw_bytes` pada `AesGcmResult`, opsi 1).

**Status dokumen:** DRAFT. Label APPROVED dipasang **saat merge**, bukan sebelumnya.

---

## 11. Koreksi Kecil

- Typo rev-1 `memaki` → **`memakai`** (§10).
- Typo rev-2 di pesan commit `febb561` "Ditandemuan" → **"Ditemukan"**. Bila merge
  memakai squash, typo hilang dengan sendirinya; bila tidak, dibiarkan (pesan commit
  historis tidak ditulis ulang).

---

## 12. Catatan Penutup

- **F4 dipisah menjadi PR tersendiri** (nilai terendah, churn terbesar). F0–F3 dapat
  merge lebih dulu tanpa menyentuh snapshot menu.
- **F0b (D11)** dikerjakan sebelum F1, agar tidak perlu jalur sementara `is_utf8`.
- `--compress`, chunked, dan format ber-header tetap fase 2 (§7.7, X1/X3).

---

*Akhir spec. Implementasi dimulai dari F0 (karakterisasi, tanpa mengubah perilaku).*
