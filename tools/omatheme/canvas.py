"""A float32 linear-light canvas with vector masks, blur/glow and dithered export."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from .color import gradient, lin, linear_to_srgb

SS = 2  # supersampling factor for vector masks (anti-aliasing)


def _box_sizes(sigma: float, n: int = 3) -> list[int]:
    ideal = np.sqrt(12 * sigma * sigma / n + 1)
    lo = int(np.floor(ideal))
    lo -= 1 if lo % 2 == 0 else 0
    hi = lo + 2
    m = round((12 * sigma * sigma - n * lo * lo - 4 * n * lo - 3 * n) / (-4 * lo - 4))
    return [lo if i < m else hi for i in range(n)]


def _box_blur(a: np.ndarray, radius: int, axis: int) -> np.ndarray:
    if radius <= 0:
        return a
    a = np.moveaxis(a, axis, 0)
    n = a.shape[0]
    padded = np.concatenate([np.repeat(a[:1], radius, 0), a, np.repeat(a[-1:], radius, 0)], 0)
    csum = np.concatenate([np.zeros_like(padded[:1], dtype=np.float64),
                           np.cumsum(padded, axis=0, dtype=np.float64)], 0)
    out = (csum[2 * radius + 1:2 * radius + 1 + n] - csum[:n]) / (2 * radius + 1)
    return np.moveaxis(out.astype(np.float32), 0, axis)


def blur(a: np.ndarray, sigma: float, sigma_y: float | None = None) -> np.ndarray:
    """Gaussian blur (three box passes) over the first two axes of an (h, w[, c]) float array.

    ``sigma`` is horizontal; ``sigma_y`` (default: same) is vertical, for streaks.
    """
    sigma_y = sigma if sigma_y is None else sigma_y
    out = a.astype(np.float32, copy=False)
    for axis, s in ((0, sigma_y), (1, sigma)):
        if s <= 0.3:
            continue
        for size in _box_sizes(s):
            out = _box_blur(out, (size - 1) // 2, axis)
    return out


class Shapes:
    """Collect anti-aliased vector shapes into a single 0..1 coverage mask."""

    def __init__(self, w: int, h: int, ss: int = SS):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("L", (w * ss, h * ss), 0)
        self.draw = ImageDraw.Draw(self.img)

    def _s(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def polygon(self, pts, fill: int = 255):
        self.draw.polygon(self._s(pts), fill=fill)
        return self

    def rect(self, x0, y0, x1, y1, fill: int = 255):
        self.draw.rectangle(self._s([(x0, y0), (x1 - 1 / self.ss, y1 - 1 / self.ss)]), fill=fill)
        return self

    def ellipse(self, cx, cy, rx, ry=None, fill: int = 255):
        ry = rx if ry is None else ry
        self.draw.ellipse(self._s([(cx - rx, cy - ry), (cx + rx, cy + ry)]), fill=fill)
        return self

    def mask(self) -> np.ndarray:
        img = self.img if self.ss == 1 else self.img.resize((self.w, self.h), Image.BOX)
        return np.asarray(img, dtype=np.float32) / 255.0


class Canvas:
    """Linear-light float canvas. Colors passed in are '#rrggbb', (r, g, b) or linear arrays."""

    def __init__(self, w: int, h: int, color="#000000"):
        self.w, self.h = w, h
        self.px = np.empty((h, w, 3), np.float32)
        self.px[:] = self._c(color)

    @staticmethod
    def _c(color) -> np.ndarray:
        if isinstance(color, np.ndarray):
            return color.astype(np.float32, copy=False)
        return lin(color).astype(np.float32)

    def vgradient(self, stops) -> "Canvas":
        """Fill with a vertical gradient; stop positions are fractions of the height."""
        ys = (np.arange(self.h) + 0.5) / self.h
        self.px[:] = gradient(stops, ys).astype(np.float32)[:, None, :]
        return self

    def paint(self, color, mask: np.ndarray, opacity: float = 1.0) -> "Canvas":
        """Alpha-composite a flat color (or an (h, w, 3) linear array) through ``mask``."""
        a = (mask * opacity)[..., None]
        self.px *= 1.0 - a
        self.px += a * self._c(color)
        return self

    def add(self, color, mask: np.ndarray, gain: float = 1.0) -> "Canvas":
        """Add light (linear space) through ``mask``."""
        self.px += (mask * gain)[..., None] * self._c(color)
        return self

    def glow(self, mask: np.ndarray, color, sigma: float, gain: float) -> "Canvas":
        """Bloom: blur ``mask`` and add it as light."""
        return self.add(color, blur(mask, sigma), gain)

    def grid(self):
        """Pixel-center coordinate grids (x, y), each (h, w) float32."""
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        return xs + 0.5, ys + 0.5

    def to_image(self, seed: int = 0, dither: bool = True) -> Image.Image:
        """Quantize to 8-bit sRGB with triangular-PDF dither so dark gradients don't band on OLED."""
        rng = np.random.default_rng(seed)
        out = np.empty((self.h, self.w, 3), np.uint8)
        step = 256
        for y in range(0, self.h, step):
            rows = slice(y, min(y + step, self.h))
            srgb = linear_to_srgb(self.px[rows].astype(np.float64)) * 255.0
            if dither:
                n = rng.random((srgb.shape[0], self.w, 1)) + rng.random((srgb.shape[0], self.w, 1)) - 1.0
                srgb = srgb + n
            out[rows] = np.clip(np.rint(srgb), 0, 255).astype(np.uint8)
        return Image.fromarray(out, "RGB")
