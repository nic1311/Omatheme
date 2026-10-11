# Omarchy → Galaxy S25

How each part of Omarchy's Tokyo Night look maps onto the phone. ✅ matched · ◐ approximated · ❌ not possible.
Omarchy files are in <https://github.com/basecamp/omarchy> (master, read on 2026-10-11).

| Omarchy | Where it comes from | On the S25 | |
|---|---|---|---|
| Palette: `#1a1b26` background, `#a9b1d6` text, `#7aa2f7` accent, ... | `themes/tokyo-night/colors.toml` | exact hex values in Theme Park, Termux and the wallpapers | ✅ |
| Terminal colors (ANSI black = background, white = foreground, bright black = muted) | `default/themed/alacritty.toml.tpl` | `termux/colors.properties`, same slot mapping | ✅ |
| Font: JetBrainsMono Nerd Font, size 9 | `config/alacritty/alacritty.toml`, `config/ghostty/config` | Termux, using the Nerd Font **Mono** variant (fixed cell grid); KWGT widgets can use the same file | ✅ in Termux · ◐ in KWGT widgets · ❌ system-wide |
| Steady block cursor | `config/ghostty/config` | `termux.properties` | ✅ |
| 14 px terminal padding, no window decorations | `config/alacritty/alacritty.toml` | Termux margins (8 dp / 4 dp) | ◐ |
| tmux: top status bar, blue accents, pane borders | `config/tmux/tmux.conf` | `termux/tmux.conf` (verbatim minus one Omarchy-only binding) | ✅ |
| Starship prompt | `config/starship.toml` | `termux/starship.toml` (3 glyphs swapped) | ✅ |
| Shell aliases (`ls` via eza, `t`, git) | `default/bash/aliases` | `termux/omarchy.sh` (subset) | ✅ |
| Neovim `tokyonight-night` | `themes/tokyo-night/neovim.lua` | `termux/nvim-init.lua` with `--nvim` | ✅ |
| Wallpapers: pink-violet dusk landscape, neon cityscape, flat navy | `themes/tokyo-night/backgrounds/` | four original wallpapers in the same flat, layered style; Omarchy's own images are third-party works and are not copied | ◐ |
| Lock screen: flat `#1a1b26`, neon `#ffbfff` glow, `#a9b1d6` text | `preview-unlock.png`, `shell.lock.toml` | `tokyo-night-lock.png` (a glowing shell prompt) | ◐ |
| Icons: `Yaru-magenta` | `themes/tokyo-night/icons.theme` | Theme Park monochrome `#ad8ee6`, or One UI's palette on app icons | ◐ |
| Square windows with a thin focused border | `preview.png` | tmux pane borders; KWGT tiles on the home screen ([kwgt.md](kwgt.md)); experimental Theme Park icon plates | ◐ |
| Tiled windows | `preview.png` | Samsung split screen (two apps); tmux panes | ◐ |
| Search-driven app launcher | n/a (not mapped to a file) | Samsung Finder, which One UI 9 lets you place above the dock | ◐ |
| Top bar (workspace numbers, centered clock, tray) | `preview.png` | a KWGT widget on the home screen ([kwgt.md](kwgt.md)); the real status bar can't be restyled ([limits](limits.md)) | ◐ |
| btop | `default/themed/btop.theme.tpl` | no btop recipe in the Termux repo | ❌ |
| Keyboard backlight `ff00ff` | `themes/tokyo-night/keyboard.rgb` | no equivalent | ❌ |
