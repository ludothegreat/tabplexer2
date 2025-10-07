"""Curses based user interface for Tabplexer."""

import curses
import textwrap
from typing import Optional
from __future__ import annotations
from .manager import TabManager, Tab, AlacrittyNotFoundError


HELP_TEXT = textwrap.dedent(
    """
    Controls:
      ↑/k and ↓/j    Move selection
      Enter          Focus selected tab (requires wmctrl)
      n              Create a new tab
      r              Rename selected tab
      c              Close selected tab
      x              Remove exited tabs from the list
      q              Quit Tabplexer (running tabs stay alive)

    When creating a tab you can leave fields blank to accept defaults.
    """
)


def _safe_input(stdscr: "curses._CursesWindow", prompt: str) -> Optional[str]:
    height, width = stdscr.getmaxyx()
    stdscr.attrset(0)
    stdscr.move(height - 2, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 2, 0, prompt)
    stdscr.refresh()

    curses.echo()
    try:
        value = stdscr.getstr(height - 2, len(prompt), width - len(prompt) - 1)
    except curses.error:
        value = b""
    finally:
        curses.noecho()

    if value is None:
        return None
    return value.decode().strip()


def _draw_header(stdscr: "curses._CursesWindow", manager: TabManager) -> None:
    wmctrl_hint = " (wmctrl unavailable)" if not manager.wmctrl_available else ""
    header = f"Tabplexer - {len(manager.tabs)} tab(s){wmctrl_hint}"
    stdscr.attrset(curses.A_BOLD)
    stdscr.addstr(0, 0, header)
    stdscr.attrset(0)


def _draw_footer(stdscr: "curses._CursesWindow", message: str) -> None:
    height, width = stdscr.getmaxyx()
    stdscr.attrset(curses.A_REVERSE)
    stdscr.move(height - 1, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 1, 0, message[: max(width - 1, 0)])
    stdscr.attrset(0)


def _format_tab_line(tab: Tab) -> str:
    status = "running" if tab.is_running() else f"exited ({tab.exit_code})"
    command = tab.command or "<shell>"
    return f"[{tab.identifier:02d}] {tab.title} - {status} - {command}"


def _draw_tabs(stdscr: "curses._CursesWindow", manager: TabManager, selected_index: int) -> None:
    height, width = stdscr.getmaxyx()
    for idx, tab in enumerate(manager.tabs):
        if idx + 2 >= height - 1:
            break
        stdscr.move(idx + 2, 0)
        stdscr.clrtoeol()
        line = _format_tab_line(tab)
        if idx == selected_index:
            stdscr.attrset(curses.A_REVERSE)
        else:
            stdscr.attrset(0)
        stdscr.addstr(idx + 2, 0, line[: max(width - 1, 0)])
    stdscr.attrset(0)


def _display_help(stdscr: "curses._CursesWindow") -> None:
    stdscr.clear()
    stdscr.attrset(0)
    for idx, line in enumerate(HELP_TEXT.strip().splitlines()):
        stdscr.addstr(idx + 1, 2, line)
    stdscr.attrset(curses.A_REVERSE)
    stdscr.addstr(len(HELP_TEXT.splitlines()) + 2, 2, "Press any key to return")
    stdscr.attrset(0)
    stdscr.refresh()
    stdscr.getch()


def run_curses_ui(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    message = "Press ? for help."

    try:
        manager = TabManager()
    except AlacrittyNotFoundError as exc:
        stdscr.clear()
        stdscr.addstr(0, 0, str(exc))
        stdscr.refresh()
        stdscr.getch()
        return

    selected_index = 0
    while True:
        manager.refresh()
        tabs = manager.tabs
        if tabs:
            selected_index = max(0, min(selected_index, len(tabs) - 1))
        else:
            selected_index = 0

        stdscr.clear()
        _draw_header(stdscr, manager)
        _draw_tabs(stdscr, manager, selected_index)
        _draw_footer(stdscr, message)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (ord("q"), 27):  # q or ESC
            break
        if key in (ord("?"), ord("h")):
            _display_help(stdscr)
            message = "Press ? for help."
            continue
        if key in (curses.KEY_UP, ord("k")):
            selected_index = max(0, selected_index - 1)
            continue
        if key in (curses.KEY_DOWN, ord("j")):
            selected_index = min(len(tabs) - 1, selected_index + 1) if tabs else 0
            continue
        if key == ord("n"):
            title = _safe_input(stdscr, "Title (optional): ")
            command = _safe_input(stdscr, "Command (optional): ")
            if command == "":
                command = None
            if title == "":
                title = None
            try:
                manager.create_tab(title=title, command=command)
                message = "Created new tab."
            except Exception as exc:  # pragma: no cover - defensive
                message = f"Failed to create tab: {exc}"
            continue
        if key == ord("r") and tabs:
            new_title = _safe_input(stdscr, "New title: ")
            if new_title:
                tabs[selected_index].title = new_title
                message = "Renamed tab."
            else:
                message = "Rename cancelled."
            continue
        if key == ord("c") and tabs:
            manager.close_tab(tabs[selected_index])
            message = "Sent termination signal to tab."
            continue
        if key == ord("x"):
            before = len(manager.tabs)
            manager.prune()
            removed = before - len(manager.tabs)
            message = f"Removed {removed} tab(s)."
            continue
        if key in (curses.KEY_ENTER, 10, 13) and tabs:
            focused = manager.focus_tab(tabs[selected_index])
            if focused:
                message = "Focus command sent to WM."
            else:
                message = "Unable to focus window automatically."
            continue

    # We intentionally do not terminate running Alacritty instances here so that
    # users can keep their shells alive after closing Tabplexer.
