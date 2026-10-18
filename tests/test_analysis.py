"""Unit tests for analysis tools (brute force, format detection, auto-decode)."""

import pytest
from cryptolab.analysis.brute_force import caesar_brute_force
from cryptolab.analysis.detect import detect_format
from cryptolab.analysis.auto_decode import auto_decode
from cryptolab.analysis.auto_engine import run_auto_analysis
from cryptolab.encoding.base64_codec import base64_encode
from cryptolab.encoding.hex_codec import hex_encode
from cryptolab.encoding.binary_codec import binary_encode
from cryptolab.exceptions import InvalidInputError


class TestCaesarBruteForce:
    """Test suite for Caesar brute force generator."""

    def test_generates_all_26_candidates(self):
        ciphertext = "Khoor, Zruog!"  # "Hello, World!" shifted by 3
        candidates = caesar_brute_force(ciphertext)

        assert len(candidates) == 26
        # Shifts should span 0 to 25
        shifts = [c.shift for c in candidates]
        assert shifts == list(range(26))

        # Shift 3 candidate should be the exact original plaintext
        shift_3_candidate = next(c for c in candidates if c.shift == 3)
        assert shift_3_candidate.text == "Hello, World!"

    def test_preserves_spaces_and_symbols(self):
        ciphertext = "123 !@# ABC"
        candidates = caesar_brute_force(ciphertext)
        assert len(candidates) == 26
        for cand in candidates:
            assert cand.text.startswith("123 !@# ")

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            caesar_brute_force("")


class TestFormatDetection:
    """Test suite for format detection heuristics."""

    def test_detect_binary(self):
        binary_str = "01000001 01000010 01000011"  # "ABC"
        results = detect_format(binary_str)
        bin_res = next(r for r in results if r.format_name == "Binary")
        assert bin_res.is_match is True
        assert bin_res.confidence in ("High", "Medium")
        assert bin_res.preview_decoded == "ABC"

    def test_detect_hexadecimal(self):
        hex_str = "48656c6c6f20576f726c64"  # "Hello World"
        results = detect_format(hex_str)
        hex_res = next(r for r in results if r.format_name == "Hexadecimal")
        assert hex_res.is_match is True
        assert hex_res.confidence == "High"
        assert hex_res.preview_decoded == "Hello World"

    def test_detect_base64(self):
        b64_str = "SGVsbG8gV29ybGQ="  # "Hello World"
        results = detect_format(b64_str)
        b64_res = next(r for r in results if r.format_name == "Base64")
        assert b64_res.is_match is True
        assert b64_res.confidence == "High"
        assert b64_res.preview_decoded == "Hello World"

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            detect_format("")


class TestAutoDecode:
    """Test suite for multi-stage auto-decode and loop protection."""

    def test_multi_stage_decoding(self):
        # Layer 1: "Flag{Lab_Selesai}"
        # Layer 2: Base64
        # Layer 3: Hex
        original = "Flag{Lab_Selesai}"
        stage1 = base64_encode(original)
        stage2 = hex_encode(stage1, delimiter="")

        result = auto_decode(stage2, max_depth=5)
        assert result.is_decoded is True
        assert result.final_text == original
        assert result.total_steps == 2
        assert result.steps[0].codec_name == "Hexadecimal"
        assert result.steps[1].codec_name == "Base64"

    def test_three_layer_pipeline(self):
        # Plain -> Base64 -> Hex -> Binary
        original = "Cyber2026"
        s1 = base64_encode(original)
        s2 = hex_encode(s1, delimiter=" ")
        s3 = binary_encode(s2)

        result = auto_decode(s3, max_depth=5)
        assert result.final_text == original
        assert result.total_steps == 3

    def test_depth_limit_stops_infinite_recursion(self):
        # Create a deep encoding of 4 layers and limit depth to 2
        original = "TopSecret"
        s1 = base64_encode(original)
        s2 = hex_encode(s1, delimiter="")
        s3 = binary_encode(s2)

        result = auto_decode(s3, max_depth=1)
        assert result.total_steps == 1
        assert "Batas kedalaman maksimum" in result.notes

    def test_plain_text_handled_gracefully(self):
        plain = "Ini adalah teks biasa yang tidak terkodekan."
        result = auto_decode(plain, max_depth=5)
        assert result.is_decoded is False
        assert result.total_steps == 0
        assert result.final_text == plain

    def test_empty_input_raises_invalid_input_error(self):
        with pytest.raises(InvalidInputError, match="tidak boleh kosong"):
            auto_decode("")


class TestAutoEngine:
    """Test suite for unified Auto Analyze engine."""

    def test_auto_analyze_empty_input(self):
        from cryptolab.analysis.auto_engine import run_auto_analysis
        with pytest.raises(InvalidInputError):
            run_auto_analysis("")

    def test_auto_analyze_base64_flag(self):
        from cryptolab.analysis.auto_engine import run_auto_analysis
        # "FLAG{sukses_auto_analyze}" in base64:
        # "RkxBR3tzdWtzZXNfYXV0b19hbmFseXplfQ=="
        b64 = "RkxBR3tzdWtzZXNfYXV0b19hbmFseXplfQ=="
        report = run_auto_analysis(b64)
        assert report.top_candidate is not None
        assert report.top_candidate.category == "Encoding"
        assert "FLAG{sukses_auto_analyze}" in report.top_candidate.output_text
        assert report.top_candidate.flag_detected

    def test_auto_analyze_caesar(self):
        from cryptolab.analysis.auto_engine import run_auto_analysis
        # "KHOOR" -> "HELLO" (shift 3)
        report = run_auto_analysis("KHOOR")
        assert report.top_candidate is not None
        assert "Caesar" in report.top_candidate.method
        assert "HELLO" in report.top_candidate.output_text

    def test_auto_analyze_des_detection_and_decryption(self):
        from cryptolab.analysis.auto_engine import run_auto_analysis
        ct_hex = "5828b071ff8b9fe9f28e2f22bd9c3f21"

        # Keyless: detects possible keyed cipher DES
        report_keyless = run_auto_analysis(ct_hex)
        assert "DES" in report_keyless.possible_keyed_ciphers

        # With key and IV
        report_keyed = run_auto_analysis(ct_hex, key="abcdefgh", iv="hgfedcba")
        assert report_keyed.top_candidate is not None
        assert "DES" in report_keyed.top_candidate.method
        assert report_keyed.top_candidate.output_text == "des_enkripsi"

    def test_keyed_cipher_detection_rc2_challenge(self):
        ciphertext = "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8"
        report = run_auto_analysis(ciphertext, key="12345678", iv="qwertyui")

        assert "RC2" in report.possible_keyed_ciphers
        assert report.top_candidate is not None
        assert report.top_candidate.method == "RC2 (CBC, Padding PKCS7)"
        assert report.top_candidate.output_text == "laboratorium_keamanan_3d"

    def test_auto_analyze_vigenere_with_key(self):
        from cryptolab.analysis.auto_engine import run_auto_analysis
        ct = "LXFOPV"  # ATTACK with LEMON
        report = run_auto_analysis(ct, key="LEMON")
        vig_cand = [c for c in report.candidates if "Vigenere" in c.method]
        assert len(vig_cand) > 0
        assert vig_cand[0].output_text == "ATTACK"

