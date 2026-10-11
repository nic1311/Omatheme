# Limits, and what was verified

_Research current as of 2026-10-11. Samsung changes these things often._

## What this kit can't do

### A system-wide monospace font

- Samsung's March 2026 security patch (CVE-2026-20989: Font Settings now verifies signatures) blocks
  non-root custom fonts on One UI 8.0 with that patch or later, and on all One UI 8.5 builds
  ([SamMobile](https://www.sammobile.com/news/samsung-closes-loophole-that-allowed-unauthorized-third-party-apps-add-fonts-to-one-ui/),
  [CVE record](https://stack.watch/vuln/CVE-2026-20989)). I found no coding font in Galaxy Store.
- A workaround is reported for One UI 8 and 9: zFont 3.9.2.3, an experimental APK distributed outside the
  Play Store, and an open-source tool
  ([Sammy Fans](https://www.sammyfans.com/2026/09/11/zfont-restores-custom-font-support-on-one-ui-8-and-9/),
  [AndroidSage](https://www.androidsage.com/2026/09/22/how-to-install-custom-fonts-on-samsung-one-ui-9/)).
  It needs an APK install, depends on a loophole Samsung can close again, and the two write-ups disagree on
  how it works. Left out on purpose, since only store apps are allowed.
- Substitute: Termux, where the font is entirely yours.

### Tiled app windows

- Samsung split screen is two apps (plus a pop-up window, but not both at once); One UI 8 lets you drag the
  split to 90/10
  ([Droid-Life](https://www.droid-life.com/2025/05/28/samsung-upgrades-split-screen-in-one-ui-8-update/)).
  I found no official figure for a larger limit on the S25. On One UI 9 the swipe gestures for split screen and
  pop-up view are reportedly off by default
  ([SamMobile](https://www.sammobile.com/news/must-try-multitasking-gestures-galaxy-z-fold-8-ultra/), a Z Fold 8
  guide).
- Hyprland-style tiling managers for Android exist but ship as APKs: for example
  [android-tiling-wm](https://github.com/Aypex/android-tiling-wm), a proof of concept tested on one Pixel
  that warns about small phone screens, and [DroidOS](https://github.com/aloim/droidos), aimed at
  external displays. Both need Shizuku and developer-option changes.
- Samsung DeX gives real windows, but on an external display: Samsung lists standalone DeX for tablets and
  the Z TriFold, not the S25 ([Samsung](https://www.samsung.com/us/support/answer/ANS10001955/)).
- Substitute: tmux panes inside Termux.

### A Waybar-style top bar

One UI does not let you rearrange the status bar by itself. Good Lock's QuickStar can hide status icons and,
per a third-party guide, move the clock to the right
([Guiding Tech](https://www.guidingtech.com/change-status-bar-clock-position-on-samsung-phone/)); I found no
centered-clock option, which is what Omarchy's bar has, and I could not confirm QuickStar's status on One UI 9.
Not attempted.

## Verified (in a cloud sandbox, 2026-10-11)

- Palette bytes match Omarchy's repo (`themes/tokyo-night/colors.toml`, fetched with curl).
- Omarchy's font and cursor settings were read from its Alacritty and Ghostty configs.
- JetBrainsMono Nerd Font Mono: every advance is 600 units (monospace); it has `❯`, Powerline and Nerd
  icons; it lacks `⇡ ⇣ ⇕`, which `termux/starship.toml` replaces.
- Termux package recipes exist for tmux, starship, eza, zoxide, fzf, bat, git, neovim and fastfetch
  (not btop), at current versions (tmux 3.8, neovim 0.12).
- `termux.properties` keys, and the `~/.termux/colors.properties` and `~/.termux/font.ttf` paths, match
  termux-app's source, including the `{macro: ...}` extra-keys syntax.
- `termux/tmux.conf` loads in a real tmux (3.4 here). The only rejected option is `extended-keys-format`,
  added in tmux 3.5; Termux ships 3.8.
- `termux/setup.sh`: shellcheck-clean; install, re-run, backup, uninstall and guard behavior tested in a
  throwaway home directory with a stubbed `pkg` and the real font download.
- Wallpapers (`tools/verify.py`): exact 1440x3120, white-text contrast over typical icon-grid, dock and
  status-bar zones, and Material You seed extraction (a proxy; see below).

## Not verified

- **Anything on a physical S25.** Samsung menu paths and labels, Theme Park's controls (hex entry,
  custom shape images), how Termux's Play build behaves, and how the font and colors actually render.
- **One UI's own Color palette algorithm** is closed. `verify.py` runs Google's Material algorithm on each
  wallpaper as a stand-in; every wallpaper yields at least one seed near Tokyo Night's blue/violet/navy,
  but One UI's picker may offer different swatches.
- **Zone positions** (icon grid 12-78% of the height, dock below 88%) are typical One UI home layouts, not
  measurements of yours.
- **The square-plate trick** for Theme Park icons (see [theme-park.md](theme-park.md)).
