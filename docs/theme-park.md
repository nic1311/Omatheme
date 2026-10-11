# Theme Park recipe (Good Lock, from Galaxy Store)

Theme Park is Samsung's own theme maker: a Good Lock module you install from Galaxy Store, so no APK.
It builds a palette from your wallpaper, lets you override colors by hand, and restyles the Quick
Panel, volume panel, keyboard and icons ([SamMobile](https://www.sammobile.com/news/update-good-lock-theme-park-six-new-features/),
[Sammy Fans](https://www.sammyfans.com/2025/12/15/samsung-theme-park-features-skyrocket-in-one-ui-8-5/)).

**Before you start:** after the One UI 9 update, open Good Lock → Apps → **Update All**. Samsung advises this
because some modules need new builds
([Sammy Fans](https://www.sammyfans.com/2026/10/08/samsung-advises-you-to-update-good-lock-modules-on-one-ui-9/)).

**Which modules work on One UI 9:** Theme Park and Keys Cafe were on Samsung's One UI 9 compatibility list from
the start; MultiStar was added in June
([Sammy Fans](https://www.sammyfans.com/2026/06/11/samsung-one-ui-9-multistar-good-lock-modules/)). Samsung's
first list ([SamMobile](https://www.sammobile.com/news/samsung-reveals-which-good-lock-modules-work-with-one-ui-9-0/),
[Android Authority](https://www.androidauthority.com/one-ui-9-good-lock-compatibility-3668756/)) had ClockFace,
LockStar, NavStar and QuickStar still in progress; later reports say several of them gained support, and I
found no confirmation for QuickStar. Good Lock's own module list is the authority.

**One UI 9 redesigned the Quick Panel** (thicker sliders, tiles without borders, more of it editable natively,
per One UI 9 coverage such as [BGR](https://www.bgr.com/2278465/samsung-phone-new-features-one-ui-9/)), so
Theme Park's Quick Panel options may not match the table below exactly. Match by function.

## About these values

Omarchy's `colors.toml` defines *roles* (background, accent, selection, ...), not phone UI slots. Mapping
them onto Theme Park's slots is a design choice made here, following how Omarchy uses each role: windows
are `background`, the focused border is `accent`, selected rows are `selection`, dim text is `muted`.
Theme Park's labels change between versions, so match by function. `assets/tokyo-night-palette.png` shows
every value on the phone.

## Quick Panel (Create new → Quick Panel)

| Part | Value | Role in Omarchy |
|---|---|---|
| Panel background | `#1a1b26` | `background` (window fill) |
| Inactive toggle | `#24283b` | `lighter_background` |
| Inactive icon | `#a9b1d6` | `foreground` |
| Active toggle | `#7aa2f7` | `accent` (focused window border) |
| Active icon | `#1a1b26` | `background`, for contrast on the accent |
| Slider / brightness fill | `#7aa2f7` | `accent` |
| Slider track | `#414868` | `muted` |
| Blur / transparency | low blur, little transparency | Omarchy windows are flat and near-opaque (taste call) |

## Icons (Create new → Icons)

| Part | Value | Why |
|---|---|---|
| Monochrome (One UI 8.5+) | on, `#ad8ee6` | Omarchy's Tokyo Night uses the `Yaru-magenta` icon theme (`themes/tokyo-night/icons.theme`); `#ad8ee6` is the theme's `magenta`. Use `#a9b1d6` for a neutral look. |
| Icon label color | `#a9b1d6` | `foreground` |
| Effects (emboss, shadow, gradient) | none | Omarchy is flat |
| Shape | the squarest option | Omarchy's windows have square corners |
| Home badge color (One UI 8.5+) | `#7aa2f7` | `accent`: Omarchy's red is a terminal color (errors), not part of the desktop look |

## Keyboard and volume panel

Theme Park applies the palette to the Samsung Keyboard and the volume panel too. If it offers per-element
colors: background `#1a1b26`, keys `#24283b`, key text `#a9b1d6`, accent/enter key `#7aa2f7` with
`#1a1b26` text, slider `#7aa2f7`.

## Experimental: square "tile" icon plates

`assets/theme-park/tokyo-night-tile.png` and `tokyo-night-tile-focused.png` (512x512: navy fill, thin
square border in `muted` / `accent`) imitate Hyprland's inactive and focused windows.

A Samsung Community thread reports that Theme Park's Shape options accept a square image from the
gallery, which is the only way to get truly square icons
([thread](https://us.community.samsung.com/t5/Galaxy-S23/Is-It-Possible-to-Have-Truly-Square-Icons-With-Good-Lock-Theme/td-p/3380530)).
**Not verified:** how Theme Park uses a custom shape image (as a mask, or as a visible plate), and
whether the current version still offers it. Try it on one app first; if the image only acts as a mask,
the plate's colors won't show, but you still get square corners.
