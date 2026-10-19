"""Analysis command handlers (detect, analyze, auto)."""

import sys
from argparse import Namespace

from cryptolab.analysis.detect import detect_format, DetectionResult
from cryptolab.analysis.auto_decode import auto_decode, AutoDecodeResult
from cryptolab.analysis.pipeline import run_decode_pipeline, PipelineResult

from cryptolab.exceptions import InvalidInputError
from cryptolab.utils.history import log_history
from cryptolab.cli.formatters import (
    render_detection,
    render_auto_decode,
    render_pipeline_result,
)


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def handle_analyze(args: Namespace) -> int:
    """Handle analyze command."""
    try:
        history_enabled = _get_history_enabled(args)
        results = detect_format(args.text)
        print(render_detection(args.text, results))
        summary = ", ".join(r.format_name for r in results if r.is_match)
        log_history("Format Detection", args.text, summary or "None", enabled=history_enabled)
        return 0
    except InvalidInputError as err:
        print(render_detection(args.text, []), file=sys.stderr)
        return 1


def handle_detect(args: Namespace) -> int:
    """Handle detect command (alias for analyze)."""
    return handle_analyze(args)


def handle_auto(args: Namespace) -> int:
    """Handle auto command (multi-stage pipeline)."""
    try:
        history_enabled = _get_history_enabled(args)
        pipeline_res = run_decode_pipeline(args.text, max_depth=args.depth)
        print(render_pipeline_result(pipeline_res))
        log_history(
            "Auto Decode Pipeline",
            args.text,
            pipeline_res.best_branch.final_text,
            {"depth": args.depth, "steps": pipeline_res.total_steps},
            enabled=history_enabled,
        )
        return 0
    except InvalidInputError as err:
        print(render_pipeline_result(PipelineResult()), file=sys.stderr)
        return 1