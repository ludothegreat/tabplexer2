# tabplexer2

A curses based tab wrapper for Alacritty. Tabplexer keeps track of multiple
Alacritty windows, making it easy to launch, rename, and close them from a
single dashboard.

## Features

- Launch new Alacritty windows with optional custom titles and commands.
- Rename existing windows directly from the dashboard.
- Send terminate signals to running windows and prune exited ones from the list.
- Optional focus support when the `wmctrl` utility is available.
- Clean separation between the process manager and the user interface for easy
  extension.

## Requirements

- Python 3.9+
- [Alacritty](https://github.com/alacritty/alacritty) available in your `PATH`.
- Optional: [`wmctrl`](https://www.freedesktop.org/wiki/Software/wmctrl/) if you
  want Tabplexer to attempt to focus windows when you press <kbd>Enter</kbd>.

## Installation

From the repository root:

```bash
pip install .
```

This will install a `tabplexer` entry point in your environment.

## Usage

## Quick start

1. Install the package into the same environment that contains
   [Alacritty](https://github.com/alacritty/alacritty):

   ```bash
   pip install .
   ```

   You can use `pip install -e .` during development to get live edits.

2. Launch the dashboard:

   ```bash
   tabplexer
   ```

   You can also run `python -m tabplexer` if you prefer not to install the
   console script.

When Tabplexer starts it immediately shows the dashboard. Press <kbd>n</kbd>
to open a fresh Alacritty window. You will be prompted (at the bottom of the
screen) for an optional title and command. Leave both prompts blank to launch
Alacritty with your default login shell. Supplying a command will execute it
through your shell (`$SHELL -lc <command>`), so you can start tools like
`htop` or `ssh user@host` directly.

Controls inside the curses UI:

| Key             | Description                                                   |
|-----------------|---------------------------------------------------------------|
| <kbd>↑</kbd>/<kbd>k</kbd> | Move selection up                                         |
| <kbd>↓</kbd>/<kbd>j</kbd> | Move selection down                                       |
| <kbd>Enter</kbd>  | Attempt to focus the selected window (requires `wmctrl`)      |
| <kbd>n</kbd>      | Create a new tab (prompts for optional title/command)        |
| <kbd>r</kbd>      | Rename the selected tab                                      |
| <kbd>c</kbd>      | Close the selected tab                                       |
| <kbd>x</kbd>      | Remove exited tabs from the list                             |
| <kbd>?</kbd> or <kbd>h</kbd> | Show built-in help screen                                 |
| <kbd>q</kbd> or <kbd>Esc</kbd> | Quit Tabplexer                                        |

If your system has `wmctrl` available, pressing <kbd>Enter</kbd> will hint to
your window manager to focus the selected window; otherwise the key shows a
message explaining that focus is unavailable.

Quitting Tabplexer leaves existing Alacritty windows running so they remain
available in your desktop environment.

## Developing

The code is intentionally split between a curses front-end and a process
manager back-end. You can re-use `tabplexer.manager.TabManager` to experiment
with other interfaces or automate complex workflows.
