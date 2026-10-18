# CryptoLab CLI

> **Interactive Cryptography & Encoding Toolkit for Practical Lab & CTF Challenges**  
> Didesain untuk kemudahan mahasiswa dan praktikan keamanan informasi: cukup jalankan `python -m cryptolab` dan ikuti panduan interaktif di terminal.

---

## 1. Pendahuluan & Tujuan Utama

CryptoLab CLI adalah toolkit kriptografi klasik, symmetric block cipher (RC2, DES, dan AES), encoding, dan analisis ciphertext otomatis yang dirancang khusus untuk pembelajaran praktikum keamanan informasi dan kompetisi Capture The Flag (CTF).

### Keunggulan Utama
- **Interaktif Penuh & Ramah Pemula**: Pengguna cukup menjalankan perintah `python -m cryptolab`. Seluruh alur kerja memakai logo ASCII ringkas, navigasi arrow yang konsisten, pertanyaan terarah, dan validasi input tanpa perlu menghafal parameter command yang panjang.
- **Auto Analyze Cerdas**: Otomatis menganalisis data, mendeteksi format encoding (Base64, Hex, Binary), mengurai *nested encoding* hingga 5 tahap, menjalankan Caesar brute-force, serta menawarkan pengujian cipher ber-kunci jika parameter key/IV tersedia.
- **Implementasi DES Lengkap (CBC & ECB)**: Mendukung ciphertext heksadesimal, validasi panjang key/IV (tepat 8 byte), pilihan padding PKCS#7 atau tanpa padding (None), serta fallback heksadesimal jika hasil dekripsi di luar karakter UTF-8.
- **Implementasi RC2 Lengkap (CBC & ECB)**: Mendukung key 5-16 byte, IV 8 byte, padding PKCS#7 atau None, dan `effective-keylen` 40-1024 bit (default 128 bit untuk kompatibilitas vector legacy).
- **Format Hasil yang Rapi & Standar**: Tampilan boks hasil konsisten dengan status keberhasilan, skor keterbacaan, alasan analisis heuristik, serta opsi langsung untuk menyimpan hasil ke file teks.
- **Pencatatan Riwayat yang Aman**: Riwayat operasi dicatat ke file lokal `.cryptolab_history/history.jsonl` tanpa pernah menyimpan kunci rahasia secara default.
- **Kompatibilitas Penuh**: Perintah langsung berbasis argumen CLI (`--help`, `caesar`, `vigenere`, `des`, `base64`, `hex`, `binary`, `auto`, `history`) tetap didukung penuh untuk skrip otomatisasi.

---

## 2. Struktur Menu Utama & Arah UI

Saat Anda menjalankan program, menu utama menampilkan logo `CRYPTOLAB` dan navigasi arrow:

```text
  CRYPTOLAB
  ----------------------------------------
  >> Auto Analyze
     Caesar Cipher
     DES / AES / RC2
     Base64 / Hex / Binary
     Riwayat

  Arrow atas/bawah untuk memilih, Enter untuk membuka, Q untuk keluar.
```

- Gunakan arrow atas/bawah untuk berpindah dan Enter untuk memilih.
- Tekan `b` atau `q` untuk kembali/keluar dari menu.
- Divider pendek digunakan agar output hasil tetap mudah dipindai.

---

## 3. Panduan Instalasi di Windows

### Langkah 1: Clone atau Buka Folder Project
Buka terminal (PowerShell atau Command Prompt) di folder project:
```powershell
cd "d:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit"
```

### Langkah 2: Buat dan Aktifkan Virtual Environment
**Pada PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(Jika muncul kebijakan eksekusi PowerShell `Execution_Policies`, jalankan: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` lalu ulangi aktivasi).*

**Pada Command Prompt (CMD):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

### Langkah 3: Pasang Dependensi
```powershell
pip install -e .
pip install pytest
```

---

## 4. Cara Menjalankan Program

### Cara Utama (Menu Interaktif)
Pengguna cukup mengetik:
```powershell
python -m cryptolab
```
Program langsung membuka antarmuka menu interaktif dalam Bahasa Indonesia yang bersih dan rapi.

### Bantuan Parameter CLI
Perintah bantuan tetap tersedia bagi pengguna yang ingin melihat opsi baris perintah:
```powershell
python -m cryptolab --help
```

---

## 5. Panduan Penggunaan Setiap Fitur

### 1. Auto Analyze (Menu 1)
Fitur analisis otomatis untuk menyelesaikan challenge kriptografi dan encoding:
1. **Deteksi Encoding vs Enkripsi**: Memeriksa apakah input berpotensi berupa Base64, Hexadecimal, Binary 8-bit, atau teks biasa.
   > **Catatan Penting**: Base64, Hex, dan Binary diklasifikasikan secara tegas sebagai **Encoding**, bukan enkripsi kriptografi, karena tidak menggunakan kunci rahasia.
2. **Multi-Stage Decoding**: Mengurai encoding bertingkat (*nested encoding*) secara berurutan hingga batas maksimal 5 langkah untuk mencegah perulangan tak terbatas.
3. **Caesar Brute Force**: Menguji seluruh 26 kemungkinan pergeseran dan menilai kandidat menggunakan scoring engine keterbacaan teks (pola vokal, konsonan alami, dan deteksi flag `FLAG{...}`).
4. **Deteksi Cipher Ber-Kunci & Pertanyaan Interaktif**:
  - Jika ciphertext berukuran kelipatan 16 karakter heksadesimal (blok 8-byte DES/RC2) atau berupa huruf alfabet acak (Vigenere), program menampilkan pertanyaan:
     ```text
     Metode ini mungkin membutuhkan key. Masukkan key jika tersedia, atau tekan Enter untuk melewati:
     ```
   - Jika pengguna memasukkan key:
    - Jika terdeteksi potensi DES/RC2: program menanyakan IV 8 byte untuk mode CBC atau menekan Enter untuk mode ECB. Kedua cipher diuji sebagai kandidat dan hasil dengan skor terbaik ditampilkan.
     - Jika terdeteksi Vigenere: program menguji dekripsi dengan kata kunci tersebut.
   - Jika pengguna menekan Enter (melewati key): program melewati kandidat berkunci dan menampilkan kandidat encoding/Caesar terbaik yang berhasil dianalisis.
5. **Transparansi Hasil**: Hasil disajikan sebagai **kandidat heuristik** yang transparan, lengkap dengan indikator skor, langkah transformasi, dan alasan keterbacaan.

---

### 2. Caesar Cipher (Menu 2)
Mendukung enkripsi, dekripsi, dan brute-force otomatis:
- **Enkripsi / Dekripsi**: Masukkan teks dan nilai pergeseran (*shift* berupa bilangan bulat positif, negatif, atau $> 26$). Huruf besar, huruf kecil, spasi, dan tanda baca dipertahankan secara akurat.
- **Brute Force (26 Kemungkinan)**: Menampilkan tabel seluruh 26 pergeseran atau opsi menampilkan kandidat terbaik dengan estimasi skor frekuensi huruf.

---

### 3. Vigenere Cipher (Menu 3)
Cipher substitusi polialfabetik klasik:
- Masukkan teks dan kata kunci (*keyword* alfabet).
- Huruf kunci tidak sensitif terhadap kapitalisasi (`KEY` sama dengan `key`). Karakter non-alfabet pada teks dipertahankan tanpa memajukan posisi kunci.
- Kunci divalidasi ketat (hanya huruf alfabet A-Z). Pesan kesalahan yang ramah ditampilkan jika kunci berisi angka/simbol.

---

### 4. DES (Data Encryption Standard) (Menu 4)
Implementasi symmetric block cipher DES untuk kebutuhan laboratorium:
- **Pilihan Mode**:
  - `Auto`: Menguji mode CBC dan ECB serta skema padding secara otomatis.
  - `CBC (Cipher Block Chaining)`: Memerlukan key (8 byte) dan IV (8 byte).
  - `ECB (Electronic Codebook)`: Memerlukan key (8 byte) dan **tidak memerlukan IV**.
- **Pilihan Padding**:
  - `PKCS#7`: Skema standar default yang melengkapi blok secara aman.
  - `Tanpa Padding (None)`: Data harus berupa kelipatan tepat 8 byte.
- **Keamanan Output UTF-8**: Jika hasil dekripsi bukan teks UTF-8 yang valid, byte hasil dekripsi akan ditampilkan dalam format Heksadesimal agar data tidak hilang.
- **Peringatan Keamanan**: DES menggunakan kunci 56-bit yang sudah usang dan hanya ditujukan untuk tujuan pembelajaran serta CTF legacy, bukan sistem keamanan modern.

### 5. RC2 (ARC2) (CBC / ECB)
RC2 adalah cipher blok 64-bit legacy. Gunakan fitur ini hanya untuk praktikum, CTF, atau interoperabilitas data lama. Key RC2 menerima 5-16 byte dan IV CBC harus tepat 8 byte. PyCryptodome menyebut implementasinya `ARC2`; CryptoLab menggunakan `effective-keylen=128` bit sebagai default.

Contoh dekripsi vector:

```powershell
python -m cryptolab rc2 decrypt -t "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8" -k "12345678" --iv "qwertyui" -m CBC -p PKCS7
```

Hasilnya adalah `laboratorium_keamanan_3d`.

---

### 6. Base64, Hexadecimal, dan Binary (Menu 5, 6, 7)
Toolkit encoding & decoding data representasi:
- **Tanpa Key/IV**: Langsung memproses data tanpa menanyakan kunci atau IV yang tidak relevan.
- **Dukungan Delimiter Kustom**: Hex dan Binary mendukung pemisah kustom (spasi default, titik dua `:`, garis bawah `_`, atau tanpa spasi `""`).
- **Validasi Integritas**: Memvalidasi kesesuaian karakter, panjang bit genap 8-bit, dan pasangan byte heksadesimal.

---

### 7. Riwayat Analisis Lokal (Menu 8)
- Menyimpan catatan waktu (UTC), operasi yang dijalankan, ringkasan input, dan output ke file `.cryptolab_history/history.jsonl`.
- **Privasi Terjaga**: Kunci rahasia (DES Key/IV, Vigenere Key) **tidak disimpan** ke dalam log riwayat.
- Dilengkapi opsi untuk melihat daftar riwayat terkini dan membersihkan riwayat secara permanen.

---

## 6. Contoh Sesi Terminal Langkah demi Langkah

### Contoh Sesi 1: Menyelesaikan Challenge DES Lab
**Ciphertext Soal**: `5828b071ff8b9fe9f28e2f22bd9c3f21`  
**Key**: `abcdefgh`  
**IV**: `hgfedcba`

```text
====================================================================
  CRYPTOLAB CLI v0.1.0 - TOOLKIT KRIPTOGRAFI & ENCODING
====================================================================
  [1] Auto Analyze
  [2] Caesar Cipher
  [3] Vigenere Cipher
  [4] DES
  [5] Base64
  [6] Hex
  [7] Binary
  [8] Riwayat
  [9] Keluar
====================================================================
  Pilih menu [1-9]: 1

====================================================================
  CRYPTOLAB - AUTO ANALYZE (DETEKSI & ANALISIS CERDAS)
====================================================================
  Masukkan ciphertext atau data yang ingin dianalisis: 5828b071ff8b9fe9f28e2f22bd9c3f21

  [*] Menganalisis format encoding (Base64, Hex, Binary)...
  [*] Menguji pipeline decoding bertingkat...
  [*] Menguji Caesar brute-force (26 kemungkinan shift)...
--------------------------------------------------------------------
  [Indikator] Karakteristik data cocok dengan cipher ber-kunci (DES).
  Metode ini mungkin membutuhkan key. Masukkan key jika tersedia, atau tekan Enter untuk melewati: abcdefgh
  Metode DES CBC membutuhkan IV (8 byte). Masukkan IV jika ada, atau tekan Enter untuk mode ECB saja: hgfedcba

====================================================================
  HASIL ANALISIS CRYPTOLAB
====================================================================
  Metode       : DES (CBC, Padding PKCS7)
  Operasi      : Decrypt
  Status       : Dekripsi DES berhasil (Teks terbaca)
  Kategori     : Kriptografi Simetris
  Skor Teks    : 68.9/100 (Tinggi)
--------------------------------------------------------------------
  INPUT        :
  5828b071ff8b9fe9f28e2f22bd9c3f21
--------------------------------------------------------------------
  OUTPUT       :
  des_enkripsi
--------------------------------------------------------------------
  Alasan       : Karakter terbaca/printable: 100.0%; Proporsi alfabet: 91.7%; Rasio vokal alami (36.4%)
====================================================================

  Opsi Setelah Proses:
  [1] Ulangi proses / Coba data lain
  [2] Simpan hasil ke file
  [0] Kembali ke menu utama
  Pilih opsi [0-2] [0]: 2
  Simpan hasil ke file? (y/n) [n]: y
  Nama file [hasil_cryptolab.txt]: solusi_des.txt
  [OK] Hasil berhasil disimpan ke: D:\...\solusi_des.txt
```

---

### Contoh Sesi 2: Mengurai Encoding Bertingkat (Nested Encoding)
**Input Challenge**: `U0dWc2JHOD0=`

1. Jalankan `python -m cryptolab`
2. Pilih menu `[1] Auto Analyze`
3. Masukkan data: `U0dWc2JHOD0=`
4. Tekan `Enter` untuk melewati pertanyaan key (karena ini adalah murni encoding).
5. **Hasil yang Ditampilkan**:
```text
====================================================================
  HASIL ANALISIS CRYPTOLAB
====================================================================
  Metode       : Base64 -> Base64
  Operasi      : Multi-Stage Decode
  Status       : Dekode bertingkat berhasil
  Kategori     : Encoding
  Skor Teks    : 73.8/100 (Tinggi)
--------------------------------------------------------------------
  INPUT        :
  U0dWc2JHOD0=
--------------------------------------------------------------------
  OUTPUT       :
  Hello
--------------------------------------------------------------------
  Alasan       : Karakter terbaca/printable: 100.0%; Proporsi alfabet: 100.0%; Rasio vokal alami (40.0%)
====================================================================
```

---

## 7. Perintah Langsung CLI (Advanced Users)

Bagi pengguna yang membutuhkan integrasi skrip atau automasi CTF, perintah langsung tetap didukung sepenuhnya:

```powershell
# 1. Caesar Encrypt / Decrypt / Brute-force
python -m cryptolab caesar encrypt -t "Pesan Rahasia" -s 5
python -m cryptolab caesar brute-force -t "KHOOR" --best

# 2. Vigenere Encrypt / Decrypt
python -m cryptolab vigenere encrypt -t "ATTACKATDAWN" -k "LEMON"
python -m cryptolab vigenere decrypt -t "LXFOPVEFRNHR" -k "LEMON"

# 3. DES CBC / ECB / Auto
python -m cryptolab des decrypt -t "5828b071ff8b9fe9f28e2f22bd9c3f21" -k "abcdefgh" --iv "hgfedcba" -m CBC
python -m cryptolab des auto -t "5828b071ff8b9fe9f28e2f22bd9c3f21" -k "abcdefgh" --iv "hgfedcba"

# 4. Base64, Hex, Binary
python -m cryptolab base64 encode -t "CryptoLab"
python -m cryptolab hex encode -t "Lab" -d ":"
python -m cryptolab binary decode -t "01001000 01101001"

# 5. Riwayat Operasi
python -m cryptolab history
python -m cryptolab history --clear
```

---

## 8. Verifikasi & Pengujian (Unit Tests)

Seluruh komponen diuji secara komprehensif menggunakan `pytest`:

```powershell
pytest -v
```

### Hasil Uji Aktual (121 Test Cases — 100% Passed):
- **Test Classical Cipher (`test_caesar.py`, `test_vigenere.py`)**: 15 tests.
- **Test Encoding Codecs (`test_codecs.py`)**: 17 tests.
- **Test Analysis & Heuristics (`test_analysis.py`, `test_phase2_*.py`)**: 40 tests.
- **Test DES Symmetric Cipher (`test_des.py`)**: 13 tests (CBC, ECB, PKCS7, None, validasi key 8-byte, IV CBC, fallback hex non-UTF8, auto analyze, CLI).
- **Test Interactive Menus & Flows (`test_interactive.py`)**: 19 tests (menu exit, retry invalid inputs, Caesar, Vigenere, DES CBC/ECB/Auto, Base64/Hex/Binary, riwayat, simpan ke file, navigasi kembali).
- **Test CLI Compatibility (`test_cli.py`, `test_phase2_cli.py`)**: 17 tests.
