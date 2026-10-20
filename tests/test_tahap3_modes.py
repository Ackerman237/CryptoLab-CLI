"""Tahap 3 - mode baru (upgrade-spec.md).

Mode 1 SHA-3 & Mode 2 SHA-512:
- Core SHA3-256/SHA3-512 ditambahkan ke hash_compute/hash_file (additive).
- Handler teks/file dengan pembanding SHA-256; item menu tab terwire.

Mode 3 HMAC-SHA-256 (buat/verifikasi MAC), Mode 4 AES-GCM (nonce acak 12
byte + tag ditolak bila tidak valid), Mode 5 Digital Signature (memakai
RSA-PSS di core), Mode 6 Argon2id/bcrypt (belum tersedia - butuh dep baru),
Mode 7 Generate Key (secrets), dan wiring menu tab.
"""

import hashlib
import hmac

import pytest

from cryptolab.core.hashing import hash_compute, hash_file, SUPPORTED_HASH_ALGOS
from cryptolab.core.exceptions import (
    InvalidInputError,
    InvalidKeyError,
    DecodingError,
)
from cryptolab.core.symmetric.aes import aes_gcm_encrypt, aes_gcm_decrypt
from cryptolab.interactive.handlers.ctx_hashing import (
    fn_sha3,
    fn_sha512,
    fn_hmac256,
    fn_keygen,
)
from cryptolab.interactive.handlers.ctx_symmetric import fn_aes_gcm
from cryptolab.interactive.tab_menu import CATEGORIES


@pytest.fixture(autouse=True)
def no_history(monkeypatch):
    """Handler memanggil log_history - matikan agar tes tidak menulis riwayat."""
    from cryptolab.interactive.handlers import ctx_hashing

    monkeypatch.setattr(ctx_hashing, "log_history", lambda *a, **k: True)


class FakeCtx:
    """Ctx tiruan: jawaban diambil berurutan dari daftar (pilihan / input)."""

    def __init__(self, answers):
        self._answers = iter(answers)
        self.inputs = []

    def choose(self, label, options, default=1):
        return next(self._answers)

    def ask(self, label, default=None, cast=str, secret=False):
        return next(self._answers)

    def work(self, text, fn):
        return fn()


def _items(label_kategori):
    for name, group in CATEGORIES:
        if name == label_kategori:
            return {label: target for label, target, _tag in group}
    raise AssertionError(f"Kategori {label_kategori} tidak ditemukan")


# ---------- Mode 1: SHA-3 ----------

class TestSha3Core:
    def test_sha3_256_vektor_dikenal(self):
        # Vektor resmi FIPS 202: SHA3-256("abc")
        res = hash_compute("abc", algorithm="SHA3-256")
        assert res.output_hash == (
            "3a985da74fe225b2045c172d6bd390bd"
            "855f086e3e9d525b46bfe24511431532"
        )

    def test_sha3_512_vektor_dikenal(self):
        res = hash_compute("abc", algorithm="SHA3-512")
        assert res.output_hash == hashlib.sha3_512(b"abc").hexdigest()

    def test_hash_file_sha3_256(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_bytes(b"abc")
        res = hash_file(str(f), algorithm="SHA3-256")
        assert res.output_hash == hashlib.sha3_256(b"abc").hexdigest()
        assert res.metadata["filepath"] == str(f)

    def test_output_lama_tidak_berubah(self):
        # Baseline beku: SHA-256("abc") tetap identik.
        res = hash_compute("abc", algorithm="SHA256")
        assert res.output_hash == (
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad"
        )

    def test_pesan_error_kini_menyebut_sha3(self):
        with pytest.raises(InvalidInputError, match="SHA3-256"):
            hash_compute("abc", algorithm="SHA999")

    def test_supported_hash_algos_termasuk_sha3(self):
        assert "SHA3-256" in SUPPORTED_HASH_ALGOS
        assert "SHA3-512" in SUPPORTED_HASH_ALGOS


# ---------- Mode 1 & 2: handler ----------

class TestHandlerHashMode:
    def test_fn_sha3_teks_tampil_pembanding_sha256(self):
        ctx = FakeCtx(["SHA3-256", "Teks", "abc"])
        res = fn_sha3(ctx)
        rows = dict(res.rows)
        assert rows["SHA3-256"] == hashlib.sha3_256(b"abc").hexdigest()
        assert rows["SHA-256 (pembanding)"] == hashlib.sha256(b"abc").hexdigest()
        assert rows["Teks"] == "abc"

    def test_fn_sha3_file(self, tmp_path):
        f = tmp_path / "d.bin"
        f.write_bytes(b"data")
        ctx = FakeCtx(["SHA3-512", "File", str(f)])
        res = fn_sha3(ctx)
        rows = dict(res.rows)
        assert rows["SHA3-512"] == hashlib.sha3_512(b"data").hexdigest()
        assert rows["File"] == str(f)

    def test_fn_sha512_teks_tampil_pembanding(self):
        ctx = FakeCtx(["Teks", "abc"])
        res = fn_sha512(ctx)
        rows = dict(res.rows)
        assert rows["SHA512"] == hashlib.sha512(b"abc").hexdigest()
        assert rows["SHA-256 (pembanding)"] == hashlib.sha256(b"abc").hexdigest()

    def test_fn_sha512_file(self, tmp_path):
        f = tmp_path / "d.bin"
        f.write_bytes(b"data")
        ctx = FakeCtx(["File", str(f)])
        res = fn_sha512(ctx)
        rows = dict(res.rows)
        assert rows["SHA512"] == hashlib.sha512(b"data").hexdigest()


class TestHmacSha256:
    def test_buat_mac(self):
        ctx = FakeCtx(["Buat MAC", "pesan", "rahasia"])
        res = fn_hmac256(ctx)
        rows = dict(res.rows)
        assert rows["MAC"] == hmac.new(b"rahasia", b"pesan", hashlib.sha256).hexdigest()
        assert rows["Algoritma"] == "HMAC-SHA256"

    def test_verifikasi_mac_cocok(self):
        mac = hmac.new(b"rahasia", b"pesan", hashlib.sha256).hexdigest()
        ctx = FakeCtx(["Verifikasi MAC", "pesan", "rahasia", mac])
        res = fn_hmac256(ctx)
        assert dict(res.rows)["Status"] == "COCOK"

    def test_verifikasi_mac_dimodifikasi_gagal(self):
        mac = hmac.new(b"rahasia", b"pesan", hashlib.sha256).hexdigest()
        ctx = FakeCtx(["Verifikasi MAC", "pesan-lain", "rahasia", mac])
        res = fn_hmac256(ctx)
        assert dict(res.rows)["Status"] == "TIDAK COCOK"
        assert res.note

    def test_verifikasi_lewat_hmac_verify_bukan_perbandingan_langsung(self):
        # Verifikasi wajib lewat hmac_verify (compare_digest), bukan "==".
        import inspect

        from cryptolab.interactive.handlers import ctx_hashing

        src = inspect.getsource(ctx_hashing.fn_hmac256)
        assert "hmac_verify" in src

    def test_hmac_sha256_terwire_ke_handler(self):
        assert _items("Hash")["HMAC-SHA-256"] is fn_hmac256


# ---------- Mode 4: AES-GCM ----------

class TestAesGcmCore:
    def test_roundtrip_teks(self):
        res = aes_gcm_encrypt("rahasia", "kunci-enambelas!")
        back = aes_gcm_decrypt(res.payload, "kunci-enambelas!")
        assert back.output_text == "rahasia"
        assert back.technical_success

    def test_nonce_acak_12_byte_dan_berbeda_tiap_enkripsi(self):
        a = aes_gcm_encrypt("pesan", "kunci-enambelas!")
        b = aes_gcm_encrypt("pesan", "kunci-enambelas!")
        assert len(bytes.fromhex(a.nonce_hex)) == 12
        assert a.nonce_hex != b.nonce_hex
        assert a.payload != b.payload

    def test_tag_rusak_ditolak(self):
        res = aes_gcm_encrypt("pesan", "kunci-enambelas!")
        nonce, ct, tag = res.payload.split(":")
        tag_rusak = ("0" if tag[0] != "0" else "1") + tag[1:]
        with pytest.raises(DecodingError, match="Tag autentikasi AES-GCM tidak valid"):
            aes_gcm_decrypt(f"{nonce}:{ct}:{tag_rusak}", "kunci-enambelas!")

    def test_ciphertext_dimodifikasi_ditolak(self):
        res = aes_gcm_encrypt("pesan", "kunci-enambelas!")
        nonce, ct, tag = res.payload.split(":")
        ct_rusak = ("0" if ct[0] != "0" else "1") + ct[1:]
        with pytest.raises(DecodingError):
            aes_gcm_decrypt(f"{nonce}:{ct_rusak}:{tag}", "kunci-enambelas!")

    def test_kunci_salah_ditolak(self):
        res = aes_gcm_encrypt("pesan", "kunci-enambelas!")
        with pytest.raises(DecodingError):
            aes_gcm_decrypt(res.payload, "kunci-16-berbeda")

    def test_kunci_salah_panjang(self):
        with pytest.raises(InvalidKeyError, match="16 byte"):
            aes_gcm_encrypt("pesan", "pendek")

    def test_format_payload_salah(self):
        with pytest.raises(InvalidInputError, match="Format payload AES-GCM"):
            aes_gcm_decrypt("bukan-payload", "kunci-enambelas!")

    def test_error_tidak_membocorkan_detail_tag(self):
        # Pesan error generik (bukan padding oracle / detail internal).
        from cryptolab.core.symmetric import aes as aes_mod
        import inspect

        src = inspect.getsource(aes_mod.aes_gcm_decrypt)
        assert "MAC check failed" not in src


class TestHandlerAesGcm:
    def test_enkripsi_tampil_nonce_dan_payload(self):
        ctx = FakeCtx(["Enkripsi", "kunci-enambelas!", "rahasia"])
        res = fn_aes_gcm(ctx)
        rows = dict(res.rows)
        assert rows["Nonce (hex, 12 byte)"]
        assert len(rows["Payload (nonce:ciphertext:tag)"].split(":")) == 3

    def test_dekripsi_payload(self):
        enc = aes_gcm_encrypt("rahasia", "kunci-enambelas!")
        ctx = FakeCtx(["Dekripsi", "kunci-enambelas!", enc.payload])
        res = fn_aes_gcm(ctx)
        rows = dict(res.rows)
        assert rows["Plaintext"] == "rahasia"
        assert rows["Tag"] == "VALID"


# ---------- Wiring menu tab ----------

class TestWiringMenuTab:
    def test_sha3_terwire_ke_handler(self):
        assert _items("Hash")["SHA-3"] is fn_sha3

    def test_sha512_terwire_ke_handler(self):
        assert _items("Hash")["SHA-512"] is fn_sha512

    def test_aes_gcm_terwire_ke_handler(self):
        assert _items("Simetris")["AES-GCM"] is fn_aes_gcm

    def test_digital_signature_terwire_ke_rsa(self):
        # RSA-PSS (sign/verify) sudah ada di core & fn_rsa.
        from cryptolab.interactive.handlers.ctx_asymmetric import fn_rsa

        assert _items("Asimetris")["Digital Signature"] is fn_rsa

    def test_generate_key_terwire(self):
        assert _items("Utilitas")["Generate Key"] is fn_keygen


class TestGenerateKey:
    def test_panjang_default_32_byte(self):
        ctx = FakeCtx([32])
        res = fn_keygen(ctx)
        key_hex = dict(res.rows)["Kunci (hex)"]
        assert len(bytes.fromhex(key_hex)) == 32

    def test_dua_panggilan_berbeda(self):
        a = fn_keygen(FakeCtx([16]))
        b = fn_keygen(FakeCtx([16]))
        assert dict(a.rows)["Kunci (hex)"] != dict(b.rows)["Kunci (hex)"]

    def test_validasi_panjang(self):
        # Validasi dilakukan oleh cast saat input (reuse _validate_length).
        from cryptolab.interactive.handlers.ctx_hashing import _validate_length

        with pytest.raises(ValueError):
            _validate_length(0)
        with pytest.raises(ValueError):
            _validate_length(1025)

