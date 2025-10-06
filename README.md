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

After installation run:

```bash
tabplexer
```

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

Quitting Tabplexer leaves existing Alacritty windows running so they remain
available in your desktop environment.

## Developing

The code is intentionally split between a curses front-end and a process
manager back-end. You can re-use `tabplexer.manager.TabManager` to experiment
with other interfaces or automate complex workflows.
