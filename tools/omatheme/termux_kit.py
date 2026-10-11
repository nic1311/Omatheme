"""Termux color scheme from an Omarchy palette."""
from __future__ import annotations

from .palette import Palette

# Same slot mapping as Omarchy's alacritty template (default/themed/alacritty.toml.tpl):
# ANSI black = background, white = foreground, bright black = muted, bright white = bright_foreground.
ANSI = (
    ("color0", "background"), ("color1", "red"), ("color2", "green"), ("color3", "yellow"),
    ("color4", "blue"), ("color5", "magenta"), ("color6", "cyan"), ("color7", "foreground"),
    ("color8", "muted"), ("color9", "bright_red"), ("color10", "bright_green"), ("color11", "bright_yellow"),
    ("color12", "bright_blue"), ("color13", "bright_magenta"), ("color14", "bright_cyan"),
    ("color15", "bright_foreground"),
)


def colors_properties(p: Palette) -> str:
    """Contents for ~/.termux/colors.properties."""
    lines = [
        f"# {p.name} - generated from themes/{p.name}/colors.toml (Omarchy). Apply with: termux-reload-settings",
        f"foreground={p.hex('foreground')}",
        f"background={p.hex('background')}",
        f"cursor={p.hex('bright_foreground')}",
    ]
    lines += [f"{slot}={p.hex(name)}" for slot, name in ANSI]
    return "\n".join(lines) + "\n"
