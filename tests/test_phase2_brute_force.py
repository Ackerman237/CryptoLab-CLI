"""Unit tests for Phase 2 Caesar Brute Force enhancements."""

import pytest
from cryptolab.analysis.brute_force import caesar_brute_force, find_best_candidate


class TestCaesarBruteForcePhase2:
    """Test suite for Caesar brute force candidate ranking and --best option."""

    def test_generates_exactly_26_candidates(self):
        ciphertext = "KHOOR"
        candidates = caesar_brute_force(ciphertext)
        assert len(candidates) == 26
        assert [c.shift for c in candidates] == list(range(26))

    def test_finds_correct_shift_for_known_ciphertext(self):
        # "KHOOR" shifted by 3 from "HELLO"
        ciphertext = "KHOOR"
        candidates = caesar_brute_force(ciphertext)
        best = find_best_candidate(candidates)
        assert best is not None
        assert best.shift == 3
        assert best.text == "HELLO"

    def test_finds_correct_shift_for_lab_challenge_6(self):
        # Lab challenge: "yrggp_szikyurp" -> "happy_birthday" at shift 17
        ciphertext = "yrggp_szikyurp"
        candidates = caesar_brute_force(ciphertext)
        best = find_best_candidate(candidates)
        assert best is not None
        assert best.shift == 17
        assert best.text == "happy_birthday"

    def test_candidate_with_flag_format_ranked_best(self):
        # Caesar encrypted flag: "Flag{c43s4r}" shifted by 7 is "Mshn{j43z4y}"
        ciphertext = "Mshn{j43z4y}"
        candidates = caesar_brute_force(ciphertext)
        best = find_best_candidate(candidates)
        assert best is not None
        assert best.shift == 7
        assert best.text == "Flag{c43s4r}"
        assert best.flag_detected is True

    def test_preserves_spaces_symbols_numbers_and_casing(self):
        # "HELLO, World!" shifted by 3 is "KHOOR, Zruog!"
        ciphertext = "KHOOR, Zruog! #2026"
        candidates = caesar_brute_force(ciphertext)
        for c in candidates:
            assert c.text.endswith("! #2026")
        cand_3 = next(c for c in candidates if c.shift == 3)
        assert cand_3.text == "HELLO, World! #2026"
