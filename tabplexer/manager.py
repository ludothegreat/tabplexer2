"""Process management for Tabplexer.

This module is intentionally free of any UI logic so that it can be reused
from other front-ends in the future (for example, a GUI written with Qt or a
web based dashboard).  All of the heavy lifting for launching, tracking and
stopping Alacritty instances lives here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
import shutil
import subprocess
import time
from typing import List, Optional


class AlacrittyNotFoundError(RuntimeError):
    """Raised when the Alacritty binary cannot be located."""


@dataclass
class Tab:
    """A running (or previously running) Alacritty window managed by Tabplexer."""

    identifier: int
    title: str
    command: Optional[str]
    cwd: str
    process: subprocess.Popen
    instance_class: str
    created_at: float = field(default_factory=time.time)
    exit_code: Optional[int] = None

    def is_running(self) -> bool:
        return self.process.poll() is None

    def refresh(self) -> None:
        if self.exit_code is None:
            result = self.process.poll()
            if result is not None:
                self.exit_code = result

    def terminate(self, timeout: float = 2.0) -> None:
        if self.process.poll() is not None:
            return
        try:
            self.process.terminate()
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=timeout)


class TabManager:
    """Launches and keeps track of Alacritty windows."""

    def __init__(self) -> None:
        self._tabs: List[Tab] = []
        self._next_id = 1
        self._alacritty_path = shutil.which("alacritty")
        if not self._alacritty_path:
            raise AlacrittyNotFoundError(
                "Unable to find the 'alacritty' executable in PATH."
            )
        self._wmctrl_path = shutil.which("wmctrl")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def tabs(self) -> List[Tab]:
        return list(self._tabs)

    @property
    def wmctrl_available(self) -> bool:
        return self._wmctrl_path is not None

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    def create_tab(
        self,
        *,
        title: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Tab:
        identifier = self._next_id
        self._next_id += 1

        if cwd is None:
            cwd = os.getcwd()

        instance_class = f"TabplexerTab{identifier}"
        args = [self._alacritty_path, "--class", f"{instance_class},Tabplexer"]
        if title:
            args += ["--title", title]
        if command:
            # Execute the command through the user's shell for convenience.
            shell = os.environ.get("SHELL", "bash")
            args += ["-e", shell, "-lc", command]

        process = subprocess.Popen(args, cwd=cwd)

        tab = Tab(
            identifier=identifier,
            title=title or f"Tab {identifier}",
            command=command,
            cwd=cwd,
            process=process,
            instance_class=instance_class,
        )
        self._tabs.append(tab)
        return tab

    def close_tab(self, tab: Tab) -> None:
        tab.terminate()

    def prune(self) -> None:
        """Remove tabs that have exited and have been acknowledged."""
        self._tabs = [tab for tab in self._tabs if tab.is_running() or tab.exit_code is None]

    def refresh(self) -> None:
        for tab in self._tabs:
            tab.refresh()

    def shutdown(self) -> None:
        for tab in self._tabs:
            tab.terminate()

    # ------------------------------------------------------------------
    # Focus handling
    # ------------------------------------------------------------------
    def focus_tab(self, tab: Tab) -> bool:
        """Attempt to focus the window for *tab*.

        Returns True if we were able to pass a focus hint to the window manager,
        False otherwise.
        """

        if not tab.is_running():
            return False
        if not self._wmctrl_path:
            return False

        try:
            subprocess.run(
                [self._wmctrl_path, "-x", "-a", tab.instance_class],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except OSError:
            return False
