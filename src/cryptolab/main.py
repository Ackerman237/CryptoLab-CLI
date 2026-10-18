"""Main entrypoint for CryptoLab CLI application."""

import sys
from cryptolab.cli import create_parser, handle_cli_args


def configure_windows_terminal() -> None:
    """Ensure standard input/output use UTF-8 and handle terminal compatibility."""
    if sys.platform == "win32":
        try:
            if sys.stdout and hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if sys.stderr and hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
            if sys.stdin and hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass


def main() -> None:
    """Application main function."""
    configure_windows_terminal()
    parser = create_parser()
    args = parser.parse_args()
    exit_code = handle_cli_args(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
