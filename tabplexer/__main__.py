"""Entry point for the Tabplexer application."""
from __future__ import annotations

import argparse
import curses
import locale
import sys

from .ui import run_curses_ui


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tab wrapper for Alacritty")
    parser.add_argument(
        "--no-locale",
        action="store_true",
        help="Do not call locale.setlocale before starting curses.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not args.no_locale:
        locale.setlocale(locale.LC_ALL, "")

    try:
        curses.wrapper(run_curses_ui)
    except KeyboardInterrupt:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
