"""Color math: sRGB <-> linear light, OKLab mixing and multi-stop gradients.

Gradients are interpolated in OKLab (no muddy mid-tones between purple and pink)
and glows are added in linear light (physically plausible bloom).
"""
from __future__ import annotations

import numpy as np

from .palette import hex_to_rgb

_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1_INV = np.linalg.inv(_M1)
_M2_INV = np.linalg.inv(_M2)


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lin(color) -> np.ndarray:
    """Normalize a color to linear-light float64 rgb.

    '#rrggbb' and (r, g, b) tuples are sRGB 0-255; a numpy array is taken to be linear
    already (so the results of mix()/tint() can be fed back in without double conversion).
    """
    if isinstance(color, np.ndarray):
        return color.astype(np.float64, copy=False)
    if isinstance(color, str):
        color = hex_to_rgb(color)
    return srgb_to_linear(np.asarray(color, dtype=np.float64) / 255.0)


def to_oklab(lin_rgb: np.ndarray) -> np.ndarray:
    return np.cbrt(np.asarray(lin_rgb) @ _M1.T) @ _M2.T


def from_oklab(lab: np.ndarray) -> np.ndarray:
    return ((np.asarray(lab) @ _M2_INV.T) ** 3) @ _M1_INV.T


def mix(a, b, t: float) -> np.ndarray:
    """Mix two colors in OKLab; returns linear-light rgb."""
    la, lb = to_oklab(lin(a)), to_oklab(lin(b))
    return from_oklab(la + (lb - la) * t)


def hue_of(color) -> float:
    """OKLCH hue of a color, in degrees."""
    _, a, b = to_oklab(lin(color))
    return float(np.degrees(np.arctan2(b, a)) % 360)


def tint(color, L: float | None = None, C: float | None = None, hue: float | None = None) -> np.ndarray:
    """Re-light a color in OKLCH: keep its hue (a palette identity), set lightness/chroma by design.

    Plain mixing with a near-grey navy washes colors out; this keeps vivid chroma at any lightness.
    Out-of-gamut results are clipped in linear space.
    """
    L0, a, b = to_oklab(lin(color))
    chroma, h = np.hypot(a, b), np.arctan2(b, a)
    L = L0 if L is None else L
    C = chroma if C is None else C
    h = h if hue is None else np.radians(hue)
    return np.clip(from_oklab(np.array([L, C * np.cos(h), C * np.sin(h)])), 0.0, 1.0)


def gradient(stops, t: np.ndarray) -> np.ndarray:
    """Evaluate ``[(position, color), ...]`` at positions ``t`` -> linear rgb, shape t.shape + (3,)."""
    pos = np.array([p for p, _ in stops], dtype=np.float64)
    labs = np.stack([to_oklab(lin(c)) for _, c in stops])
    flat = np.asarray(t, dtype=np.float64).ravel()
    out = np.stack([np.interp(flat, pos, labs[:, i]) for i in range(3)], axis=-1)
    return from_oklab(out).reshape(np.shape(t) + (3,))


def luminance(lin_rgb: np.ndarray) -> np.ndarray:
    """WCAG relative luminance of linear-light rgb (last axis = channels)."""
    return lin_rgb @ np.array([0.2126, 0.7152, 0.0722])
