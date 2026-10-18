"""Three-phase flow for CryptoLab interactive actions.

Phase 1: Input - labeled prompts with defaults and validation
Phase 2: Processing - spinner with elapsed time, Ctrl+C cancel
Phase 3: Result - clean display with labels, wrap, scroll, post-options
"""

import sys
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager

from cryptolab.banner import (
    paint, DIM, BOLD, WHITE, GREEN, RED, CYAN, term_width, term_height,
    hide_cursor, show_cursor, clear_screen, clear_from_cursor,
    render_footer, render_header, _clip
)

# ============================================================
# Result container
# ============================================================

@dataclass
class Result:
    """Structured result for display."""
    rows: List[tuple] = field(default_factory=list)  # (label, value, wrap) tuples
    note: str = ""
    error: str = ""
    raw: Any = None  # raw data for repeat/copy

    def add(self, label: str, value: str, wrap: bool = True):
        self.rows.append((label, value, wrap))

    def set_note(self, note: str):
        self.note = note

    def set_error(self, error: str):
        self.error = error


# ============================================================
# Spinner
# ============================================================

class Spinner:
    """Spinner with elapsed time."""
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str):
        self.message = message
        self.start = time.time()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_idx = 0
        self.cancelled = False

    def _spin(self):
        while self._running:
            elapsed = time.time() - self.start
            frame = self.FRAMES[int(elapsed * 10) % len(self.FRAMES)]
            sys.stdout.write(f"\r{paint(self.FRAMES[self._frame_idx], '1;36')} {self.message}  {elapsed:.1f}s")
            sys.stdout.flush()
            self._frame_idx = (self._frame_idx + 1) % len(self.FRAMES)
            time.sleep(0.1)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, success: bool = True):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.2)
        elapsed = time.time() - self.start
        mark = "✓" if success else "✗"
        color = "1;32" if success else "1;31"
        sys.stdout.write(f"\r{paint(mark, color)} {self.message}  {elapsed:.2f}s\n")
        sys.stdout.flush()


@contextmanager
def spinner(message: str):
    """Context manager for spinner."""
    s = Spinner(message)
    s.start()
    try:
        yield s
        s.stop(success=True)
    except KeyboardInterrupt:
        s.stop(success=False)
        raise
    except Exception:
        s.stop(success=False)
        raise


# ============================================================
# Input helpers
# ============================================================

def _render_prompt(label: str, default: str = "", secret: bool = False) -> str:
    """Render a single prompt line."""
    if default:
        prompt = f"{label} [{paint(default, DIM)}] › "
    else:
        prompt = f"{label} › "
    if secret:
        import getpass
        return getpass.getpass(prompt)
    return input(prompt)


def ask(label: str, default: str = "", cast: type = str, secret: bool = False,
        validate: Optional[Callable[[str], str]] = None,
        error_msg: str = "Nilai tidak valid") -> Any:
    """Ask for input with label, default, type casting, and validation."""
    while True:
        raw = _render_prompt(label, default)
        if not raw and default:
            raw = default
        try:
            val = cast(raw) if raw else default
            if validate:
                val = validate(val)
            return val
        except ValueError as e:
            print(f"\r{paint('✗', '1;31')} {error_msg}: {e}")
            continue


def choose(label: str, options: List[str], default: int = 0) -> int:
    """Choose from list with arrow keys."""
    # For now, simple numbered selection
    print()
    for i, opt in enumerate(options):
        mark = paint(">>", "1;36") if i == 0 else "  "
        print(f"  {mark} {i+1}. {opt}")
    while True:
        raw = input(f"pilih [{default+1}] › ")
        if not raw:
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        print(f"\r{paint('✗', '1;31')} Pilih angka 1-{len(options)}")


# ============================================================
# Work runner
# ============================================================

def work(message: str, func: Callable, *args, **kwargs) -> Any:
    """Run function with spinner."""
    with spinner(message) as s:
        return func(*args, **kwargs)


# ============================================================
# Result display
# ============================================================

def _wrap(text: str, width: int, indent: int = 0) -> List[str]:
    """Wrap text to width with indent."""
    if not text:
        return [""]
    words = text.split()
    lines = []
    current = ""
    indent_str = " " * 2
    for word in text.split():
        if len(current) + len(word) + 1 <= width - 4:
            current += (" " if current else "") + word
        else:
            lines.append(indent_str + current)
            current = word
    if current:
        lines.append(indent_str + current)
    return lines or [""]


def render_result(ctx_name: str, result: Result, input_echo: Dict[str, str] = None) -> List[str]:
    """Render result screen with input echo, result rows, and footer."""
    w = term_width()
    lines = []

    # Header
    lines.append("")
    lines.append(paint(f"  CRYPTOLAB › {ctx_name}", "1;36"))
    lines.append(paint("─" * term_width(), DIM))
    lines.append("")

    # Input echo
    if input_echo:
        for label, value in input_echo.items():
            label_w = max(len(k) for k in input_echo.keys()) if input_echo else 10
            lines.append(f"  {label:<{label_w}}  {value}")

    # Result rows
    if result.rows:
        lines.append("")
        for label, value, wrap in result.rows:
            if wrap and len(value) > term_width() - 6:
                for line in _wrap(value, term_width()):
                    lines.append(f"  {label:<12}  {line}" if label else f"  {line}")
            else:
                lines.append(f"  {label:<12}  {value}")

    # Note
    if result.note:
        lines.append("")
        lines.append(paint(result.note, DIM))

    # Error
    if result.error:
        lines.append("")
        lines.append(paint(f"✗ {result.error}", "1;31"))

    # Footer
    lines.append("")
    lines.append(paint("─" * term_width(), DIM))
    lines.append(render_footer([("enter", "kembali"), ("r", "ulangi"), ("q", "keluar")]))

    return lines


# ============================================================
# Main action runner
# ============================================================

def run_action(ctx_name: str, input_fn: Callable, process_fn: Callable,
               input_prompts: List[Dict], allow_repeat: bool = True) -> Any:
    """Run complete action: input → process → result with repeat option."""
    while True:
        # Phase 1: Input
        clear_screen()
        # Compact header
        print(f"\r{paint('CRYPTOLAB', '1;36')} › {paint(ctx_name, '1;36')}{' ' * (term_width() - len(ctx_name) - 14)}ctrl+c batal")
        print(paint("─" * term_width(), DIM))
        print()

        # Collect inputs
        inputs = {}
        for prompt in input_prompts:
            try:
                val = prompt["fn"](**prompt.get("args", {}))
                inputs[prompt["key"]] = val
            except KeyboardInterrupt:
                return None  # Cancelled
            except Exception as e:
                # Show error inline and retry
                print(f"\r{paint('✗', '1;31')} {e}")
                time.sleep(1)
                return None

        # Phase 2: Process
        clear_screen()
        print(f"\r{paint('CRYPTOLAB', '1;36')} › {paint(ctx_name, '1;36')}{' ' * (term_width() - len(ctx_name) - 14)}ctrl+c batal")
        print(paint("─" * term_width(), DIM))
        print()

        # Show input summary
        for k, v in inputs.items():
            print(f"  {k:<12}  {v}")
        print()

        # Run processing
        try:
            with spinner("Memproses...") as s:
                result = process_fn(inputs)
                s.stop(success=True)
        except KeyboardInterrupt:
            print(f"\r{paint('✗', '1;31')} Dibatalkan")
            time.sleep(0.5)
            return None
        except Exception as e:
            print(f"\r{paint('✗', '1;31')} Error: {e}")
            time.sleep(1)
            continue

        # Phase 3: Result
        clear_screen()
        result_rows = render_result(ctx_name, result, inputs)
        print("\n".join(result_rows))

        # Post-result options
        while True:
            choice = input("pilih › ").strip().lower()
            if choice in ("", "q", "keluar", "enter", "kembali"):
                return result
            elif choice == "r" and allow_repeat:
                break  # Repeat from input phase
        # Loop continues for repeat