#!/usr/bin/env python3
"""Check the generated wallpapers: size, Material You seed colors, and white-label legibility.

    pip install -r tools/requirements.txt materialyoucolor
    python tools/verify.py            # exits 1 if a hard check fails

Seed extraction follows Android's pipeline (downscale -> Celebi quantizer -> Material "Score") using the
Python port of Material Color Utilities. One UI's own palette code is closed, so the seeds are a proxy
for what the Color palette picker will offer, not a guarantee.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from omatheme.color import luminance, srgb_to_linear  # noqa: E402
from omatheme.palette import load_palette  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SIZE = (1440, 3120)  # 19.5:9, exactly 4/3 of the S25's 1080x2340 panel

# Vertical bands (fractions of height) where white text or icons usually sit.
HOME_ZONES = {"status bar": (0.0, 0.036), "icon grid": (0.12, 0.78), "dock": (0.88, 1.0)}
LOCK_ZONES = {"status bar": (0.0, 0.036), "clock + notifications": (0.04, 0.50)}
ZONES = {"dusk": HOME_ZONES, "city": HOME_ZONES, "solid": HOME_ZONES, "lock": LOCK_ZONES}

# Omarchy's Tokyo Night desktop is navy, blue, violet and pink; its shell uses red only for alerts and
# errors, and orange only in the terminal. A seed in this HCT hue band (with real chroma) would let One UI
# offer a red palette, so it fails. Pinks and magentas, such as Omarchy's own lock-screen glow #ff54d6
# (hue 343), stay below 350.
RED_HUES = (350.0, 50.0)  # wraps through 0
RED_MIN_CHROMA = 20.0

MAX_FRACTION_BELOW_3_TO_1 = 0.02  # at most 2% of a zone may fall under WCAG's 3:1 for large text/icons


# Android's WallpaperColors shrinks the bitmap to at most this many pixels (MAX_WALLPAPER_EXTRACTION_AREA,
# 112 x 112), keeping the aspect ratio, with Bitmap.createScaledBitmap(..., filter=false): nearest sampling.
EXTRACTION_AREA = 112 * 112


def seeds(img: Image.Image, n: int = 4):
    """Top-n Material seed colors as (argb, hue, chroma, tone), or None if the library is missing."""
    try:
        from materialyoucolor.hct import Hct
        from materialyoucolor.quantize import QuantizeCelebi
        from materialyoucolor.score.score import Score, ScoreOptions
    except ImportError:
        return None
    scale = min(1.0, (EXTRACTION_AREA / (img.width * img.height)) ** 0.5)
    small = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.NEAREST)
    quantized = QuantizeCelebi(np.asarray(small).reshape(-1, 3).tolist(), 128)
    out = []
    for argb in Score.score(quantized, ScoreOptions(desired=n)):
        hct = Hct.from_int(argb)
        out.append((argb, hct.hue, hct.chroma, hct.tone))
    return out


def hue_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def zone_stats(img: Image.Image, zones: dict[str, tuple[float, float]]):
    small = img.resize((img.width // 4, img.height // 4), Image.BOX)
    lum = luminance(srgb_to_linear(np.asarray(small, dtype=np.float64) / 255.0))
    contrast = 1.05 / (lum + 0.05)  # white (#fff, luminance 1.0) against the wallpaper
    h = contrast.shape[0]
    rows = {}
    for name, (a, b) in zones.items():
        c = contrast[int(a * h):int(b * h)]
        rows[name] = (float((c < 3.0).mean()), float((c < 4.5).mean()), float(np.percentile(c, 1)))
    return rows


def main() -> int:
    palette = load_palette(ROOT / "themes" / "tokyo-night" / "colors.toml")
    try:
        from materialyoucolor.hct import Hct
        anchors = {k: Hct.from_int(0xFF000000 | int(palette.hex(k)[1:], 16)).hue
                   for k in ("blue", "bright_magenta", "background")}
    except ImportError:
        anchors = {}

    failed = False
    paths = sorted((ROOT / "wallpapers").glob("tokyo-night-*.png"))
    if not paths:
        print("no wallpapers found; run tools/generate.py first")
        return 1
    for path in paths:
        scene = path.stem.split("-")[-1]
        img = Image.open(path)
        print(f"\n{path.name}")
        ok_size = img.size == EXPECTED_SIZE and img.mode == "RGB"
        verdict = "OK" if ok_size else "FAIL (expected 1440x3120 RGB)"
        print(f"  size      {img.size[0]}x{img.size[1]} {img.mode:4s} {verdict}")
        failed |= not ok_size
        img = img.convert("RGB")

        found = seeds(img)
        if found is None:
            print("  seeds     skipped (pip install materialyoucolor)")
        else:
            near = False
            for argb, hue, chroma, tone in found:
                gap = min((hue_gap(hue, a) for a in anchors.values()), default=999)
                near |= gap <= 30
                red = (hue >= RED_HUES[0] or hue <= RED_HUES[1]) and chroma >= RED_MIN_CHROMA
                failed |= red
                label = "FAIL: red/orange" if red else "near Tokyo Night" if gap <= 30 else ""
                print(f"  seed      #{argb & 0xFFFFFF:06x}  hue {hue:5.1f}  chroma {chroma:5.1f}  tone {tone:5.1f}"
                      f"   {label}")
            note = ("at least one seed within 30 deg of Tokyo Night blue/violet/navy" if near
                    else "WARN: no seed near Tokyo Night hues")
            print(f"  palette   {note}")

        for zone, (lt3, lt45, p1) in zone_stats(img, ZONES.get(scene, HOME_ZONES)).items():
            ok = lt3 <= MAX_FRACTION_BELOW_3_TO_1
            failed |= not ok
            print(f"  white on {zone:22s} <3:1 {lt3:6.1%}   <4.5:1 {lt45:6.1%}"
                  f"   worst 1% >= {p1:4.1f}:1  {'OK' if ok else 'FAIL'}")
    print("\n" + ("FAILED" if failed else "all hard checks passed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
