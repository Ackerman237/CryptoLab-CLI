"""Multi-stage auto-decoding pipeline with branching and depth protection."""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
from cryptolab.exceptions import InvalidInputError, DecodingError
from cryptolab.encoding.binary_codec import binary_decode
from cryptolab.encoding.hex_codec import hex_decode
from cryptolab.encoding.base64_codec import base64_decode
from cryptolab.analysis.detect import is_printable_text, detect_format
from cryptolab.analysis.scoring import calculate_text_score, ScoreResult


@dataclass
class DecodeStep:
    """Record of a single decoding stage."""

    step_number: int
    codec_name: str
    input_preview: str
    output_preview: str


@dataclass
class DecodeBranch:
    """A distinct path of transformations and its final candidate output."""

    steps: List[DecodeStep] = field(default_factory=list)
    final_text: str = ""
    score: float = 0.0
    score_level: str = "Sedang"
    flag_detected: bool = False
    reasons: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def total_steps(self) -> int:
        return len(self.steps)


@dataclass
class PipelineResult:
    """Complete result of pipeline analysis including primary and alternative branches."""

    original_text: str
    best_branch: DecodeBranch
    alternative_branches: List[DecodeBranch] = field(default_factory=list)
    total_steps: int = 0
    is_decoded: bool = False
    notes: str = ""


def _find_applicable_codecs(text: str) -> List[Tuple[str, str]]:
    """Find all valid decoders that produce printable, non-trivial UTF-8 text.

    Returns:
        List of tuples: (codec_name, decoded_text).
    """
    valid_transformations: List[Tuple[str, str]] = []
    detections = detect_format(text)

    # Check matches in prioritized order: Binary, Hex, Base64
    for det in detections:
        if not det.is_match or det.confidence == "None":
            continue

        try:
            if det.format_name == "Binary":
                res = binary_decode(text)
                if res != text and is_printable_text(res):
                    valid_transformations.append(("Binary", res))
            elif det.format_name == "Hexadecimal":
                res = hex_decode(text)
                if res != text and is_printable_text(res):
                    valid_transformations.append(("Hexadecimal", res))
            elif det.format_name == "Base64":
                res = base64_decode(text)
                if res != text and is_printable_text(res):
                    valid_transformations.append(("Base64", res))
        except (DecodingError, InvalidInputError):
            continue

    return valid_transformations


def run_decode_pipeline(
    text: str, max_depth: int = 5, beam_width: int = 3
) -> PipelineResult:
    """Execute multi-stage decoding across potential branches with bounded search.

    Prevents:
    - Combinatorial explosion using beam width bounding.
    - Infinite loops using cycle detection.
    - Runaway transformations using max_depth limit.

    Args:
        text: Input string to decode.
        max_depth: Maximum recursion/transformation steps (default: 5).
        beam_width: Maximum branches to explore concurrently (default: 3).

    Returns:
        PipelineResult with best branch and alternative candidates.

    Raises:
        InvalidInputError: If text is empty or invalid, or max_depth < 1.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    cleaned = text.strip()
    if len(cleaned) == 0:
        raise InvalidInputError("Input teks tidak boleh kosong.")
    if max_depth < 1:
        raise InvalidInputError("Batas kedalaman (max_depth) harus minimal 1.")

    # State: (current_text, steps_list, seen_set)
    initial_state = (cleaned, [], {cleaned})
    active_branches = [initial_state]
    completed_branches: List[DecodeBranch] = []

    for depth in range(1, max_depth + 1):
        next_branches = []
        for current_text, steps, seen_states in active_branches:
            codecs = _find_applicable_codecs(current_text)

            if not codecs:
                # Terminal node: no further decoders apply
                score_info = calculate_text_score(current_text)
                branch_notes = (
                    f"Transformasi selesai pada kedalaman ke-{len(steps)}."
                    if steps
                    else "Tidak ada format encoding yang cocok."
                )
                completed_branches.append(
                    DecodeBranch(
                        steps=steps,
                        final_text=current_text,
                        score=score_info.score,
                        score_level=score_info.level,
                        flag_detected=score_info.flag_detected,
                        reasons=score_info.reasons,
                        notes=branch_notes,
                    )
                )
                continue

            for codec_name, decoded in codecs:
                # Cycle detection
                if decoded in seen_states:
                    score_info = calculate_text_score(current_text)
                    completed_branches.append(
                        DecodeBranch(
                            steps=steps,
                            final_text=current_text,
                            score=score_info.score,
                            score_level=score_info.level,
                            flag_detected=score_info.flag_detected,
                            reasons=score_info.reasons,
                            notes="Siklus berulang terdeteksi; cabang dihentikan untuk mencegah loop.",
                        )
                    )
                    continue

                preview_in = (
                    current_text
                    if len(current_text) <= 50
                    else current_text[:47] + "..."
                )
                preview_out = (
                    decoded if len(decoded) <= 50 else decoded[:47] + "..."
                )

                new_step = DecodeStep(
                    step_number=depth,
                    codec_name=codec_name,
                    input_preview=preview_in,
                    output_preview=preview_out,
                )

                next_branches.append(
                    (decoded, steps + [new_step], seen_states | {decoded})
                )

        if not next_branches:
            break

        # Prune branches if exceeding beam width to avoid exponential explosion
        # Sort by intermediate score
        next_branches.sort(
            key=lambda item: calculate_text_score(item[0]).score, reverse=True
        )
        active_branches = next_branches[:beam_width]
    else:
        # Depth limit reached for remaining active branches
        for current_text, steps, _ in active_branches:
            score_info = calculate_text_score(current_text)
            completed_branches.append(
                DecodeBranch(
                    steps=steps,
                    final_text=current_text,
                    score=score_info.score,
                    score_level=score_info.level,
                    flag_detected=score_info.flag_detected,
                    reasons=score_info.reasons,
                    notes=f"Batas kedalaman maksimum ({max_depth} langkah) tercapai.",
                )
            )

    if not completed_branches:
        # Fallback if text was not transformed
        score_info = calculate_text_score(cleaned)
        completed_branches.append(
            DecodeBranch(
                steps=[],
                final_text=cleaned,
                score=score_info.score,
                score_level=score_info.level,
                flag_detected=score_info.flag_detected,
                reasons=score_info.reasons,
                notes="Teks asli tidak memerlukan decoding tambahan.",
            )
        )

    # Rank completed branches by: flag_detected (1st), score (2nd), and number of successful steps
    completed_branches.sort(
        key=lambda b: (b.flag_detected, b.score, len(b.steps)), reverse=True
    )

    best = completed_branches[0]
    # Filter distinct alternative candidates (different final text from best)
    seen_finals = {best.final_text}
    alternatives = []
    for branch in completed_branches[1:]:
        if branch.final_text not in seen_finals and branch.total_steps > 0:
            alternatives.append(branch)
            seen_finals.add(branch.final_text)

    is_decoded = best.total_steps > 0
    overall_notes = best.notes

    return PipelineResult(
        original_text=text,
        best_branch=best,
        alternative_branches=alternatives,
        total_steps=best.total_steps,
        is_decoded=is_decoded,
        notes=overall_notes,
    )
