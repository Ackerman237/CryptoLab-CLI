"""Analysis module: format detection, brute force, multi-stage pipeline, and scoring."""

from cryptolab.analysis.detect import detect_format, DetectionResult
from cryptolab.analysis.brute_force import (
    caesar_brute_force,
    CaesarCandidate,
    find_best_candidate,
)
from cryptolab.analysis.auto_decode import auto_decode, AutoDecodeResult, DecodeStep
from cryptolab.analysis.scoring import calculate_text_score, ScoreResult
from cryptolab.analysis.pipeline import (
    run_decode_pipeline,
    PipelineResult,
    DecodeBranch,
)
from cryptolab.analysis.auto_engine import (
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

