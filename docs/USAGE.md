# Panduan Penggunaan CryptoLab CLI

Dokumen ini berisi rincian fitur utama, alur interaktif, dan contoh penggunaan untuk toolkit CryptoLab.

## 1. Navigasi UI

Saat menjalankan `cryptolab`, Anda akan masuk ke menu utama dengan logo terminal dan daftar kategori. Navigasi utamanya:

- `↑` / `↓`: geser pilihan
- `Enter`: masuk ke submenu atau menjalankan operasi
- `Esc` / `b`: kembali ke menu sebelumnya
- `?`: bantuan aplikasi
- `q`: keluar

Menu utama yang umum ditemui:

- Auto Analyze
- Classical Ciphers
- Symmetric Ciphers
- Hashing & MAC
- Asymmetric Crypto
- Encoding Tools
- History

## 2. Auto Analyze

Fitur ini dirancang untuk membantu memecahkan challenge dengan cara yang cepat dan transparan. Ia dapat:

- mendeteksi format input seperti Base64, Hex, Binary, atau plaintext biasa;
- men-decoding nested encoding berulang hingga 5 tahap;
- mencoba Caesar brute force untuk semua kemungkinan pergeseran;
- membandingkan kandidat hasil dari cipher ber-kunci bila key atau IV tersedia.

Keluaran Auto Analyze biasanya menampilkan skor heuristik, langkah transformasi, dan alasan mengapa kandidat tertentu tampak relevan.

## 3. Classical Ciphers

### Caesar

- mendukung enkripsi, dekripsi, dan brute-force;
- bisa menerima shift positif, negatif, dan angka lebih dari 26;
- mempertahankan ruang dan karakter non-alfabet.

### Vigenere

- menggunakan keyword untuk substitusi polialfabetik;
- huruf kunci bersifat case-insensitive;
- karakter non-alfabet tidak memajukan indeks kunci.

### Playfair

- membangun matriks 5x5 berdasarkan keyword;
- membersihkan duplikat dan konversi J ke I;
- memproses plaintext dalam bentuk digram.

### Hill

- mendukung matriks 2x2 atau 3x3;
- validasi key harus invertible modulo 26.

### Affine

- formula: `E(x) = (a*x + b) mod 26`;
- parameter `a` harus coprime dengan 26.

### Rail Fence

- model transposisi zigzag dengan jumlah rail yang dipilih;
- mendukung enkripsi, dekripsi, serta brute-force atas jumlah rail.

## 4. Symmetric Ciphers

### DES

- mendukung mode CBC dan ECB;
- validasi panjang key/IV sesuai spesifikasi;
- pilihan padding PKCS#7 atau None.

### RC2 (legacy)

- tersedia untuk kebutuhan lab dan kompatibilitas legacy;
- menampilkan peringatan karena cipher ini sudah usang.

### AES

- mendukung CBC, ECB, dan GCM;
- validasi key 16/24/32 byte dan IV sesuai mode;
- cocok untuk penggunaan modern dibanding DES dan RC2.

## 5. Hashing & MAC

CryptoLab mendukung:

- MD5, SHA1, SHA256, SHA512
- HMAC
- PBKDF2
- Bcrypt (opsional)

Fitur compute dan verify tersedia untuk operasi yang umum di lab kriptografi.

Catatan keamanan: MD5, SHA1, DES, RC2, dan ECB mode akan menampilkan peringatan karena sudah dianggap lemah untuk penggunaan produksi.

## 6. Asymmetric Crypto

### RSA

- key generation
- encrypt/decrypt
- sign/verify
- mode: OAEP, PKCS#1 v1.5, dan PSS

### Diffie-Hellman

- menjalankan pertukaran kunci dengan parameter yang valid;
- cocok untuk mempelajari konsep key exchange.

## 7. Encoding Tools

Tersedia formatter dasar untuk:

- Base64
- Hexadecimal
- Binary

Fitur ini berguna untuk keperluan analisis data dan transformasi struktur ciphertext/teks sebelum atau sesudah operasi kriptografi.

## 8. Riwayat

Semua operasi yang dijalankan dapat disimpan ke log lokal tanpa menuliskan informasi sensitif seperti kunci rahasia. Panduan keamanan tetap menganjurkan menutup atau merahasiakan key, IV, dan secret material saat bekerja di lingkungan kolaboratif.

## 9. Contoh CLI cepat

```bash
cryptolab --help
cryptolab caesar brute-force -t "KHOOR" --best
cryptolab hash compute -t "data" --algo SHA256
cryptolab rsa keygen --bits 2048 --out-dir ./keys
```

## 10. Pengujian

```bash
pytest -v
```

## 11. Catatan keamanan

- Gunakan AES atau mode modern bila memungkinkan.
- Hindari penggunaan MD5/SHA1/DES/RC2 untuk data sensitif.
- Selalu simpan kunci dan salt dengan cara aman, bukan di log atau output terminal yang tidak perlu.