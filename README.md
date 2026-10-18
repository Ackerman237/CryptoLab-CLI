# CryptoLab CLI

> **Interactive Cryptography & Encoding Toolkit for Practical Lab & CTF Challenges**  
> Didesain untuk kemudahan mahasiswa dan praktikan keamanan informasi: cukup jalankan `cryptolab` dan ikuti panduan interaktif di terminal.

---

## 1. Pendahuluan & Tujuan Utama

CryptoLab CLI adalah toolkit kriptografi klasik, symmetric block cipher (RC2, DES, dan AES), encoding, hashing, asymmetric crypto (RSA, DH), dan analisis ciphertext otomatis yang dirancang khusus untuk pembelajaran praktikum keamanan informasi dan kompetisi Capture The Flag (CTF).

### Keunggulan Utama
- **Interaktif Penuh & Ramah Pemula**: Pengguna cukup menjalankan perintah `cryptolab`. Seluruh alur kerja memakai logo ASCII ringkas, navigasi arrow yang konsisten, pertanyaan terarah, dan validasi input tanpa perlu menghafal parameter command yang panjang.
- **Auto Analyze Cerdas**: Otomatis menganalisis data, mendeteksi format encoding (Base64, Hex, Binary), mengurai *nested encoding* hingga 5 tahap, menjalankan Caesar brute-force, serta menawarkan pengujian cipher ber-kunci jika parameter key/IV tersedia.
- **Implementasi DES Lengkap (CBC & ECB)**: Mendukung ciphertext heksadesimal, validasi panjang key/IV (tepat 8 byte), pilihan padding PKCS#7 atau tanpa padding (None), serta fallback heksadesimal jika hasil dekripsi di luar karakter UTF-8.
- **Implementasi RC2 Lengkap (CBC & ECB)**: Mendukung key 5-16 byte, IV 8 byte, padding PKCS#7 atau None, dan `effective-keylen` 40-1024 bit (default 128 bit untuk kompatibilitas vector legacy).
- **Implementasi AES Lengkap (CBC & ECB)**: Mendukung key 16/24/32 byte, IV 16 byte, padding PKCS#7 atau None, mode CBC/ECB/GCM.
- **Hashing & MAC Modern**: MD5, SHA1, SHA256, SHA512, HMAC (semua algoritma), PBKDF2 (SHA256/SHA512), Bcrypt (opsional). Mendukung compute & verify.
- **Asymmetric Cryptography**: RSA (keygen, encrypt, decrypt, sign, verify - PKCS#1 v1.5 & PSS) dan Diffie-Hellman Key Exchange.
- **Classical Ciphers**: Caesar, Vigenere, Playfair, Hill (2x2/3x3), Affine, Rail Fence - lengkap dengan brute-force & auto-analyze.
- **Format Hasil yang Rapi & Standar**: Tampilan boks hasil konsisten dengan status keberhasilan, skor keterbacaan, alasan analisis heuristik, serta opsi langsung untuk menyimpan hasil ke file teks.
- **Pencatatan Riwayat yang Aman**: Riwayat operasi dicatat ke file lokal `.cryptolab_history/history.jsonl` tanpa pernah menyimpan kunci rahasia secara default.
- **Kompatibilitas Penuh**: Perintah langsung berbasis argumen CLI (`--help`, `caesar`, `vigenere`, `des`, `aes`, `rc2`, `hash`, `rsa`, `dh`, `base64`, `hex`, `binary`, `auto`, `history`) tetap didukung penuh untuk skrip otomatisasi.

---

## 2. Struktur Menu Utama & Arah UI

Saat Anda menjalankan program, menu utama menampilkan logo `CRYPTOLAB` dan navigasi arrow:

```text
  CRYPTOLAB
  ----------------------------------------
  >> Auto Analyze
     Classical Ciphers
     Symmetric Ciphers
     Hashing & MAC
     Asymmetric Crypto
     Encoding Tools
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
cryptolab
```
Program langsung membuka antarmuka menu interaktif dalam Bahasa Indonesia yang bersih dan rapi.

### Bantuan Parameter CLI
Perintah bantuan tetap tersedia bagi pengguna yang ingin melihat opsi baris perintah:
```powershell
cryptolab --help
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

### 2. Classical Ciphers (Menu 2)

#### Caesar Cipher
Mendukung enkripsi, dekripsi, dan brute-force otomatis:
- **Enkripsi / Dekripsi**: Masukkan teks dan nilai pergeseran (*shift* berupa bilangan bulat positif, negatif, atau $> 26$). Huruf besar, huruf kecil, spasi, dan tanda baca dipertahankan secara akurat.
- **Brute Force (26 Kemungkinan)**: Menampilkan tabel seluruh 26 pergeseran atau opsi menampilkan kandidat terbaik dengan estimasi skor frekuensi huruf.

#### Vigenere Cipher
Cipher substitusi polialfabetik klasik:
- Masukkan teks dan kata kunci (*keyword* alfabet).
- Huruf kunci tidak sensitif terhadap kapitalisasi (`KEY` sama dengan `key`). Karakter non-alfabet pada teks dipertahankan tanpa memajukan posisi kunci.
- Kunci divalidasi ketat (hanya huruf alfabet A-Z). Pesan kesalahan yang ramah ditampilkan jika kunci berisi angka/simbol.

#### Playfair Cipher
Cipher substitusi digram 5x5 matrix:
- Keyword dibersihkan (hapus duplikat, J→I), lalu mengisi matrix 5x5.
- Plaintext dipecah menjadi digram, dengan padding 'X' jika perlu.
- Aturan: same row→right, same col→down, rectangle→swap columns.

#### Hill Cipher (2x2 / 3x3)
Cipher matriks linear algebra:
- Key berupa matriks 2x2 atau 3x3 (4 atau 9 integer).
- Validasi determinan harus coprime dengan 26 (invertible modulo 26).
- Operasi matriks modulo 26 pada blok plaintext.

#### Affine Cipher
Cipher substitusi afine: `E(x) = (a*x + b) mod 26`
- Parameter `a` harus coprime dengan 26 (1,3,5,7,9,11,15,17,19,21,23,25).
- Mendukung enkripsi, dekripsi, dan brute-force (312 kunci valid).

#### Rail Fence Cipher (Zigzag)
Cipher transposisi zigzag:
- Jumlah rail minimum 2.
- Mendukung enkripsi, dekripsi, dan brute-force (mencoba semua rail 2..max).

---

### 3. Symmetric Ciphers (Menu 3)

#### DES (Data Encryption Standard)
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

#### RC2 (ARC2)
RC2 adalah cipher blok 64-bit legacy. Gunakan fitur ini hanya untuk praktikum, CTF, atau interoperabilitas data lama. Key RC2 menerima 5-16 byte dan IV CBC harus tepat 8 byte. PyCryptodome menyebut implementasinya `ARC2`; CryptoLab menggunakan `effective-keylen=128` bit sebagai default.

Contoh dekripsi vector:
```powershell
cryptolab rc2 decrypt -t "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8" -k "12345678" --iv "qwertyui" -m CBC -p PKCS7
```
Hasilnya adalah `laboratorium_keamanan_3d`.

#### AES (Advanced Encryption Standard)
Modern symmetric block cipher 128-bit block:
- **Key Size**: 128-bit (16 byte), 192-bit (24 byte), 256-bit (32 byte)
- **Mode**: CBC, ECB, GCM (authenticated encryption)
- **Padding**: PKCS#7 atau None
- **GCM**: Menghasilkan authentication tag untuk verifikasi integritas

---

### 4. Hashing & MAC (Menu 4)

#### Hash Computation (MD5, SHA1, SHA256, SHA512)
- Input: pesan (string) dan pilihan encoding output (Hex/Base64).
- Output: hash value dalam format yang dipilih.

#### Hash File
- Hash file langsung dari path file.
- Mendukung algoritma MD5, SHA1, SHA256, SHA512.
- Berguna untuk verifikasi integritas file.

#### Hash Verification
- Verifikasi apakah hash pesan cocok dengan expected hash.
- Input: pesan, expected hash, algoritma, encoding.
- Output: VALID/INVALID dengan konstanta-time comparison.

#### HMAC (Hash-based Message Authentication Code)
- HMAC-MD5, HMAC-SHA1, HMAC-SHA256, HMAC-SHA512.
- Operasi: Compute (pesan + kunci → HMAC) dan Verify (pesan + kunci + expected HMAC → valid/invalid).
- Konstanta-time verification untuk keamanan timing attack.

#### PBKDF2 (Password-Based Key Derivation Function 2)
- PBKDF2-SHA256 dan PBKDF2-SHA512.
- Parameter: password, salt (opsional, auto-generate), iterations (default 600,000), dklen (default 32 byte).
- Operasi: Hash password dan Verify password.

#### Bcrypt (Opsional - butuh `pip install bcrypt`)
- Hash password dengan cost factor 4-31 (default 12).
- Built-in salt generation dan verification.

#### Random Bytes Generator
- Generate cryptographically secure random bytes.
- Panjang 1-1024 byte, output Hex atau Base64.

---

### 5. Asymmetric Crypto (Menu 5)

#### RSA
- **Key Generation**: 2048, 3072, 4096 bit. Output PEM format (PKCS#1/PKCS#8).
- **Encrypt/Decrypt**: RSA-OAEP (SHA256) dengan public/private key.
- **Sign/Verify**: PKCS#1 v1.5 dan PSS (SHA256).
- Input key via file path atau paste PEM langsung.

#### Diffie-Hellman Key Exchange
- Parameter group: RFC 3526 Group 14 (2048-bit), Group 15 (3072-bit), Group 16 (4096-bit), atau custom.
- Operasi: Generate key pair, Derive shared secret dari peer public key.
- Output shared secret dalam Hex/Base64.

---

### 6. Encoding Tools (Menu 6)

#### Base64, Hexadecimal, Binary
Toolkit encoding & decoding data representasi:
- **Tanpa Key/IV**: Langsung memproses data tanpa menanyakan kunci atau IV yang tidak relevan.
- **Dukungan Delimiter Kustom**: Hex dan Binary mendukung pemisah kustom (spasi default, titik dua `:`, garis bawah `_`, atau tanpa spasi `""`).
- **Validasi Integritas**: Memvalidasi kesesuaian karakter, panjang bit genap 8-bit, dan pasangan byte heksadesimal.

---

### 7. Riwayat Analisis Lokal (Menu 7)
- Menyimpan catatan waktu (UTC), operasi yang dijalankan, ringkasan input, dan output ke file `.cryptolab_history/history.jsonl`.
- **Privasi Terjaga**: Kunci rahasia (DES Key/IV, Vigenere Key, RSA private key, HMAC key, dll) **tidak disimpan** ke dalam log riwayat.
- Dilengkapi opsi untuk melihat daftar riwayat terkini dan membersihkan riwayat secara permanen.

---

## 6. Contoh Sesi Terminal Langkah demi Langkah

### Contoh Sesi 1: Menyelesaikan Challenge DES Lab
**Ciphertext Soal**: `5828b071ff8b9fe9f28e2f22bd9c3f21`  
**Key**: `abcdefgh`  
**IV**: `hgfedcba`

```text
====================================================================
  CRYPTOLAB CLI v1.0.0 - TOOLKIT KRIPTOGRAFI & ENCODING
====================================================================
  [1] Auto Analyze
  [2] Classical Ciphers
  [3] Symmetric Ciphers
  [4] Hashing & MAC
  [5] Asymmetric Crypto
  [6] Encoding Tools
  [7] Riwayat
  [8] Keluar
====================================================================
  Pilih menu [1-8]: 1

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

1. Jalankan `cryptolab`
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

### Contoh Sesi 3: HMAC Verification
```powershell
cryptolab hmac verify --message "Pesan rahasia" --key "kunci123" --expected "a1b2c3..." --algo SHA256 --encoding hex
```

---

### Contoh Sesi 4: RSA Encrypt/Decrypt
```powershell
# Generate key pair
cryptolab rsa keygen --bits 2048 --out-dir ./keys

# Encrypt
cryptolab rsa encrypt --pubkey ./keys/public.pem --message "Rahasia" --out cipher.bin

# Decrypt
cryptolab rsa decrypt --privkey ./keys/private.pem --in cipher.bin
```

---

### Contoh Sesi 5: Diffie-Hellman Key Exchange
```powershell
# Alice generates key pair
cryptolab dh exchange --group 14 --out-dir ./alice

# Bob generates key pair
cryptolab dh exchange --group 14 --out-dir ./bob

# Alice derives shared secret using Bob's public key
cryptolab dh derive --privkey ./alice/private.pem --peer-pub ./bob/public.pem

# Bob derives shared secret using Alice's public key
cryptolab dh derive --privkey ./bob/private.pem --peer-pub ./alice/public.pem
# Both get the same shared secret!
```

---

## 7. Perintah Langsung CLI (Advanced Users)

Bagi pengguna yang membutuhkan integrasi skrip atau automasi CTF, perintah langsung tetap didukung sepenuhnya:

```powershell
# 1. Caesar Encrypt / Decrypt / Brute-force
cryptolab caesar encrypt -t "Pesan Rahasia" -s 5
cryptolab caesar brute-force -t "KHOOR" --best

# 2. Vigenere Encrypt / Decrypt
cryptolab vigenere encrypt -t "ATTACKATDAWN" -k "LEMON"
cryptolab vigenere decrypt -t "LXFOPVEFRNHR" -k "LEMON"

# 3. Classical Ciphers
cryptolab playfair encrypt -t "HELLO WORLD" -k "KEYWORD"
cryptolab hill encrypt -t "ACT" -k "2 3 5 7" --size 2
cryptolab affine encrypt -t "HELLO" -a 5 -b 8
cryptolab railfence encrypt -t "HELLO WORLD" -r 3

# 4. DES CBC / ECB / Auto
cryptolab des decrypt -t "5828b071ff8b9fe9f28e2f22bd9c3f21" -k "abcdefgh" --iv "hgfedcba" -m CBC
cryptolab des auto -t "5828b071ff8b9fe9f28e2f22bd9c3f21" -k "abcdefgh" --iv "hgfedcba"

# 5. RC2
cryptolab rc2 decrypt -t "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8" -k "12345678" --iv "qwertyui" -m CBC -p PKCS7

# 6. AES
cryptolab aes encrypt -t "Secret Message" -k "0123456789abcdef0123456789abcdef" --iv "abcdefghijklmnop" -m CBC

# 7. Hashing
cryptolab hash compute -t "data" --algo SHA256 --encoding hex
cryptolab hash verify -t "data" --expected "..." --algo SHA256
cryptolab hmac compute -t "msg" -k "key" --algo SHA256
cryptolab hmac verify -t "msg" -k "key" --expected "..." --algo SHA256
cryptolab pbkdf2 hash --password "pwd" --salt "salt" --algo SHA256
cryptolab bcrypt hash --password "pwd" --rounds 12

# 8. RSA
cryptolab rsa keygen --bits 2048 --out-dir ./keys
cryptolab rsa encrypt --pubkey ./keys/public.pem -t "msg"
cryptolab rsa sign --privkey ./keys/private.pem -t "msg" --scheme PSS

# 9. Diffie-Hellman
cryptolab dh exchange --group 14 --out-dir ./keys
cryptolab dh derive --privkey ./keys/private.pem --peer-pub ./peer/public.pem

# 10. Encoding
cryptolab base64 encode -t "CryptoLab"
cryptolab hex encode -t "Lab" -d ":"
cryptolab binary decode -t "01001000 01101001"

# 11. History
cryptolab history
cryptolab history --clear
```

---

## 8. Verifikasi & Pengujian (Unit Tests)

Seluruh komponen diuji secara komprehensif menggunakan `pytest`:

```powershell
pytest -v
```

### Hasil Uji Aktual (231 Test Cases - 100% Passed, 4 Skipped for bcrypt):
- **Test Classical Cipher** (`test_caesar.py`, `test_vigenere.py`, `test_playfair.py`, `test_hill.py`, `test_affine.py`, `test_railfence.py`): 45+ tests.
- **Test Encoding Codecs** (`test_codecs.py`): 17 tests.
- **Test Analysis & Heuristics** (`test_analysis.py`, `test_phase2_*.py`): 40 tests.
- **Test DES Symmetric Cipher** (`test_des.py`): 13 tests (CBC, ECB, PKCS7, None, validasi key 8-byte, IV CBC, fallback hex non-UTF8, auto analyze, CLI).
- **Test AES Symmetric Cipher** (`test_aes.py`): 15+ tests.
- **Test RC2 Symmetric Cipher** (`test_rc2.py`): 12+ tests.
- **Test Hashing** (`test_hashing.py`): 35+ tests (MD5, SHA, HMAC, PBKDF2, Bcrypt, Random Bytes).
- **Test Asymmetric Crypto** (`test_rsa.py`, `test_dh.py`): 25+ tests.
- **Test Interactive Menus & Flows** (`test_interactive.py`): 19 tests (menu exit, retry invalid inputs, Caesar, Vigenere, DES CBC/ECB/Auto, Base64/Hex/Binary, riwayat, simpan ke file, navigasi kembali).
- **Test CLI Compatibility** (`test_cli.py`, `test_phase2_cli.py`): 17 tests.