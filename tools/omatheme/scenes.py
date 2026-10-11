"""Wallpaper scenes in the flat, layered style of Omarchy's Tokyo Night backgrounds.

Every scene returns a PIL image sized for the Galaxy S25 family (19.5:9). Colors are
derived from the Omarchy palette; the two neon values used for glows were measured
from Omarchy's own lock screen (themes/tokyo-night/preview-unlock.png).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .canvas import Canvas, Shapes, blur, blur_sparse
from .color import gradient, hue_lerp, hue_of, lin, tint
from .palette import Palette, rgb_to_hex

W, H = 1440, 3120  # 19.5:9, exact 4:3 of the S25's 1080x2340 panel; S25+/Ultra are native

# Measured from Omarchy's tokyo-night preview-unlock.png: logo fill and halo hue.
NEON = "#ffbfff"
NEON_GLOW = "#ff54d6"


# ---------------------------------------------------------------- helpers

def fbm1d(rng: np.random.Generator, n: int, cells: float = 5, octaves: int = 5,
          persistence: float = 0.5, ridged: bool = False) -> np.ndarray:
    """Smooth 1-D fractal noise in [0, 1], n samples. ``ridged`` gives sharper peaks."""
    x = np.linspace(0.0, 1.0, n)
    total, norm, amp, freq = np.zeros(n), 0.0, 1.0, cells
    for _ in range(octaves):
        ctrl = rng.random(int(np.ceil(freq)) + 2)
        xi = x * freq
        i0 = np.floor(xi).astype(int)
        f = xi - i0
        f = f * f * (3 - 2 * f)
        v = ctrl[i0] * (1 - f) + ctrl[i0 + 1] * f
        if ridged:
            v = 1 - np.abs(2 * v - 1)
        total += amp * v
        norm += amp
        amp *= persistence
        freq *= 2
    return total / norm


def ridge_polygon(ys: np.ndarray, w: int, h: int, step: int = 2):
    """Closed polygon under a ridge line sampled every ``step`` px."""
    pts = [(float(x), float(ys[x])) for x in range(0, w, step)] + [(float(w), float(ys[w - 1]))]
    return pts + [(float(w), h + 4.0), (0.0, h + 4.0)]


def pine(shapes: Shapes, rng: np.random.Generator, cx: float, base: float, height: float):
    """A stepped conifer silhouette."""
    tiers = int(rng.integers(5, 8))
    width = height * rng.uniform(0.26, 0.36)
    trunk = width * 0.07
    shapes.rect(cx - trunk, base - height * 0.10, cx + trunk, base + 6)
    top = base - height
    step = height * 0.86 / tiers
    for i in range(tiers):
        apex = top + i * step
        hw = width / 2 * (0.30 + 0.70 * (i + 1) / tiers) * rng.uniform(0.92, 1.08)
        bottom = min(apex + step * 2.1, base - height * 0.08)
        jitter = rng.uniform(-1.5, 1.5)
        shapes.polygon([(cx + jitter, apex), (cx + hw, bottom), (cx - hw, bottom)])


def stars(canvas: Canvas, rng: np.random.Generator, y_max: float, count: int,
          tint, big: int = 14):
    """Scatter 1-px stars plus a few soft, larger ones (light added in linear space)."""
    w, h = canvas.w, canvas.h
    xs = rng.random(count) * (w - 1)
    # denser toward the top of the sky
    ys = (rng.random(count) ** 1.6) * (y_max * h - 1)
    lum = rng.random(count) ** 3 * 0.9 + 0.08
    px = canvas.px
    col = lin(tint).astype(np.float32)
    for x, y, brightness in zip(xs.astype(int), ys.astype(int), lum):
        px[y, x] += col * brightness
    soft = Shapes(w, h)
    for i in rng.choice(count, size=min(big, count), replace=False):
        r = rng.uniform(1.6, 3.0)
        soft.ellipse(xs[i], ys[i], r)
    canvas.add(col, soft.mask(), 0.9)
    canvas.glow(soft.mask(), col, 7.0, 3.0)


# ---------------------------------------------------------------- scenes

def solid(p: Palette, w: int = W, h: int = H) -> Image.Image:
    """The terminal-black look: Omarchy's background color and nothing else."""
    return Canvas(w, h, p.hex("background")).to_image(dither=False)


def lock(p: Palette, w: int = W, h: int = H) -> Image.Image:
    """Navy field with a glowing prompt and block cursor, echoing Omarchy's unlock screen.

    Omarchy's lock screen is a flat #1a1b26 with a neon-pink glowing mark; here the mark
    is a shell prompt (chevron + block cursor, Omarchy's cursor style) so it stays original.
    """
    c = Canvas(w, h, p.hex("background"))
    cell_h = 520.0
    cell_w = cell_h * 0.6 / 1.32  # JetBrains Mono: 0.6em advance, 1.32em line height
    cx, cy = w / 2, h * 0.56
    x0 = cx - 1.5 * cell_w

    shape = Shapes(w, h)
    # block cursor in the third cell
    shape.rect(x0 + 2 * cell_w, cy - cell_h / 2, x0 + 3 * cell_w, cy + cell_h / 2)
    # chevron prompt in the first cell
    xl, xr = x0 + 0.12 * cell_w, x0 + 0.88 * cell_w
    yt, yb, tx = cy - 0.34 * cell_h, cy + 0.34 * cell_h, 0.56 * cell_w
    shape.polygon([(xl, yt), (xl + tx, yt), (xr, cy), (xl + tx, yb), (xl, yb), (xr - tx, cy)])
    mask = shape.mask()

    # halo profile fitted to the Omarchy unlock screen (~30% at the edge, gone by ~40px)
    c.glow(mask, NEON_GLOW, 15.0, 0.75)
    c.glow(mask, NEON_GLOW, 60.0, 0.20)
    c.glow(mask, NEON_GLOW, 220.0, 0.07)
    c.paint(NEON, mask)
    return c.to_image(seed=11)


def _pinks(p: Palette) -> tuple[float, float]:
    """Hues for the warm end of the sky: a soft pink and a hot pink, both between violet and red.

    The hot pink sits where Omarchy's own Tokyo Night pink does (its lock screen glow, #ff54d6, is about
    60% of the way from bright_magenta to bright_red), so the sunsets read pink and magenta, never red
    or orange: those palette colors are terminal colors, not part of the desktop look.
    """
    h_violet, h_red = hue_of(p["bright_magenta"]), hue_of(p["bright_red"])
    return hue_lerp(h_violet, h_red, 0.40), hue_lerp(h_violet, h_red, 0.60)


def dusk(p: Palette, w: int = W, h: int = H, seed: int = 7) -> Image.Image:
    """Layered ridges under a haloed setting sun, in the spirit of Omarchy's sunset backgrounds.

    Hues come from the palette (navy -> violet -> pink); lightness and chroma are set by design so
    the sky stays vivid yet dark enough for white app labels to stay readable.
    """
    rng = np.random.default_rng(seed)
    night, ink, violet = p["background"], p["darker_background"], p["bright_magenta"]
    h_night, h_violet = hue_of(night), hue_of(violet)
    h_pink, h_rose = _pinks(p)
    rose = tint(violet, hue=h_rose)

    # The bright band sits below the app grid (~80% of the screen) and above the dock, so white
    # labels keep their contrast; verify.py checks this.
    horizon = 0.835
    k = horizon / 0.765
    glow_rose = tint(rose, L=0.78, C=0.14)
    sky = [
        (0.00, tint(night, L=0.165, C=0.022)),
        (0.18 * k, tint(night, L=0.220, C=0.060, hue=h_night + 6)),
        (0.38 * k, tint(violet, L=0.300, C=0.115, hue=h_violet - 4)),
        (0.55 * k, tint(violet, L=0.400, C=0.160, hue=h_violet + 16)),
        (0.68 * k, tint(violet, L=0.520, C=0.185, hue=h_pink)),
        (0.74 * k, tint(rose, L=0.640, C=0.180)),
        (horizon, tint(rose, L=0.780, C=0.120)),
        (1.00, tint(rose, L=0.780, C=0.120)),
    ]
    c = Canvas(w, h).vgradient(sky)

    # stars in the upper sky
    stars(c, rng, 0.50, 260, tint(p["bright_foreground"], L=0.92, C=0.03))

    # setting sun with concentric halo rings (Omarchy's sunset-lake motif)
    sx, sy = w * 0.56, h * horizon - h * 0.010
    disc = Shapes(w, h).ellipse(sx, sy, w * 0.085).mask()
    c.glow(disc, glow_rose, 80.0, 1.0)
    c.glow(disc, glow_rose, 340.0, 0.8)
    ring_color = tint(rose, L=0.82, C=0.10)
    for radius, alpha in ((0.32, 0.045), (0.24, 0.065), (0.17, 0.095), (0.12, 0.14)):
        c.paint(ring_color, Shapes(w, h).ellipse(sx, sy, w * radius).mask(), alpha)
    c.paint(tint(rose, L=0.95, C=0.045), disc)

    # ridges: far -> near; each is a vertical gradient (lit crest, darker base)
    ys = np.arange(h) + 0.5
    layers = [
        # crest y, amplitude, ridged noise?, crest color, base color
        (0.845, 0.045, True,  tint(violet, L=0.47, C=0.130, hue=h_pink - 8), tint(violet, L=0.40, C=0.120)),
        (0.870, 0.040, True,  tint(violet, L=0.37, C=0.110), tint(violet, L=0.30, C=0.095)),
        (0.903, 0.028, False, tint(violet, L=0.285, C=0.088, hue=h_violet - 8), tint(night, L=0.215, C=0.060)),
        (0.937, 0.022, False, tint(night, L=0.190, C=0.040), tint(ink, L=0.150, C=0.020)),
    ]
    for i, (base, amp, ridged, top, bottom) in enumerate(layers):
        prof = fbm1d(rng, w, cells=3 + i, octaves=6, persistence=0.55, ridged=ridged)
        ridge = (base - amp * prof) * h
        mask = Shapes(w, h).polygon(ridge_polygon(ridge, w, h)).mask()
        t = np.clip((ys - ridge.min()) / (h - ridge.min()), 0, 1)
        color = gradient([(0.0, top), (1.0, bottom)], t).astype(np.float32)[:, None, :]
        c.paint(color, mask)
        if i == 3:  # foreground: conifers along the crest and framing both edges
            trees = Shapes(w, h)
            for x in rng.uniform(0, w, 70):
                pine(trees, rng, x, ridge[int(x)] + 14, rng.uniform(70, 150))
            for x, hgt in ((w * 0.05, 520), (w * 0.17, 330), (w * 0.93, 600), (w * 0.82, 380)):
                pine(trees, rng, x, ridge[int(x)] + 24, hgt)
            c.paint(tint(night, L=0.135, C=0.028), trees.mask())

    return c.to_image(seed=seed)


def city(p: Palette, w: int = W, h: int = H, seed: int = 21) -> Image.Image:
    """A neon skyline under a pink-clouded night sky: the 'Tokyo night' of the theme's name."""
    rng = np.random.default_rng(seed)
    night, ink = p["background"], p["darker_background"]
    violet, blue = p["bright_magenta"], p["blue"]
    h_night, h_violet = hue_of(night), hue_of(violet)
    h_pink, h_rose = _pinks(p)
    rose = tint(violet, hue=h_rose)

    sky = [
        (0.00, tint(night, L=0.160, C=0.022)),
        (0.30, tint(night, L=0.205, C=0.050, hue=h_night + 4)),
        (0.52, tint(violet, L=0.290, C=0.105, hue=h_violet - 6)),
        (0.64, tint(violet, L=0.410, C=0.150, hue=h_pink)),
        (0.74, tint(rose, L=0.560, C=0.170)),
        (1.00, tint(rose, L=0.560, C=0.170)),
    ]
    c = Canvas(w, h).vgradient(sky)
    ys = np.arange(h) + 0.5
    stars(c, rng, 0.36, 200, tint(p["bright_foreground"], L=0.92, C=0.03), big=8)

    # moon with a warm-to-cool shaded disc (as in Omarchy's cityscape background)
    mx, my, mr = w * 0.80, h * 0.115, w * 0.062
    moon = Shapes(w, h).ellipse(mx, my, mr).mask()
    c.glow(moon, tint(p["bright_foreground"], L=0.75, C=0.05), 40.0, 0.9)
    xs_, ys_ = c.grid()
    t = np.clip(((xs_ - mx) + (ys_ - my)) / (2 * mr) * 0.5 + 0.5, 0, 1)
    moon_color = gradient([(0.0, tint(p["yellow"], L=0.94, C=0.07)),
                           (0.55, tint(p["bright_foreground"], L=0.80, C=0.07)),
                           (1.0, tint(blue, L=0.40, C=0.14))], t).astype(np.float32)
    c.paint(moon_color, moon)

    # flat cumulus banks, lit from the upper left
    def cloud_bank(x0, x1, y_base, scale):
        s = Shapes(w, h)
        x = x0
        while x < x1:
            edge = min(x - x0, x1 - x) / max(x1 - x0, 1) * 2  # taper toward both ends
            r = rng.uniform(34, 92) * scale * (0.45 + 0.55 * min(edge * 2, 1))
            s.ellipse(x, y_base - r * 0.55 - rng.uniform(0, 26 * scale), r)
            x += r * rng.uniform(0.55, 0.9)
        m = s.mask()
        m[int(y_base):] = 0
        return m
    clouds = np.maximum(cloud_bank(-80, w * 0.47, h * 0.572, 1.0), cloud_bank(w * 0.55, w + 80, h * 0.572, 0.9))
    rim = np.clip(clouds - np.roll(np.roll(clouds, 14, axis=0), 8, axis=1), 0, 1)
    c.paint(tint(violet, L=0.455, C=0.150, hue=h_pink), blur(clouds, 0.7))
    c.paint(tint(violet, L=0.60, C=0.110, hue=h_pink + 8), blur(rim, 1.2), 0.85)

    # distant mountains
    prof = fbm1d(rng, w, cells=3, octaves=6, persistence=0.55, ridged=True)
    ridge = (0.700 - 0.040 * prof) * h
    mtn = Shapes(w, h).polygon(ridge_polygon(ridge, w, h)).mask()
    t = np.clip((ys - ridge.min()) / (h * 0.9 - ridge.min()), 0, 1)
    c.paint(gradient([(0.0, tint(blue, L=0.32, C=0.085)), (1.0, tint(night, L=0.20, C=0.05))], t)
            .astype(np.float32)[:, None, :], mtn)

    # horizon glow bleeding up behind the skyline
    band = np.zeros((h, w), np.float32)
    band[int(h * 0.70):int(h * 0.78)] = 1.0
    c.glow(band, tint(rose, L=0.62, C=0.17), 60.0, 0.35)

    # skyline: three depth layers of rectangular towers with lit windows
    ground = int(h * 0.905)
    lit_colors = [tint(p["yellow"], L=0.86, C=0.12), tint(p["yellow"], L=0.80, C=0.09),
                  tint(p["bright_cyan"], L=0.80, C=0.11), tint(rose, L=0.78, C=0.14),
                  tint(p["bright_foreground"], L=0.90, C=0.05)]
    lit_weights = np.array([0.42, 0.20, 0.16, 0.10, 0.12])
    emissive = np.zeros((h, w, 3), np.float32)
    layers = [  # width range, height range (frac of h), cell (w, h), lit prob range, body, window scale
        ((26, 60), (0.04, 0.095), (9, 13), (0.02, 0.07), tint(violet, L=0.295, C=0.075, hue=h_pink - 20), 0.40),
        ((44, 100), (0.055, 0.125), (12, 17), (0.05, 0.18), tint(night, L=0.215, C=0.050), 0.62),
        ((74, 170), (0.07, 0.15), (17, 25), (0.07, 0.24), tint(night, L=0.150, C=0.035), 0.85),
    ]
    near_signs = []
    rim_color = lin(tint(violet, L=0.36, C=0.10, hue=h_pink)).astype(np.float32)
    for li, (wr, hr, (cw, ch), (p0, p1), body, win_gain) in enumerate(layers):
        body_lin = lin(body).astype(np.float32)
        x = -int(rng.integers(0, 40))
        while x < w + 40:
            bw = int(rng.integers(*wr))
            bh = int(rng.uniform(*hr) * h * (1.0 + 0.7 * (rng.random() < 0.09)))  # a few skyscrapers
            top = ground - bh
            tiers = [(x, top, bw, ground)]  # x, top, width, bottom
            if rng.random() < 0.35:  # setback crown sitting on the base
                tiers.append((x + int(bw * 0.18), top - int(bh * 0.10), int(bw * 0.64), top))
            rims = [(tx, ty, tb) for tx, ty, _, tb in tiers]  # left edge of each tier catches the glow
            for tx, ty, tw, tb in tiers:
                x0, x1 = max(tx, 0), min(tx + tw, w)
                if x1 > x0:
                    c.px[max(ty, 0):tb, x0:x1] = body_lin
            if li == 2 and rng.random() < 0.30 and bw > 80:  # antenna with a pink aviation light
                ax, ah = x + bw // 2, int(rng.uniform(0.02, 0.05) * h)
                c.px[max(top - ah, 0):top, max(ax - 2, 0):ax + 2] = body_lin
                rims.append((ax - 2, top - ah, top))
                emissive[max(top - ah, 0):top - ah + 7, max(ax - 4, 0):ax + 4] = lin(tint(rose, L=0.74, C=0.19))
            if li == 2:  # rim light on the side facing the horizon glow
                for rx, ry, rb in rims:
                    x0, x1 = max(rx, 0), min(rx + 4, w)
                    if x1 > x0:
                        strip = c.px[max(ry, 0):rb, x0:x1]
                        strip *= 0.3
                        strip += 0.7 * rim_color
            # windows: each tier gets its own grid, limited to the tier's own height
            lit_p = rng.uniform(p0, p1)
            for tx, ty, tw, tb in tiers:
                cols, rows = (tw - 16) // cw, (tb - ty - 24) // ch
                for r in range(max(rows, 0)):
                    for q in range(max(cols, 0)):
                        if rng.random() < lit_p:
                            wx, wy = tx + 8 + q * cw + 3, ty + 12 + r * ch + 5
                            if 0 <= wx and wx + cw - 6 <= w:
                                col = lit_colors[int(rng.choice(len(lit_colors), p=lit_weights))]
                                emissive[wy:wy + ch - 10, wx:wx + cw - 6] = lin(col) * win_gain
            if li == 2 and bw > 90 and rng.random() < 0.16:
                near_signs.append((x + bw - 3, top + int(bh * rng.uniform(0.15, 0.5))))
            x += int(bw * (1 - rng.uniform(0.0, 0.18)))
        # paint this layer's windows now so nearer layers occlude them
        lit = (emissive.sum(axis=2) > 0).astype(np.float32)
        c.paint(emissive, lit)
        c.px += blur_sparse(emissive, 5.0) * (0.55 * win_gain)
        if li < 2:
            emissive[:] = 0

    # neon signs on a few near towers
    sign_mask = np.zeros((h, w), np.float32)
    sign_col = np.zeros((h, w, 3), np.float32)
    for k, (sx_, sy_) in enumerate(near_signs[:5]):
        sh = int(rng.uniform(110, 230))
        col = lin(tint(rose if k % 2 == 0 else p["bright_cyan"], L=0.80, C=0.17))
        sign_mask[sy_:sy_ + sh, sx_:sx_ + 12] = 1.0
        sign_col[sy_:sy_ + sh, sx_:sx_ + 12] = col
    c.paint(sign_col, sign_mask)
    c.px += blur_sparse(sign_col * sign_mask[..., None], 10.0) * 1.1
    emissive += sign_col * sign_mask[..., None]

    # wet street: dark ground plus streaky reflections of the near layer's lights
    street_t = np.clip((ys - ground) / (h - ground), 0, 1)
    street = gradient([(0.0, tint(night, L=0.17, C=0.035)), (1.0, tint(ink, L=0.14, C=0.015))], street_t)
    ground_mask = np.zeros((h, w), np.float32)
    ground_mask[ground:] = 1.0
    c.paint(street.astype(np.float32)[:, None, :], ground_mask)
    depth = h - ground
    src = ground - np.arange(1, depth + 1)
    refl = np.zeros((h, w, 3), np.float32)
    refl[ground:] = emissive[src.clip(0)]
    refl = blur_sparse(refl, 2.5, 16.0)
    fade = np.exp(-(ys - ground).clip(0) / 105.0).astype(np.float32)[:, None, None]
    c.px += refl * fade * 0.30 * ground_mask[..., None]

    return c.to_image(seed=seed)



FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / f"JetBrainsMono-{weight}.woff"), size)


def palette_card(p: Palette, w: int = 1080, h: int = 2340) -> Image.Image:
    """A phone-sized swatch sheet: compare it against One UI's color pickers.

    The desktop look (surfaces, text, accents) gets large tiles. The rest of the terminal palette
    (red, orange, yellow, green, brown) gets small ones under its own heading: Omarchy uses those for
    terminal output such as errors and git diffs, not for the look of the desktop. Every color appears
    once; keys that repeat another key's value (Tokyo Night's ``blue`` equals its ``accent``) are shown
    under the first name only.
    """
    pad, gap = 48, 14
    groups = [  # title, keys, columns, tile height, caption
        ("surfaces", ["background", "lighter_background", "dark_background", "darker_background",
                      "selection", "muted"], 2, 108, None),
        ("text", ["foreground", "bright_foreground", "light_foreground", "dark_foreground"], 2, 108, None),
        ("accents", ["accent", "blue", "bright_blue", "magenta", "bright_magenta", "cyan", "bright_cyan"],
         2, 108, None),
        ("terminal colors", ["red", "bright_red", "orange", "brown", "yellow", "bright_yellow", "green",
                             "bright_green"], 4, 76, "terminal output only (errors, git diffs), not the desktop look"),
    ]
    known = {k for _, ks, *_ in groups for k in ks}
    groups.append(("other", [k for k in p if k not in known], 4, 76, None))
    seen, shown = set(), []
    for title, keys, cols, tile_h, caption in groups:
        keep = []
        for key in keys:
            if key in p and p[key] not in seen:
                seen.add(p[key])
                keep.append(key)
        if keep:
            shown.append((title, keep, cols, tile_h, caption))

    def rows(keys, cols):
        return (len(keys) + cols - 1) // cols

    def height(keys, cols, tile_h, caption):
        return 52 + (40 if caption else 0) + rows(keys, cols) * (tile_h + gap) + 26

    needed = 220 + sum(height(*g[1:]) for g in shown) + pad
    img = Image.new("RGB", (w, max(h, needed)), p["background"])
    d = ImageDraw.Draw(img)
    d.text((pad, 70), p.name, font=_font("Bold", 64), fill=p["bright_foreground"])
    d.text((pad, 150), "Omarchy colors.toml", font=_font("Regular", 30), fill=p["dark_foreground"])

    y = 220
    for title, keys, cols, tile_h, caption in shown:
        d.text((pad, y), title, font=_font("Bold", 30), fill=p["foreground"])
        y += 52
        if caption:
            d.text((pad, y - 8), caption, font=_font("Regular", 24), fill=p["dark_foreground"])
            y += 40
        small = cols > 2
        tile_w = (w - 2 * pad - gap * (cols - 1)) // cols
        for i, key in enumerate(keys):
            x = pad + (i % cols) * (tile_w + gap)
            yy = y + (i // cols) * (tile_h + gap)
            fill = p[key]
            focused = key == "background"  # Hyprland-style: the focused tile gets the accent border
            d.rectangle([x, yy, x + tile_w - 1, yy + tile_h - 1], fill=fill,
                        outline=p["accent"] if focused else p["muted"], width=3)
            ink = max((p["background"], p["bright_foreground"]), key=lambda c: contrast(fill, c))
            if small:
                d.text((x + 14, yy + 9), key, font=_font("Regular", 19), fill=ink)
                d.text((x + 14, yy + 34), rgb_to_hex(fill), font=_font("Bold", 28), fill=ink)
            else:
                d.text((x + 20, yy + 12), key, font=_font("Regular", 26), fill=ink)
                d.text((x + 20, yy + 48), rgb_to_hex(fill), font=_font("Bold", 44), fill=ink)
        y += rows(keys, cols) * (tile_h + gap) + 26
    return img


def luminance_srgb(rgb) -> float:
    from .color import luminance, srgb_to_linear
    return float(luminance(srgb_to_linear(np.asarray(rgb, dtype=np.float64) / 255.0)))


def contrast(a, b) -> float:
    """WCAG contrast ratio between two sRGB colors."""
    hi, lo = sorted((luminance_srgb(a), luminance_srgb(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def tile_frame(p: Palette, focused: bool, size: int = 512) -> Image.Image:
    """Square, sharp-cornered icon plate in the look of a tiled window: navy fill, thin border.

    Experimental: for Good Lock > Theme Park's icon Shape picker, which can take a gallery image.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    border = p["accent"] if focused else p["muted"]
    d.rectangle([0, 0, size - 1, size - 1], fill=p["background"] + (255,))
    d.rectangle([0, 0, size - 1, size - 1], outline=border + (255,), width=max(2, size // 48))
    return img


def _chevron(d: ImageDraw.ImageDraw, x: float, y: float, height: float, fill) -> None:
    """A prompt chevron centered vertically on ``y`` (the font subset used here has no U+276F)."""
    t = height * 0.30
    d.polygon([(x, y - height / 2), (x + t, y - height / 2), (x + height * 0.62, y),
               (x + t, y + height / 2), (x, y + height / 2), (x + height * 0.32, y)], fill=fill)


def kwgt_mockup(p: Palette, w: int = 1080, h: int = 2340, background: Image.Image | None = None) -> Image.Image:
    """Mock-up (not a screenshot) of the home screen built in docs/kwgt.md: bar and tiles over `dusk`.

    Pass the rendered dusk wallpaper as ``background`` to avoid rendering it twice.
    """
    img = (dusk(p) if background is None else background).convert("RGB").resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    margin, bw = 36, 4
    left, right = margin, w - margin

    def tile(x0, y0, x1, y1, border):
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=p["background"], outline=border, width=bw)

    # top bar: workspace-style numbers, centered clock, battery (as in Omarchy's Waybar)
    d.rectangle([left, 132, right - 1, 211], fill=p["background"])
    num = _font("Bold", 34)
    d.text((left + 26, 172), "1", font=num, fill=p["accent"], anchor="lm")
    rest_x = left + 26 + d.textlength("1 ", font=num)
    d.text((rest_x, 172), "2 3 4 5", font=num, fill=p["dark_foreground"], anchor="lm")
    d.text((w / 2, 172), "Sat 20:25", font=_font("Bold", 38), fill=p["bright_foreground"], anchor="mm")
    d.text((right - 26, 172), "85%", font=num, fill=p["foreground"], anchor="rm")

    # focused tile: a prompt and the clock
    tile(left, 250, 540, 590, p["accent"])
    small, label = _font("Regular", 30), _font("Regular", 28)
    x = left + 26
    d.text((x, 296), "~", font=small, fill=p["accent"], anchor="lm")
    x += d.textlength("~ ", font=small)
    _chevron(d, x, 296, 26, p["bright_cyan"])
    d.text((x + 40, 296), "date", font=small, fill=p["foreground"], anchor="lm")
    d.text((left + 26, 410), "20:25", font=_font("Bold", 112), fill=p["bright_foreground"], anchor="lm")
    d.text((left + 26, 525), "Saturday 11 Oct", font=small, fill=p["foreground"], anchor="lm")

    # battery tile
    x0 = 564
    tile(x0, 250, right, 590, p["muted"])
    d.text((x0 + 26, 296), "bat", font=label, fill=p["dark_foreground"], anchor="lm")
    d.text((x0 + 26, 400), "85%", font=_font("Bold", 96), fill=p["green"], anchor="lm")
    track = (x0 + 26, 468, right - 26, 494)
    d.rectangle(track, fill=p["selection"])
    d.rectangle((track[0], track[1], track[0] + (track[2] - track[0]) * 0.85, track[3]), fill=p["green"])
    d.text((x0 + 26, 535), "discharging", font=label, fill=p["foreground"], anchor="lm")

    # palette tile
    tile(left, 614, right, 790, p["muted"])
    d.text((left + 26, 668), p.name, font=_font("Bold", 40), fill=p["bright_foreground"], anchor="lm")
    d.text((left + 26, 722), "omarchy colors", font=label, fill=p["dark_foreground"], anchor="lm")
    # the desktop look's colors; red, orange and the other terminal-only colors stay off the home screen
    swatches = ["accent", "magenta", "cyan", "bright_cyan", "muted", "bright_foreground"]
    size, gap = 52, 14
    sx = right - 26 - (len(swatches) * size + (len(swatches) - 1) * gap)
    for i, key in enumerate(swatches):
        d.rectangle([sx + i * (size + gap), 676, sx + i * (size + gap) + size - 1, 727], fill=p[key])

    note = _font("Regular", 24)
    caption = "mock-up, not a screenshot: app icons omitted"
    d.text((w / 2, h - 52), caption, font=note, fill=p["dark_foreground"], anchor="mm")
    return img


SCENES = {
    "solid": solid,
    "lock": lock,
    "dusk": dusk,
    "city": city,
}
