"""Unit tests for Phase 2 format detection, auto-decode pipeline, and edge cases."""

import pytest
from cryptolab import detect_format
from cryptolab import run_decode_pipeline
from cryptolab import base64_encode
from cryptolab import hex_encode
from cryptolab import binary_encode


class TestDetectAndPipelinePhase2:
    """Test suite for Phase 2 detection, multi-stage pipeline, and loop prevention."""

    def test_detect_base64_hex_binary(self):
        # 1. Base64
        b64_res = detect_format("SGVsbG8gV29ybGQ=")
        b64_match = next(r for r in b64_res if r.format_name == "Base64")
        assert b64_match.is_match is True
        assert b64_match.is_valid_utf8 is True
        assert b64_match.preview_decoded == "Hello World"

        # 2. Hex
        hex_res = detect_format("48656c6c6f")
        hex_match = next(r for r in hex_res if r.format_name == "Hexadecimal")
        assert hex_match.is_match is True
        assert hex_match.is_valid_utf8 is True
        assert hex_match.preview_decoded == "Hello"

        # 3. Binary
        bin_res = detect_format("01001000 01101001")
        bin_match = next(r for r in bin_res if r.format_name == "Binary")
        assert bin_match.is_match is True
        assert bin_match.is_valid_utf8 is True
        assert bin_match.preview_decoded == "Hi"

    def test_ambiguous_input_handled_without_overclaiming(self):
        # "feed" is valid hex chars, but only 4 characters and also an English word
        # Should be detected as Low confidence for hex, not claiming certainty
        results = detect_format("feed")
        hex_match = next(r for r in results if r.format_name == "Hexadecimal")
        assert hex_match.is_match is True
        assert hex_match.confidence == "Low"

    def test_non_utf8_binary_handled_safely(self):
        # 0xFF 0xFE 0xFD 0xFC in binary:
        # 11111111 11111110 11111101 11111100 (not valid UTF-8 sequence)
        invalid_utf8_bin = "11111111 11111110 11111101 11111100"
        results = detect_format(invalid_utf8_bin)
        bin_res = next(r for r in results if r.format_name == "Binary")
        assert bin_res.is_match is True
        assert bin_res.is_valid_utf8 is False
        assert bin_res.confidence == "Low"

    def test_non_utf8_hex_handled_safely(self):
        # ff fe fd fc in hex
        results = detect_format("fffefdfc")
        hex_res = next(r for r in results if r.format_name == "Hexadecimal")
        assert hex_res.is_match is True
        assert hex_res.is_valid_utf8 is False

    def test_pipeline_single_and_multi_layer(self):
        # Single layer Base64
        single = base64_encode("Flag{simple}")
        res_single = run_decode_pipeline(single, max_depth=5)
        assert res_single.is_decoded is True
        assert res_single.total_steps == 1
        assert res_single.best_branch.final_text == "Flag{simple}"

        # Triple layer (Challenge "3 benteng": Base64 x 3)
        triple = "WVRKV01GbFhhREZaVnpWbVpWZEZQUT09"
        res_triple = run_decode_pipeline(triple, max_depth=5)
        assert res_triple.is_decoded is True
        assert res_triple.total_steps == 3
        assert res_triple.best_branch.final_text == "ketahuan_ya"

    def test_depth_limit_enforced_strictly(self):
        # Create 4 layers of encoding and set max_depth to 2
        original = "DeepSecret"
        s1 = base64_encode(original)
        s2 = hex_encode(s1, delimiter="")
        s3 = base64_encode(s2)
        s4 = hex_encode(s3, delimiter="")

        res = run_decode_pipeline(s4, max_depth=2)
        assert res.total_steps <= 2
        assert "Batas kedalaman maksimum" in res.notes

    def test_cycles_prevented_safely(self):
        # A test string should terminate without infinite loop
        test_str = "Plain text not encoded"
        res = run_decode_pipeline(test_str, max_depth=5)
        assert res.total_steps == 0
        assert res.best_branch.final_text == test_str
