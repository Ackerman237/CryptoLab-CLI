"""Message widget - unified error/success/warning/info formatting."""

from cryptolab.ui.theme import Color, Symbol, Spacing


class Message:
    """Unified message formatting for consistent error/success/warning/info display."""

    PREFIX_ERROR = f"{Color.red(Symbol.ERROR)}"
    PREFIX_SUCCESS = f"{Color.green(Symbol.SUCCESS)}"
    PREFIX_WARNING = f"{Color.yellow(Symbol.WARNING)}"
    PREFIX_INFO = f"{Color.cyan(Symbol.INFO)}"

    @staticmethod
    def error(title: str, detail: str = "") -> str:
        """Error message: ✗ TITLE - detail"""
        msg = f"{Message.PREFIX_ERROR} {Color.red(title)}"
        if detail:
            msg += f"{Spacing.PAD}{Color.dim(detail)}"
        return msg

    @staticmethod
    def success(title: str, detail: str = "") -> str:
        """Success message: ✓ TITLE - detail"""
        msg = f"{Message.PREFIX_SUCCESS} {Color.green(title)}"
        if detail:
            msg += f"{Spacing.PAD}{Color.dim(detail)}"
        return msg

    @staticmethod
    def warning(title: str, detail: str = "") -> str:
        """Warning message: ⚠ TITLE - detail"""
        msg = f"{Message.PREFIX_WARNING} {Color.yellow(title)}"
        if detail:
            msg += f"{Spacing.PAD}{Color.dim(detail)}"
        return msg

    @staticmethod
    def info(title: str, detail: str = "") -> str:
        """Info message: ℹ TITLE - detail"""
        msg = f"{Message.PREFIX_INFO} {Color.cyan(title)}"
        if detail:
            msg += f"{Spacing.PAD}{Color.dim(detail)}"
        return msg

    @staticmethod
    def error_box(title: str, detail: str = "", width: int = 70) -> str:
        """Error in a box format (CLI style)."""
        from cryptolab.ui.widgets.rule import Rule
        lines = [
            Rule.heavy(width),
            f"  {Color.red('CRYPTOLAB CLI - ERROR')}",
            Rule.heavy(width),
            f"  {title}",
        ]
        if detail:
            lines.append(f"  {detail}")
        lines.append(Rule.heavy(width))
        return "\n".join(lines)

    @staticmethod
    def success_box(
        title: str, operation: str, status: str, input_text: str, output_text: str, params: dict = None, width: int = 70
    ) -> str:
        """Success result box (CLI style)."""
        from cryptolab.ui.widgets.rule import Rule
        lines = [
            Rule.heavy(width),
            f"  CRYPTOLAB CLI - {title.upper()}",
            Rule.heavy(width),
            f"  {operation}",
            f"  Status: {status}",
            Rule.light(width),
            f"  Input:  {input_text}",
            f"  Output: {output_text}",
        ]
        if params:
            for k, v in params.items():
                lines.append(f"  {k}: {v}")
        lines.append(Rule.heavy(width))
        return "\n".join(lines)

    @staticmethod
    def print_error(title: str, detail: str = "") -> None:
        """Print error message to stdout."""
        print(Message.error(title, detail))

    @staticmethod
    def print_success(title: str, detail: str = "") -> None:
        """Print success message to stdout."""
        print(Message.success(title, detail))

    @staticmethod
    def print_warning(title: str, detail: str = "") -> None:
        """Print warning message to stdout."""
        print(Message.warning(title, detail))

    @staticmethod
    def print_info(title: str, detail: str = "") -> None:
        """Print info message to stdout."""
        print(Message.info(title, detail))