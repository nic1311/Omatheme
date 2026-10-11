#!/usr/bin/env python3
"""Regenerate every theme asset from an Omarchy colors.toml.

    python tools/generate.py                       # Tokyo Night, everything
    python tools/generate.py --only wallpapers     # or: palette, termux, frames, mockup, preview
    python tools/generate.py --scene dusk          # just one wallpaper (dusk, city, lock, solid)
    python tools/generate.py --theme path/to/colors.toml

Tokyo Night (the kit's theme) is written into the repo itself: wallpapers/, assets/, termux/colors.properties,
docs/preview.jpg and docs/kwgt-mockup.png. Any other theme goes to build/<theme>/ with the same layout, so it
can never overwrite the kit; --out picks another folder.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw  # noqa: E402

from omatheme.palette import load_palette  # noqa: E402
from omatheme.scenes import SCENES, _font, kwgt_mockup, palette_card, tile_frame  # noqa: E402
from omatheme.termux_kit import colors_properties  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KIT_THEME = "tokyo-night"
WALLPAPER_SCENES = ("dusk", "city", "lock", "solid")


def shown(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True, compress_level=9)
    print(f"  {shown(path)}  {img.width}x{img.height}  {path.stat().st_size / 1e6:.1f} MB")


def make_preview(paths: list[Path], out: Path, height: int = 900) -> None:
    """Side-by-side, captioned contact sheet of the wallpapers for the README."""
    tiles = []
    for path in paths:
        im = Image.open(path).convert("RGB")
        scaled = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
        tiles.append((path.stem.split("-")[-1], scaled))
    gap, caption_h = 24, 56
    bg = (14, 14, 20)
    sheet_w = sum(t.width for _, t in tiles) + gap * (len(tiles) + 1)
    sheet = Image.new("RGB", (sheet_w, height + 2 * gap + caption_h), bg)
    draw = ImageDraw.Draw(sheet)
    font = _font("Regular", 28)
    x = gap
    for label, tile in tiles:
        sheet.paste(tile, (x, gap))
        width = draw.textlength(label, font=font)
        draw.text((x + (tile.width - width) / 2, gap + height + 12), label, font=font, fill=(169, 177, 214))
        x += tile.width + gap
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88, optimize=True)
    print(f"  {shown(out)}  {sheet.width}x{sheet.height}  {out.stat().st_size / 1e3:.0f} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--theme", default=str(ROOT / "themes" / KIT_THEME / "colors.toml"))
    parser.add_argument("--only", choices=("wallpapers", "palette", "termux", "frames", "mockup", "preview"))
    parser.add_argument("--scene", choices=WALLPAPER_SCENES, action="append",
                        help="render only this wallpaper (repeatable); implies --only wallpapers")
    parser.add_argument("--out", help="output folder (default: the repo for Tokyo Night, build/<theme>/ otherwise)")
    args = parser.parse_args()
    if args.scene:
        args.only = "wallpapers"

    palette = load_palette(args.theme)
    name = palette.name
    out = Path(args.out) if args.out else ROOT if name == KIT_THEME else ROOT / "build" / name
    if out != ROOT:
        print(f"writing to {shown(out)}/")
    want = lambda part: args.only in (None, part)  # noqa: E731
    wallpapers = [out / "wallpapers" / f"{name}-{scene}.png" for scene in WALLPAPER_SCENES]
    rendered: dict[str, Image.Image] = {}

    if want("wallpapers"):
        print("wallpapers")
        for scene, path in zip(WALLPAPER_SCENES, wallpapers):
            if args.scene is None or scene in args.scene:
                rendered[scene] = SCENES[scene](palette)
                save_png(rendered[scene], path)
    if want("palette"):
        print("palette card")
        save_png(palette_card(palette), out / "assets" / f"{name}-palette.png")
    if want("frames"):
        print("theme park icon plates (experimental)")
        save_png(tile_frame(palette, focused=False), out / "assets" / "theme-park" / f"{name}-tile.png")
        save_png(tile_frame(palette, focused=True), out / "assets" / "theme-park" / f"{name}-tile-focused.png")
    if want("mockup"):
        print("kwgt mock-up")
        save_png(kwgt_mockup(palette, background=rendered.get("dusk")), out / "docs" / "kwgt-mockup.png")
    if want("termux"):
        path = out / "termux" / "colors.properties"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(colors_properties(palette), encoding="utf-8")
        print(f"termux\n  {shown(path)}")
    if want("preview") and all(p.exists() for p in wallpapers):
        print("preview")
        make_preview(wallpapers, out / "docs" / "preview.jpg")


if __name__ == "__main__":
    main()
