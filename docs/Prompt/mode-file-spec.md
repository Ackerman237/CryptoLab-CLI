# Spec: Mode File (Enkripsi/Dekripsi/Hash Berkas)

**Status:** DRAFT — menunggu keputusan desain (lihat §8)
**Tanggal:** 2026-10-20
**Target:** `main` pasca-PR #3 (`abe1e4f`)
**Prinsip:** 1 step = 1 commit · scope = spec ini saja · no behavior change untuk jalur teks · no new deps (stdlib only)

---

## 1. Latar Belakang

Saat ini CryptoLab hanya bisa memproses **teks** yang diketik/ditempel di terminal.
Opsi `-t/--text` bersifat `required=True` di hampir semua sub-perintah
(`src/cryptolab/cli/parser.py`), dan menu interaktif selalu meminta input teks.

Akibatnya, berkas nyata (foto, dokumen, arsip) **tidak bisa** diproses:
- menempel isi berkas 5 MB sebagai teks tidak praktis,
- ciphertext berisi byte non-UTF8 tidak bisa dipindahkan lewat clipboard dengan aman,
- tidak ada cara menulis hasil ke berkas dari CLI (kecuali jalur kunci RSA).

**Yang sudah ada (jangan dibuat ulang):**
- `hash_file(filepath, algorithm="SHA256")` — `src/cryptolab/core/hashing.py:169`
  sudah membaca berkas per chunk 8 KB dan mengembalikan `HashResult`.
- RSA keygen sudah menulis kunci ke berkas (`src/cryptolab/cli/commands/asymmetric.py`).

**Yang belum ada:** enkripsi/dekripsi berkas, opsi `--file`, dan opsi `--out`.

---

## 2. Ruang Lingkup

### Termasuk (in-scope)

| No | Item |
|----|------|
| S1 | Opsi CLI `-f/--file PATH` sebagai **alternatif** `-t/--text` |
| S2 | Opsi CLI `-o/--out PATH` untuk menulis hasil ke berkas |
| S3 | Mode **read-all** untuk berkas kecil (baca seluruh isi → enkripsi → tulis) |
| S4 | Dukungan algoritma: **AES-CBC** dan **AES-GCM** (AEAD) pada tahap pertama |
| S5 | Menu interaktif: item "Mode File" pada tab yang relevan |
| S6 | Pesan galat berkas yang ramah (berkas tidak ada, bukan berkas, tidak bisa ditulis, terlalu besar) |
| S7 | Perintah `hash --file` (karena `hash_file` sudah tersedia — hanya wiring + teks UI) |

### Tidak termasuk (out-of-scope, catat sebagai fitur lanjutan)

| No | Item | Alasan |
|----|------|--------|
| X1 | Mode **chunked/streaming** untuk berkas besar | butuh format berkas & penanganan padding antar-blok; fase 2 |
| X2 | Mode file untuk DES, RC2, RSA, klasik | DES/RC2 tidak AEAD & kunci pendek; RSA lambat untuk berkas besar |
| X3 | Format berkas ber-header (magic bytes, metadata algo/IV) | keputusan desain §8; fase 2 bersama chunked |
| X4 | Integritas otomatis (hash menyertai ciphertext) | AES-GCM sudah memberi tag; untuk AES-CBC ditunda |
| X5 | Kompresi sebelum enkripsi | di luar tujuan tool |
| X6 | Progres bar untuk berkas besar | baru berguna bersama chunked |

---

## 3. Keputusan Desain (default yang diusulkan)

Keputusan ini **harus disetujui** sebelum implementasi. Semua punya default
yang saya rekomendasikan (ditandai **[DEFAULT]**); yang lain disimpan sebagai
alternatif agar mudah dibalik.

| Kode | Pertanyaan | **[DEFAULT]** usulan | Alternatif |
|------|-----------|----------------------|-----------|
| D1 | Sumber input | `--file PATH` (mutually exclusive dengan `--text`) | `--in PATH`; atau `--file` menggantikan `--text` |
| D2 | Tujuan output | `--out PATH`; tanpa `--out` → stdout | selalu tulis ke berkas `<nama>.enc` |
| D3 | Format output enkripsi | **teks hex** (aman di clipboard/log) | biner mentah (lebih kecil, tidak aman di clipboard) |
| D4 | Batas ukuran read-all | **10 MB**, dengan galat jelas bila lewat | 50 MB; tanpa batas |
| D5 | Algoritma fase 1 | **AES-GCM** (AEAD, tag 128-bit) + **AES-CBC** | AES saja; semua simetris |
| D6 | Payload AES-GCM di berkas | tulis `nonce_hex:ciphertext_hex:tag_hex` (sudah jadi format `aes_gcm_encrypt`) | biner `nonce ‖ ct ‖ tag` |
| D7 | Berkas keluaran bila ada | **menolak menimpa** (galat), perlu `--force` untuk menimpa | menimpa langsung |
| D8 | Menu interaktif | item **"Mode File"** di tab Simetris & Hash | tidak ada UI interaktif |

**Rekomendasi tambahan (di luar pertanyaan):**
- Jalur teks lama **tidak boleh berubah sedikit pun**. `--file` sepenuhnya jalur baru.
- Format hex untuk output (D3 default) menjaga rantai round-trip: `--file` → hex →
  `--text` harus bisa didekripsi.
- Bila `--file` dan `--text` dipakai bersama → galat `InvalidInputError`.

---

## 4. Perubahan yang Direncanakan (per berkas)

> Belum ada kode diubah saat spec ditulis. Daftar ini prediksi; akan dikoreksi saat implementasi.

| Berkas | Perubahan |
|--------|-----------|
| `src/cryptolab/cli/parser.py` | `-t/--text` → tidak lagi `required=True`; tambah `-f/--file`, `-o/--out`, `--force` (per sub-perintah yang relevan) |
| `src/cryptolab/cli/input.py` **(baru)** | `read_input(args) -> bytes` & `write_output(path, text, force)` — satu pintu I/O berkas |
| `src/cryptolab/cli/commands/symmetric.py` | Pakai `read_input`/`write_output`; jalur `--text` tetap identik |
| `src/cryptolab/cli/commands/hashing.py` | Wiring `hash --file PATH` → `hash_file()` yang sudah ada |
| `src/cryptolab/interactive/handlers/ctx_symmetric.py` | Handler "Mode File" (AES-CBC/GCM) untuk menu |
| `src/cryptolab/interactive/handlers/ctx_hashing.py` | Handler "Hash File" |
| `src/cryptolab/interactive/tab_menu.py` | Daftarkan item baru di `CATEGORIES` |
| `tests/test_file_mode.py` **(baru)** | Karakterisasi + round-trip + batas ukuran + pesan galat |

**Tidak disentuh:** `core/symmetric/*.py`, `core/hashing.py`, `core/encoding/*.py`
(logika kripto beku). Mode file hanya **memanggil** API yang sudah ada.

---

## 5. Kontrak Perilaku

### 5.1 Membaca input

```
read_input(args) -> bytes
  - args.file  -> open(file, "rb") ; sisa ditangani pemanggil
  - args.text  -> args.text.encode("utf-8")
  - keduanya  -> InvalidInputError("Pilih salah satu: --text atau --file")
  - tidak ada -> InvalidInputError("Butuh --text atau --file")
```

Galat berkas dipetakan ke pesan ramah:
| Kondisi | Pesan |
|---|---|
| Tidak ada | `Berkas tidak ditemukan: <path>` |
| Bukan berkas (mis. direktori) | `<path> bukan berkas biasa.` |
| Ukuran > batas read-all | `Berkas <N> MB melebihi batas mode read-all (<10> MB). Mode streaming belum tersedia.` |
| Izin baca ditolak | `Tidak bisa membaca berkas: <alasan singkat>` |

### 5.2 Menulis output

```
write_output(path, text, force=False)
  - path None     -> print ke stdout (perilaku lama)
  - path ada + tidak force -> InvalidInputError("<path> sudah ada. Pakai --force untuk menimpa.")
  - sukses        -> tulis teks apa adanya (UTF-8), tanpa tambahan pesan ke stdout
```
Bila `--out` dipakai, **kotak hasil** tetap dicetak ke stdout tetapi `output_text`
diganti ringkasan (mis. `Ditulis ke <path> (<N> byte)`), supaya keluaran tidak
menggandakan seluruh ciphertext.

### 5.3 Jalur teks (regresi)

Untuk `--text` tanpa `--out`, keluaran byte harus **identik** dengan sebelum
perubahan. Dikunci oleh `tests/test_cli_snapshot.py` yang sudah ada.

---

## 6. Rencana Tahapan (1 step = 1 commit)

| Step | Isi | Tes | Commit |
|------|-----|-----|--------|
| **F0** | Karakterisasi: kunci perilaku `--text` saat ini untuk perintah simetris + hash | `tests/test_file_mode.py` (bagian karakterisasi) | `test(file): karakterisasi jalur teks` |
| **F1** | `cli/input.py` + `--file`/`--out`/`--force` pada **satu** perintah (AES-GCM) | round-trip teks↔berkas, galat berkas, `--force` | `feat(cli): opsi --file/--out (AES-GCM)` |
| **F2** | Perluas ke AES-CBC, lalu DES/RC2 **hanya bila** §8 → D5 disetujui | round-trip per algoritma | `feat(cli): --file untuk AES-CBC` |
| **F3** | `hash --file` (wiring `hash_file`) | hash berkas == hash teks setara | `feat(cli): hash --file` |
| **F4** | Menu interaktif "Mode File" (tab Simetris + Hash) | tes snapshot menu & alur | `feat(interactive): mode file` |
| **F5** | Dokumen: `docs/USAGE.md` + README (contoh `--file`) | — | `docs: mode file` |

Setiap step: `pytest tests/ -q` → ringkas → tunggu konfirmasi → commit.

---

## 7. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| `--text` tidak lagi `required` → perintah lain kehilangan validasi | Validasi `required` dipindah ke runtime (`read_input`) + tes negatif untuk tiap sub-perintah |
| Ciphertext biner dari berkas masuk ke terminal/log | Default output **hex** (D3); biner hanya bila diminta eksplisit |
| Berkas besar menghabiskan memori | Batas 10 MB + galat jelas (D4); chunked masuk fase 2 |
| Menimpa berkas pengguna tanpa sengaja | Tolak bila ada + `--force` (D7) |
| Jalur teks berubah tanpa sadar | Snapshot lama + bagian karakterisasi F0 |

---

## 8. Keputusan yang Dibutuhkan (persetujuan)

Mohon jawab yang sesuai (nomor kode memaki §3). Saya sarankan semua **[DEFAULT]**.

- [ ] **D1** Sumber input: `--file` (default) / lain
- [ ] **D2** Tujuan output: `--out` atau stdout (default) / selalu ke berkas
- [ ] **D3** Format output: hex (default) / biner mentah
- [ ] **D4** Batas read-all: 10 MB (default) / lain
- [ ] **D5** Algoritma fase 1: AES-GCM + AES-CBC (default) / AES saja / semua
- [ ] **D6** Payload GCM: string `nonce:cipher:tag` (default) / biner
- [ ] **D7** Berkas output ada: tolak + `--force` (default) / timpa langsung
- [ ] **D8** Menu interaktif "Mode File": ya (default) / tidak

Setelah disetujui, spec ini dipindah statusnya menjadi **APPROVED** dan
implementasi dimulai dari **F0**.

---

*Draf ini hanya dokumen — belum ada kode yang diubah.*
