"""Tabplexer - a lightweight tab wrapper for Alacritty."""

from .manager import TabManager, Tab
from .ui import run_curses_ui

__all__ = ["TabManager", "Tab", "run_curses_ui"]
