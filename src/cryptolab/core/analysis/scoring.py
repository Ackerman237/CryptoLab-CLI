"""Text readability and flag pattern scoring engine."""

import re
from dataclasses import dataclass, field
from typing import List

# Common letters in English & Indonesian
COMMON_LETTERS = set("ETAOINSRHDLUetaoinsrhdlu")
VOWELS = set("AEIOUaeiou")

# Common bigrams in English & Indonesian natural words
COMMON_BIGRAMS = {
    "th", "he", "in", "er", "an", "re", "on", "at", "en", "nd",
    "ti", "es", "or", "te", "of", "ed", "is", "it", "al", "ar",
    "st", "to", "ay", "da", "ha", "ap", "pp", "ir", "rt", "ng",
    "an", "ka", "ma", "ra", "sa", "pa", "la", "ta", "ya", "me",
}

# Known CTF flag prefixes (non-capturing group so findall returns full matched text)
KNOWN_FLAG_REGEX = re.compile(
    r"(?i)\b(?:FLAG|CTF|LAB|CYBER|KEY|SECRET|CHALL)\{[^{}\s\r\n]{2,120}\}"
)
GENERIC_FLAG_REGEX = re.compile(
    r"(?i)\b[a-zA-Z0-9_\-]{2,15}\{[^{}\s\r\n]{2,120}\}"
)


@dataclass
class ScoreResult:
    """Result of text scoring analysis."""

    score: float  # 0.0 to 100.0
    level: str  # "Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"
    reasons: List[str] = field(default_factory=list)
    flag_detected: bool = False
    has_known_flag: bool = False
    flag_matches: List[str] = field(default_factory=list)
    printable_ratio: float = 0.0
    letter_ratio: float = 0.0

    def summary(self) -> str:
        """Return a compact one-line summary of score and level."""
        flag_note = " [Pola Flag Ditemukan]" if self.flag_detected else ""
        return f"{self.score:.1f}/100 ({self.level}){flag_note}"


def calculate_text_score(text: str) -> ScoreResult:
    """Evaluate text readability and search for interesting patterns (flags, natural words).

    Note:
        The score is a heuristic readability index, not a calibrated statistical
        probability. A high score does not guarantee the text is the intended plaintext.

    Args:
        text: Plaintext or decoded candidate string to evaluate.

    Returns:
        ScoreResult containing score (0-100), quality level, detected flags, and reasons.
    """
    if not text or not isinstance(text, str):
        return ScoreResult(
            score=0.0,
            level="Sangat Rendah",
            reasons=["Teks kosong atau tidak valid"],
        )

    length = len(text)
    reasons: List[str] = []

    # 1. Printable characters proportion
    printable_count = sum(1 for c in text if c.isprintable() or c in "\r\n\t")
    printable_ratio = printable_count / length

    # 2. Alphabet letter proportion
    alpha_count = sum(1 for c in text if c.isalpha())
    letter_ratio = alpha_count / length

    # If mostly unprintable bytes, immediately assign very low score
    if printable_ratio < 0.6:
        return ScoreResult(
            score=round(printable_ratio * 20.0, 1),
            level="Sangat Rendah",
            reasons=[f"Karakter non-printable dominan ({printable_ratio*100:.1f}%)"],
            printable_ratio=round(printable_ratio, 3),
            letter_ratio=round(letter_ratio, 3),
        )

    points = 0.0

    # Printable bonus (up to 25 points)
    points += printable_ratio * 25.0
    reasons.append(f"Karakter terbaca/printable: {printable_ratio*100:.1f}%")

    # Letter bonus (up to 20 points)
    points += letter_ratio * 20.0
    reasons.append(f"Proporsi alfabet: {letter_ratio*100:.1f}%")

    # Common letters & vowels (up to 25 points)
    if alpha_count > 0:
        common_count = sum(1 for c in text if c in COMMON_LETTERS)
        common_ratio = common_count / alpha_count
        points += common_ratio * 15.0

        vowel_count = sum(1 for c in text if c in VOWELS)
        vowel_ratio = vowel_count / alpha_count
        # Natural languages usually have 20% - 50% vowels among letters
        if 0.20 <= vowel_ratio <= 0.55:
            points += 10.0
            reasons.append(f"Rasio vokal alami ({vowel_ratio*100:.1f}%)")
        else:
            points += 4.0

    # Word structure & bigram frequency (up to 15 points)
    words = re.findall(r"[A-Za-z]+", text.lower())
    if words:
        total_bigrams = sum(max(0, len(w) - 1) for w in words)
        bigram_hits = sum(
            1 for w in words for i in range(len(w) - 1) if w[i : i + 2] in COMMON_BIGRAMS
        )
        if total_bigrams > 0:
            bigram_ratio = bigram_hits / total_bigrams
            points += bigram_ratio * 15.0
            if bigram_ratio >= 0.35:
                reasons.append(f"Pola suku kata alami ({bigram_ratio*100:.0f}%)")
        else:
            points += 5.0

    # Flag pattern detection (up to 15 points bonus + flag highlight)
    known_flags = KNOWN_FLAG_REGEX.findall(text)
    generic_flags = GENERIC_FLAG_REGEX.findall(text)

    flag_detected = False
    has_known_flag = False
    flag_matches: List[str] = []

    if known_flags:
        points += 15.0
        flag_detected = True
        has_known_flag = True
        flag_matches = [m if isinstance(m, str) else m[0] for m in known_flags]
        reasons.append(
            f"Terdeteksi format flag standar (prioritas tinggi): {', '.join(flag_matches[:2])}"
        )
    elif generic_flags:
        points += 5.0
        flag_detected = True
        flag_matches = generic_flags
        reasons.append(
            f"Terdeteksi pola kurung kurawal kandidat flag: {', '.join(flag_matches[:2])}"
        )

    # Clamp points between 0.0 and 100.0
    final_score = max(0.0, min(100.0, points))

    # Determine qualitative level
    if final_score >= 80.0:
        level = "Sangat Tinggi"
    elif final_score >= 65.0:
        level = "Tinggi"
    elif final_score >= 45.0:
        level = "Sedang"
    elif final_score >= 25.0:
        level = "Rendah"
    else:
        level = "Sangat Rendah"

    return ScoreResult(
        score=round(final_score, 1),
        level=level,
        reasons=reasons,
        flag_detected=flag_detected,
        has_known_flag=has_known_flag,
        flag_matches=flag_matches,
        printable_ratio=round(printable_ratio, 3),
        letter_ratio=round(letter_ratio, 3),
    )
