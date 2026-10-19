"""Analysis module: format detection, brute force, multi-stage pipeline, and scoring. Backward compatibility."""

from cryptolab.core.analysis import (
    detect_format,
    DetectionResult,
    caesar_brute_force,
    CaesarCandidate,
    find_best_candidate,
    auto_decode,
    AutoDecodeResult,
    DecodeStep,
    calculate_text_score,
    ScoreResult,
    run_decode_pipeline,
    PipelineResult,
    DecodeBranch,
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