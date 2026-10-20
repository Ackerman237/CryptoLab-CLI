Kamu mengerjakan upgrade pada tool CLI Keamanan Informasi di proyek ini.

Langkah pertama: baca file `upgrade-spec.md` (letakkan di root proyek) dan telusuri seluruh kode yang sudah ada sebelum mengubah apa pun.

## Aturan

1. Jangan ubah logika enkripsi, dekripsi, hash, atau encoding yang sudah ada. Output lama harus identik.
2. Jangan ubah tampilan yang sudah ada. UI baru hanya tambahan, dan menu lama tetap tersedia sebagai fallback.
3. Hanya tambah fitur dan variasi UI: pemisah Binary/Hex, menu tab kategori, dan mode baru.
4. Kode di `upgrade-spec.md` hanya ilustrasi (Python + Rich + readchar). Bahasa, library, nama fungsi, dan struktur proyek ini bisa berbeda. Sesuaikan dengan kode yang sudah ada, dan pertahankan perilakunya, bukan snippetnya. Jangan tambah dependensi baru kalau library yang sudah dipakai cukup.
5. Kalau spec bertentangan dengan kode yang ada, ikuti kode yang ada, lalu laporkan perbedaannya.

## Alur

Kerjakan berurutan sesuai tahap di spec (Tahap 0 sampai 3). Di akhir setiap tahap:

- jalankan tes regresi,
- ringkas file yang diubah dan alasannya,
- berhenti dan tunggu konfirmasi sebelum lanjut ke tahap berikutnya.

Mulai dari Tahap 0 (tes patokan dari output tool saat ini).
