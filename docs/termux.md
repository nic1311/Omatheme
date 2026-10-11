# Termux kit

Gives you a terminal that looks like Omarchy's: Tokyo Night colors, **JetBrainsMono Nerd Font Mono**
(Omarchy's terminal font family), a steady block cursor, and Omarchy's own tmux, starship prompt and
shell aliases. It is also where "tiles" work for real: tmux panes.

## Install

1. Install **Termux** from Google Play (Termux publishes a separate Play build:
   <https://play.google.com/store/apps/details?id=com.termux>). Open it once.
2. In Termux:

   ```sh
   pkg install -y git
   git clone https://github.com/nic1311/Omatheme
   cd Omatheme
   bash termux/setup.sh            # add --nvim for Neovim with tokyonight-night
   ```

3. Close and reopen Termux, then type `t` to start tmux.

If a command is missing or crashes after the install, run `pkg upgrade` once (Termux does not support
partially upgraded installs) and run the script again. It is safe to re-run.

## What the script changes

| File on the phone | From | Notes |
|---|---|---|
| `~/.termux/colors.properties` | `termux/colors.properties` | Omarchy's palette, same slot mapping as its Alacritty template |
| `~/.termux/font.ttf` | downloaded | `JetBrainsMonoNerdFontMono-Regular.ttf` from the Nerd Fonts repo (about 2.5 MB), checked to be a TrueType file before use |
| `~/.termux/termux.properties` | `termux/termux.properties` | block cursor, margins, and a **PFX** key (Ctrl+Space) in the extra-keys row |
| `~/.config/tmux/tmux.conf` | `termux/tmux.conf` | Omarchy's, minus one Omarchy-only binding |
| `~/.config/starship.toml` | `termux/starship.toml` | Omarchy's, with three arrow glyphs swapped for ones the font has |
| `~/.config/omatheme/omarchy.sh` | `termux/omarchy.sh` | aliases (`ls`, `lt`, `ff`, `t`, git), zoxide, fzf, starship; sourced from a marked block in `~/.bashrc` |
| `~/.config/nvim/init.lua` | `termux/nvim-init.lua` | only with `--nvim` |

Packages installed: tmux, starship, eza, zoxide, fzf, bat, git, curl (plus neovim with `--nvim`).
Anything it overwrites is first copied to `~/.omatheme-backup/<timestamp>/`.

**Undo:** `bash termux/setup.sh --uninstall` removes the `.bashrc` block and every file that is still
identical to what it installed. It leaves `~/.termux/font.ttf` (delete it to return to the default font)
and the backups.

## Using it

- `t` attaches to (or creates) the tmux session `Work`, as on Omarchy.
- tmux prefix is **Ctrl+Space**; the **PFX** key in Termux's extra-keys row sends it in one tap.
  After the prefix: `h` split top/bottom, `v` split left/right, `x` close pane, `c` new window,
  `n`/`p` next/previous window. Mouse is on, so tapping a pane focuses it.
- Omarchy's Alt-based shortcuts (Alt+Enter to split, Alt+1..9 for windows) need a hardware keyboard.

## Tiling next to another app

Open Termux, then Recents → tap Termux's icon → **Open in split screen view** → pick a browser, chat or
notes app. Terminal in one tile, any app in the other, tmux panes inside the terminal tile.

## Not included

- **btop**: Omarchy's screenshots show it, but I found no `btop` recipe in the Termux package repo.
- **Hyprland, Waybar, Walker, Mako**: desktop Wayland tools; not applicable on Android.
