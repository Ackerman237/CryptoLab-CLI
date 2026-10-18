"""Multi-stage auto-decode analyzer with depth limit and loop prevention.

Maintains full backward compatibility with Phase 1 while leveraging the enhanced pipeline.
"""

from dataclasses import dataclass
from typing import List
from cryptolab.analysis.pipeline import (
    DecodeStep,
    run_decode_pipeline,
)


@dataclass
class AutoDecodeResult:
    """Result of multi-stage auto-decoding."""

    original_text: str
    final_text: str
    steps: List[DecodeStep]
    total_steps: int
    is_decoded: bool
    notes: str


def auto_decode(text: str, max_depth: int = 5) -> AutoDecodeResult:
    """Attempt multi-stage decoding on layered encoded texts.

    Stops when:
    - Maximum depth is reached (prevent runaway execution).
    - A cycle/loop is detected.
    - No further valid encoding is detected or decodable into printable text.

    Args:
        text: Input string to decode.
        max_depth: Maximum number of decoding steps (default: 5).

    Returns:
        AutoDecodeResult containing step-by-step history and final output.

    Raises:
        InvalidInputError: If text is empty or invalid, or max_depth < 1.
    """
    pipeline_res = run_decode_pipeline(text, max_depth=max_depth)
    return AutoDecodeResult(
        original_text=pipeline_res.original_text,
        final_text=pipeline_res.best_branch.final_text,
        steps=pipeline_res.best_branch.steps,
        total_steps=pipeline_res.total_steps,
        is_decoded=pipeline_res.is_decoded,
        notes=pipeline_res.notes,
    )
