"""Load an Omarchy ``colors.toml`` (the single source of truth for a theme's colors)."""
from __future__ import annotations

import tomllib
from pathlib import Path

RGB = tuple[int, int, int]

# Keys the wallpapers, mock-up and Termux colors rely on. Omarchy themes share this schema, so any
# theme's colors.toml works; a missing key is reported up front instead of mid-render. The palette
# card shows whatever keys exist, so display-only keys (orange, lighter_background, ...) are optional.
REQUIRED = (
    "background", "darker_background", "selection", "muted", "accent",
    "foreground", "bright_foreground", "dark_foreground",
    "red", "yellow", "green", "cyan", "blue", "magenta",
    "bright_red", "bright_yellow", "bright_green", "bright_cyan", "bright_blue", "bright_magenta",
)


def hex_to_rgb(value: str) -> RGB:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"expected #rrggbb, got {value!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


class Palette(dict[str, RGB]):
    """name -> (r, g, b), 0-255."""

    name: str = ""

    def hex(self, key: str) -> str:
        return rgb_to_hex(self[key])


def load_palette(path: str | Path) -> Palette:
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    palette = Palette()
    palette.name = path.resolve().parent.name
    for key, value in raw.items():
        if isinstance(value, str) and value.startswith("#"):
            palette[key] = hex_to_rgb(value)
    missing = [k for k in REQUIRED if k not in palette]
    if missing:
        raise KeyError(f"{path} is missing colors: {', '.join(missing)}")
    return palette
