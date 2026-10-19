"""Interactive Entry Point - cryptolab menu."""

import sys
from cryptolab.interactive import run_interactive_menu


def main() -> int:
    """Main interactive entry point."""
    run_interactive_menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())