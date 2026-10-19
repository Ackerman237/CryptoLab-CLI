"""History command handler."""

import sys
from argparse import Namespace

from cryptolab import log_history, read_history, clear_history, get_history_file
from cryptolab.cli.formatters import render_history_list, render_box


def _get_history_enabled(args: Namespace) -> bool:
    return not getattr(args, "no_history", False)


def handle_history(args: Namespace) -> int:
    """Handle history command."""
    try:
        history_enabled = _get_history_enabled(args)
        if getattr(args, "clear", False):
            success = clear_history()
            if success:
                print("\n  [OK] Riwayat analisis lokal berhasil dibersihkan.\n")
            else:
                print("\n  [Gagal] Tidak dapat menghapus file riwayat.\n")
        else:
            records = read_history(limit=args.limit)
            print("\n" + render_history_list(records))
        return 0
    except Exception as err:
        print(render_box("Error", "History", "", str(err)), file=sys.stderr)
        return 1