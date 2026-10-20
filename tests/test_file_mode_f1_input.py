"""F1a — unit tests for ``cryptolab.cli.input`` (no parser wiring).

Step F1a of docs/Prompt/mode-file-spec.md. These tests exercise the pure
helpers directly, with a monkeypatched small limit so boundary tests are fast.
"""

import base64
import os

import pytest

from cryptolab.cli import input as fin
from cryptolab.core.exceptions import InvalidInputError


KEY = b"kunci-enambelas!"  # 16 byte
IV = b"iv-enam-belas-by"  # 16 byte


# ---------------------------------------------------------------------------
# read_file_bytes
# ---------------------------------------------------------------------------
class TestReadFileBytes:
    def test_baca_biasa(self, tmp_path):
        p = tmp_path / "a.txt"
        p.write_bytes(b"halo")
        assert fin.read_file_bytes(str(p), limit=1024) == b"halo"

    def test_tidak_ada(self, tmp_path):
        with pytest.raises(InvalidInputError, match="tidak ditemukan"):
            fin.read_file_bytes(str(tmp_path / "nope"), limit=1024)

    def test_direktori(self, tmp_path):
        with pytest.raises(InvalidInputError, match="bukan berkas biasa"):
            fin.read_file_bytes(str(tmp_path), limit=1024)

    def test_tepat_limit_ok(self, tmp_path):
        p = tmp_path / "a.bin"
        p.write_bytes(b"A" * 100)
        assert len(fin.read_file_bytes(str(p), limit=100)) == 100

    def test_limit_plus_satu_ditolak(self, tmp_path):
        p = tmp_path / "a.bin"
        p.write_bytes(b"A" * 101)
        with pytest.raises(InvalidInputError, match="melebihi batas"):
            fin.read_file_bytes(str(p), limit=100)

    def test_pesan_galat_menyebut_mb(self, tmp_path):
        p = tmp_path / "a.bin"
        p.write_bytes(b"A" * (fin.LIMIT_PLAINTEXT_BYTES + 1))
        with pytest.raises(InvalidInputError, match="MB"):
            fin.read_file_bytes(str(p), limit=fin.LIMIT_PLAINTEXT_BYTES)


# ---------------------------------------------------------------------------
# max_encoded_len / max_binary_len
# ---------------------------------------------------------------------------
class TestBatas:
    def test_binary_gcm(self):
        assert fin.max_binary_len("GCM", 1000) == 1000 + 28

    def test_binary_cbc(self):
        assert fin.max_binary_len("CBC", 1000) == 1000 + 16

    def test_hex_gcm(self):
        assert fin.max_encoded_len("hex", "GCM", 1000) == (1000 + 28) * 2 + 8

    def test_base64_gcm(self):
        b = 1000 + 28
        assert fin.max_encoded_len("base64", "GCM", 1000) == 4 * ((b + 2) // 3) + 8

    def test_raw_gcm(self):
        assert fin.max_encoded_len("raw", "GCM", 1000) == 1000 + 28

    def test_roundtrip_limit_tepat_gcm_hex(self, tmp_path):
        """A ciphertext produced from exactly ``limit`` plaintext must decode."""
        limit = 64
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"A" * limit, KEY)
        parsed = fin.decode_ciphertext(res.payload.encode("ascii"), "hex", "GCM")
        assert len(bytes.fromhex(parsed["ct_hex"])) == limit


# ---------------------------------------------------------------------------
# encode_ciphertext / build_cbc_payload
# ---------------------------------------------------------------------------
class TestEncode:
    def test_gcm_hex_adalah_payload_apa_adanya(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        out = fin.encode_ciphertext(res.payload, "hex", "GCM")
        assert out.decode("ascii") == res.payload

    def test_gcm_raw_layout(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        raw = fin.encode_ciphertext(res.payload, "raw", "GCM")
        nonce_hex, ct_hex, tag_hex = res.payload.split(":")
        assert raw == bytes.fromhex(nonce_hex) + bytes.fromhex(ct_hex) + bytes.fromhex(tag_hex)
        assert len(raw) == 12 + len(b"halo") + 16

    def test_gcm_base64_roundtrip_layout(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        b64 = fin.encode_ciphertext(res.payload, "base64", "GCM")
        assert base64.b64decode(b64) == fin.encode_ciphertext(res.payload, "raw", "GCM")

    def test_cbc_hex_iv_ct(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        assert payload == f"{IV.hex()}:{'aa' * 16}"

    def test_cbc_raw_layout(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        raw = fin.encode_ciphertext(payload, "raw", "CBC")
        assert raw == IV + bytes.fromhex("aa" * 16)
        assert len(raw) == 16 + 16


# ---------------------------------------------------------------------------
# decode_ciphertext
# ---------------------------------------------------------------------------
class TestDecode:
    def test_gcm_hex_roundtrip(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        parsed = fin.decode_ciphertext(res.payload.encode("ascii"), "hex", "GCM")
        assert parsed["nonce_hex"] == res.payload.split(":")[0]

    def test_gcm_raw_roundtrip(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        raw = fin.encode_ciphertext(res.payload, "raw", "GCM")
        parsed = fin.decode_ciphertext(raw, "raw", "GCM")
        assert f"{parsed['nonce_hex']}:{parsed['ct_hex']}:{parsed['tag_hex']}" == res.payload

    def test_gcm_base64_roundtrip(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        b64 = fin.encode_ciphertext(res.payload, "base64", "GCM")
        parsed = fin.decode_ciphertext(b64, "base64", "GCM")
        assert f"{parsed['nonce_hex']}:{parsed['ct_hex']}:{parsed['tag_hex']}" == res.payload

    def test_cbc_hex_roundtrip(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        parsed = fin.decode_ciphertext(payload.encode("ascii"), "hex", "CBC")
        assert parsed["iv_hex"] == IV.hex()
        assert parsed["ct_hex"] == "aa" * 16

    def test_cbc_raw_roundtrip(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        raw = fin.encode_ciphertext(payload, "raw", "CBC")
        parsed = fin.decode_ciphertext(raw, "raw", "CBC")
        assert parsed["iv_hex"] == IV.hex()
        assert parsed["ct_hex"] == "aa" * 16

    # --- whitespace tolerance (§5.5) ---
    def test_hex_newline_akhir(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        parsed = fin.decode_ciphertext((payload + "\n").encode("ascii"), "hex", "CBC")
        assert parsed["ct_hex"] == "aa" * 16

    def test_hex_crlf(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        parsed = fin.decode_ciphertext((payload + "\r\n").encode("ascii"), "hex", "CBC")
        assert parsed["ct_hex"] == "aa" * 16

    def test_hex_gcm_newline_di_tengah(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"halo", KEY)
        nonce, ct, tag = res.payload.split(":")
        messy = f"{nonce}:\n{ct}\r\n:{tag}\n"
        parsed = fin.decode_ciphertext(messy.encode("ascii"), "hex", "GCM")
        assert f"{parsed['nonce_hex']}:{parsed['ct_hex']}:{parsed['tag_hex']}" == res.payload

    def test_bom_utf8_dibuang(self):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        parsed = fin.decode_ciphertext(b"\xef\xbb\xbf" + payload.encode("ascii"), "hex", "CBC")
        assert parsed["iv_hex"] == IV.hex()

    @pytest.mark.parametrize("bom", [b"\xff\xfe", b"\xfe\xff"])
    def test_bom_utf16_galat_khusus(self, bom):
        payload = fin.build_cbc_payload(IV.hex(), "aa" * 16)
        with pytest.raises(InvalidInputError, match="UTF-16"):
            fin.decode_ciphertext(bom + payload.encode("ascii"), "hex", "CBC")

    # --- malformed ---
    def test_hex_ganjil(self):
        with pytest.raises(InvalidInputError, match="ganjil"):
            fin.decode_ciphertext(f"{IV.hex()}:abc".encode("ascii"), "hex", "CBC")

    def test_hex_bukan_hex(self):
        with pytest.raises(InvalidInputError, match="heksadesimal"):
            fin.decode_ciphertext(f"{IV.hex()}:zz".encode("ascii"), "hex", "CBC")

    def test_base64_rusak(self):
        with pytest.raises(InvalidInputError, match="base64"):
            fin.decode_ciphertext(b"!!!!not base64!!!!", "base64", "GCM")

    def test_raw_gcm_terpotong(self):
        with pytest.raises(InvalidInputError, match="terpotong"):
            fin.decode_ciphertext(b"\x00" * 10, "raw", "GCM")

    def test_gcm_kosong_valid_nonce_tag_tanpa_ct(self):
        """Empty GCM plaintext -> 12+0+16 payload must decode (not "terpotong")."""
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"", KEY)
        raw = fin.encode_ciphertext(res.payload, "raw", "GCM")
        assert len(raw) == 28
        parsed = fin.decode_ciphertext(raw, "raw", "GCM")
        assert parsed["ct_hex"] == ""

    def test_gcm_kosong_valid_base64(self):
        from cryptolab.core.symmetric.aes import aes_gcm_encrypt

        res = aes_gcm_encrypt(b"", KEY)
        b64 = fin.encode_ciphertext(res.payload, "base64", "GCM")
        parsed = fin.decode_ciphertext(b64, "base64", "GCM")
        assert parsed["ct_hex"] == ""

    def test_gcm_hex_kurang_bagian(self):
        with pytest.raises(InvalidInputError, match="nonce:ciphertext:tag"):
            fin.decode_ciphertext(b"aa:bb", "hex", "GCM")


# ---------------------------------------------------------------------------
# write_output
# ---------------------------------------------------------------------------
class TestWriteOutput:
    def test_tulis_baru(self, tmp_path):
        out = tmp_path / "o.bin"
        fin.write_output(str(out), b"halo")
        assert out.read_bytes() == b"halo"

    def test_tolak_timpa_tanpa_force(self, tmp_path):
        out = tmp_path / "o.bin"
        out.write_bytes(b"lama")
        with pytest.raises(InvalidInputError, match="sudah ada"):
            fin.write_output(str(out), b"baru")
        assert out.read_bytes() == b"lama"

    def test_force_menimpa(self, tmp_path):
        out = tmp_path / "o.bin"
        out.write_bytes(b"lama")
        fin.write_output(str(out), b"baru", force=True)
        assert out.read_bytes() == b"baru"

    def test_force_tidak_tinggalkan_tmp(self, tmp_path):
        out = tmp_path / "o.bin"
        fin.write_output(str(out), b"baru", force=True)
        sisa = [p.name for p in tmp_path.iterdir() if p.name != "o.bin"]
        assert sisa == []

    def test_direktori_induk_tidak_ada(self, tmp_path):
        with pytest.raises(InvalidInputError, match="Direktori tujuan tidak ada"):
            fin.write_output(str(tmp_path / "sub" / "o.bin"), b"x")

    def test_out_adalah_direktori(self, tmp_path):
        with pytest.raises(InvalidInputError, match="direktori"):
            fin.write_output(str(tmp_path), b"x")

    def test_out_sama_dengan_file(self, tmp_path):
        src = tmp_path / "a.bin"
        src.write_bytes(b"x")
        with pytest.raises(InvalidInputError, match="tidak boleh sama"):
            fin.write_output(str(src), b"y", source_path=str(src))

    def test_out_sama_ejaan_berbeda(self, tmp_path):
        src = tmp_path / "a.bin"
        src.write_bytes(b"x")
        beda = str(tmp_path) + os.sep + "." + os.sep + "a.bin"
        with pytest.raises(InvalidInputError, match="tidak boleh sama"):
            fin.write_output(beda, b"y", source_path=str(src))

    def test_tulis_biner_preserve_newline(self, tmp_path):
        """Binary write must not translate newlines on Windows."""
        out = tmp_path / "o.bin"
        fin.write_output(str(out), b"a\r\nb\n")
        assert out.read_bytes() == b"a\r\nb\n"
