"""CLI Entry Point - cryptolab command."""

import sys
from cryptolab.cli import create_parser, handle_cli_args
from cryptolab.interactive import run_interactive_menu


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command provided, show help and enter interactive menu
    if args.command is None or args.command == "menu":
        run_interactive_menu()
        return 0

    return handle_cli_args(args)


if __name__ == "__main__":
    sys.exit(main())