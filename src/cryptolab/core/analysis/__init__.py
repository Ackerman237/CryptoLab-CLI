"""Analysis module: format detection, brute force, multi-stage pipeline, and scoring."""

from .detect import detect_format, DetectionResult
from .brute_force import (
    caesar_brute_force,
    CaesarCandidate,
    find_best_candidate,
)
from .auto_decode import auto_decode, AutoDecodeResult, DecodeStep
from .scoring import calculate_text_score, ScoreResult
from .pipeline import (
    run_decode_pipeline,
    PipelineResult,
    DecodeBranch,
)
from .auto_engine import (
    run_auto_analysis,
    AutoCandidate,
    AutoAnalysisReport,
)

__all__ = [
    "detect_format",
    "DetectionResult",
    "caesar_brute_force",
    "CaesarCandidate",
    "find_best_candidate",
    "auto_decode",
    "AutoDecodeResult",
    "DecodeStep",
    "calculate_text_score",
    "ScoreResult",
    "run_decode_pipeline",
    "PipelineResult",
    "DecodeBranch",
    "run_auto_analysis",
    "AutoCandidate",
    "AutoAnalysisReport",
]