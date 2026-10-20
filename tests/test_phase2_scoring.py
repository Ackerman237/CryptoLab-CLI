"""Unit tests for Phase 2 candidate scoring engine."""

import pytest
from cryptolab import calculate_text_score, ScoreResult


class TestScoringEngine:
    """Test suite for text readability and pattern scoring."""

    def test_consistent_scoring_for_same_input(self):
        text = "Praktikum Keamanan Informasi 2026 - Belajar Kriptografi"
        res1 = calculate_text_score(text)
        res2 = calculate_text_score(text)
        assert res1.score == res2.score
        assert res1.level == res2.level
        assert res1.reasons == res2.reasons

    def test_detects_flag_pattern(self):
        flag_text = "Selamat, flag Anda adalah FLAG{c43s4r_c1ph3r_succ3ss}!"
        res = calculate_text_score(flag_text)
        assert res.flag_detected is True
        assert len(res.flag_matches) >= 1
        assert "FLAG{c43s4r_c1ph3r_succ3ss}" in res.flag_matches[0]
        assert any("flag" in r.lower() for r in res.reasons)

    def test_detects_various_flag_prefixes(self):
        for sample in ["LAB{serangan_fajar_normandia_1944}", "CTF{basic_encoding}", "cyber{test_flag}"]:
            res = calculate_text_score(sample)
            assert res.flag_detected is True
            assert res.level in ("Tinggi", "Sangat Tinggi")

    def test_unprintable_bytes_score_low(self):
        unprintable = "\x00\x01\x02\x03\xff\xfe\x07\x08"
        res = calculate_text_score(unprintable)
        assert res.score < 25.0
        assert res.level == "Sangat Rendah"
        assert res.flag_detected is False

    def test_empty_input_handled_safely(self):
        res = calculate_text_score("")
        assert res.score == 0.0
        assert res.level == "Sangat Rendah"

    def test_random_consonant_gibberish_scores_lower_than_natural_text(self):
        natural = "This is a meaningful readable sentence with clear words."
        gibberish = "zqxjkwvrpt bfmclpndg trkzwx vq"
        res_nat = calculate_text_score(natural)
        res_gib = calculate_text_score(gibberish)
        assert res_nat.score > res_gib.score
