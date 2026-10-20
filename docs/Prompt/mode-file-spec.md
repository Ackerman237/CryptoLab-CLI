# Spec: Mode File (Enkripsi/Dekripsi/Hash Berkas)

**Status:** APPROVED (revisi 2) — keputusan §3 disetujui pemilik proyek
**Tanggal:** 2026-10-20 (revisi 2)
**Target:** `main` pasca-PR #3 (`abe1e4f`)
**Prinsip:** 1 step = 1 commit · scope = spec ini saja · no behavior change untuk jalur teks (kecuali yang dinyatakan) · no new deps (stdlib only)

---

## 0. Riwayat Revisi

| Rev | Perubahan |
|-----|-----------|
| 1 | Draf awal |
| 2 | Menutup 4 celah wajib (dekripsi biner, batas ukuran per-format, konflik F2/X2/D5, `argparse` vs runtime) + 7 perbaikan; tambah `--format hex\|base64\|raw` (D3′); verifikasi signature core (§1.1). |

**Verifikasi signature core (diminta reviewer):** sudah dicek langsung, lihat §1.1 dan
`tests/file_mode/README.md` untuk skrip pembuktian.

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
| `AesGcmResult` **tidak** punya `raw_bytes` — hanya `output_text` (hex saat non-UTF8) | `core/symmetric/aes.py:358-370` |
| `_to_bytes` menerima `str` maupun `bytes` | `core/symmetric/aes.py:43-51` |
| `_clean_hex` sudah `strip()` + buang `0x`/`:`, `-`, whitespace internal | `core/symmetric/aes.py:54-78` |

**Hasil uji nyata** (64 byte `os.urandom`, bukan UTF-8):
```
AES-CBC: aes_encrypt(binary) -> raw_bytes=80B ; aes_decrypt(...).raw_bytes == binary  →  True
AES-GCM: aes_gcm_encrypt(binary) -> payload "nonce:cipher:tag" ; is_utf8=False
```

**Kesimpulan:** tujuan fitur (round-trip biner) **tercapai tanpa mengubah core.**
"Core beku" tidak bentrok. Pola yang dipakai:

- **Enkripsi:** teruskan `bytes` langsung ke `aes_encrypt` / `aes_gcm_encrypt`.
- **Dekripsi CBC:** ambil `result.raw_bytes` (byte asli).
- **Dekripsi GCM:** ambil `result.output_text` (hex) → `bytes.fromhex(...)`.
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

**Keputusan tambahan (dari rev-2):**
- **D9** Dekripsi menerima `--format` yang sama dengan enkripsi. **Tidak ada auto-detect.**
- **D10** Dekripsi tanpa `--out` yang menghasilkan non-UTF8 → **galat jelas**, bukan dump byte.

---

## 4. Perubahan yang Direncanakan (per berkas)

> Belum ada kode diubah. Prediksi ini akan dikoreksi saat implementasi.

| Berkas | Perubahan |
|--------|-----------|
| `src/cryptolab/cli/parser.py` | Ganti `required=True` pada `-t` dengan `add_mutually_exclusive_group(required=True)`; tambah `-f`, `-o`, `--force`, `--format` |
| `src/cryptolab/cli/input.py` **(baru)** | `read_input`, `read_file_bytes`, `write_output`, konversi format, `payload` CBC/GCM |
| `src/cryptolab/cli/commands/symmetric.py` | Pakai `cli/input.py`; jalur `--text` tetap identik |
| `src/cryptolab/cli/commands/hashing.py` | `hash --file` → **`hash_file()` langsung** (bukan `read_input`) |
| `src/cryptolab/interactive/handlers/ctx_symmetric.py` | Handler "Mode File" |
| `src/cryptolab/interactive/handlers/ctx_hashing.py` | Handler "Hash File" |
| `src/cryptolab/interactive/tab_menu.py` | Item baru di `CATEGORIES` |
| `tests/test_file_mode.py` **(baru)** | Karakterisasi + round-trip + batas + galat (lihat §6) |

**Tidak disentuh:** `core/symmetric/*.py`, `core/hashing.py`, `core/encoding/*.py`.

---

## 5. Kontrak Perilaku

### 5.0 Parsing argumen (menutup masalah 4)

**Opsi terpilih: `add_mutually_exclusive_group(required=True)`.** Alasan: validasi
tetap di parse-time (exit code 2), "keduanya sekaligus" ditolak argparse tanpa kode
manual, dan **pesan galat "tanpa input" tidak berubah** (argparse sudah memakai
mutually-exclusive group => pesannya tetap "one of the arguments -t/--text -f/--file
is required"). Snapshot lama **tidak perlu diperbarui** untuk kasus ini.

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
4. Ambil plaintext:
   - CBC → `result.raw_bytes` (bytes asli) ✅
   - GCM → `bytes.fromhex(result.output_text)` ⚠️ (tidak ada `raw_bytes`)

> Perbedaan CBC (`raw_bytes`) vs GCM (`output_text` hex) **harus** ditangani
> eksplisit di `cli/input.py`. Tes §6 memverifikasi keduanya.

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
| **F0** | Karakterisasi jalur `--text` + `--format` parsing | `tests/test_file_mode.py` | Belum ada fitur menu |
| **F1** | `cli/input.py` + `--file`/`--out`/`--force`/`--format` untuk **AES-GCM & AES-CBC** | §6.1 | Termasuk round-trip biner |
| **F2** | Perluas ke perintah lain (hashing) + dokumentasi `--format` | — | **Tanpa DES/RC2** (X2) |
| **F3** | `hash --file` → `hash_file` **langsung** | hash berkas besar (>10 MB) lolos | Lihat §6.2 |
| **F4** | Menu interaktif "Mode File" (+ Hash File) | snapshot menu | **PR terpisah** (lihat §12) |
| **F5** | Docs: `docs/USAGE.md` + README | — | — |

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
- [ ] Tanpa `--text`/`--file` → argparse exit 2, **pesan tidak berubah**

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

### 7.2 Dekripsi GCM vs CBC (asimetri API)
`AesResult.raw_bytes` ada; `AesGcmResult` tidak. Ditangani di `cli/input.py` (§5.2).
Ditambah tes khusus yang memastikan kedua jalur menghasilkan byte identik.

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
- Jalur `--text` **tanpa** `--out`: byte keluaran identik (dikunci snapshot lama).
- **Pengecualian disengaja:** F4 (menu interaktif) **menambah item**, sehingga
  snapshot menu berubah. Ini disetujui dan akan memperbarui snapshot terkait.
- Pengecualian kedua: parser `-t` menjadi bagian mutually-exclusive group;
  pesan "tanpa input" tetap sama (§5.0) — **tidak** berubah.

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
| Snapshot jalur teks berubah | Mutually-exclusive group menjaga pesan; snapshot lama + F0 |
| Wiring hash salah kena limit | §6.2 eksplisit: `hash_file` langsung |
| `--out` = `--file` merusak data | Ditolak eksplisit (§5.4) |

---

## 9. Definisi Selesai (DoD)

- [ ] Semua tes §6.1 lolos, plus regresi penuh (`pytest tests/ -q`) hijau
- [ ] `--text` tanpa `--out` byte-identik (snapshot lama hijau)
- [ ] README + `docs/USAGE.md` punya contoh: enkripsi foto → dekripsi → byte identik
- [ ] Tidak ada dependensi baru (hanya cek `pyproject.toml` tidak berubah)
- [ ] `core/` tidak tersentuh (dicek `git diff --stat src/cryptolab/core/`)

---

## 10. Keputusan §3 — Status

Semua disetujui pemilik proyek: **D1, D2, D3′ (default hex), D5 (GCM+CBC), D6, D7, D8**,
**D4** disetujui bersyarat — syarat "batas simetris per-format" dipenuhi §5.3.
Tambahan rev-2: **D9** (tanpa auto-detect), **D10** (dekripsi non-UTF8 tanpa `--out` = galat).

---

## 11. Koreksi Kecil

- Typo rev-1 `memaki` → **`memakai`** (§10).

---

## 12. Catatan Penutup

- **F4 dipisah menjadi PR tersendiri** (nilai terendah, churn terbesar). F0–F3 dapat
  merge lebih dulu tanpa menyentuh snapshot menu.
- `--compress`, chunked, dan format ber-header tetap fase 2 (§7.7, X1/X3).

---

*Akhir spec. Implementasi dimulai dari F0 (karakterisasi, tanpa mengubah perilaku).*
