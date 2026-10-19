"""Caesar Cipher brute force analysis with scoring integration."""

from dataclasses import dataclass, field
from typing import List, Optional
from ..classical.caesar import caesar_decrypt
from ..exceptions import InvalidInputError
from .scoring import calculate_text_score, ScoreResult

# Approximate frequencies for English & Indonesian common letters (for backward compatibility)
COMMON_CHARS = set("ETAOINSRHDLUetaoinsrhdlu")


@dataclass
class CaesarCandidate:
    """Represents one candidate plaintext from a Caesar brute force attempt."""

    shift: int
    text: str
    common_ratio: float
    score: float = 0.0
    score_level: str = "Sedang"
    flag_detected: bool = False
    has_known_flag: bool = False
    reasons: List[str] = field(default_factory=list)


def caesar_brute_force(ciphertext: str) -> List[CaesarCandidate]:
    """Generate all 26 possible Caesar decryption candidates (shifts 0 to 25).

    Args:
        ciphertext: Caesar-encrypted string to test.

    Returns:
        List of 26 CaesarCandidate objects representing shift 0 through 25,
        enriched with readability scores and flag pattern indicators.

    Raises:
        InvalidInputError: If ciphertext is empty or not a string.
    """
    if ciphertext is None or not isinstance(ciphertext, str):
        raise InvalidInputError("Input ciphertext harus berupa string.")
    if len(ciphertext) == 0:
        raise InvalidInputError("Input ciphertext tidak boleh kosong.")

    candidates: List[CaesarCandidate] = []
    alpha_chars = [c for c in ciphertext if c.isalpha()]
    total_alpha = len(alpha_chars)

    for shift in range(26):
        decrypted = caesar_decrypt(ciphertext, shift)
        if total_alpha > 0:
            hits = sum(1 for c in decrypted if c in COMMON_CHARS)
            ratio = hits / total_alpha
        else:
            ratio = 0.0

        # Run enhanced scoring
        score_info: ScoreResult = calculate_text_score(decrypted)

        candidates.append(
            CaesarCandidate(
                shift=shift,
                text=decrypted,
                common_ratio=round(ratio, 4),
                score=score_info.score,
                score_level=score_info.level,
                flag_detected=score_info.flag_detected,
                has_known_flag=score_info.has_known_flag,
                reasons=score_info.reasons,
            )
        )

    return candidates


def find_best_candidate(candidates: List[CaesarCandidate]) -> Optional[CaesarCandidate]:
    """Select the candidate with the highest combined readability score.

    Note:
        The highest scoring candidate is a heuristic estimate and is not
        guaranteed to be the true plaintext. Always review other candidates.

    Args:
        candidates: List of CaesarCandidate objects.

    Returns:
        The top-ranked candidate, or None if the list is empty.
    """
    if not candidates:
        return None
    # Prioritize known flag format (e.g. FLAG{...}), then general flag, then score, then ratio
    return max(
        candidates,
        key=lambda c: (c.has_known_flag, c.flag_detected, c.score, c.common_ratio),
    )
