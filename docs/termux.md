# Termux kit

Gives you a terminal that looks like Omarchy's: Tokyo Night colors, **JetBrainsMono Nerd Font Mono**
(Omarchy's terminal font family), a steady block cursor, and Omarchy's own tmux, starship prompt and
shell aliases. If you want tiles, tmux panes give you them inside the terminal.

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
partially upgraded installs) and run `bash ~/Omatheme/termux/setup.sh` again. It is safe to re-run.
To pick up a newer version of this kit later: `git -C ~/Omatheme pull && bash ~/Omatheme/termux/setup.sh`.

## What the script changes

| File on the phone | From | Notes |
|---|---|---|
| `~/.termux/colors.properties` | `termux/colors.properties` | Omarchy's palette, same slot mapping as its Alacritty template |
| `~/.termux/font.ttf` | downloaded | `JetBrainsMonoNerdFontMono-Regular.ttf` from the Nerd Fonts repo (about 2.5 MB), checked to be a TrueType file before use |
| `~/.termux/termux.properties` | `termux/termux.properties` | block cursor, margins, and a **PFX** key (Ctrl+Space) in the extra-keys row |
| `~/.config/tmux/tmux.conf` | `termux/tmux.conf` | Omarchy's, minus one Omarchy-only binding |
| `~/.config/starship.toml` | `termux/starship.toml` | Omarchy's, with three arrow glyphs swapped for ones the font has (like upstream, the prompt leaves them out; the file's header says how to show them) |
| `~/.config/omatheme/omarchy.sh` | `termux/omarchy.sh` | aliases (`ls`, `lt`, `ff`, `eff`, `t`, git), zoxide, fzf, starship; sourced from a marked block in `~/.bashrc` |
| `~/.config/nvim/init.lua` | `termux/nvim-init.lua` | only with `--nvim` |

Packages installed: tmux, starship, eza, zoxide, fzf, bat, git, curl (plus neovim with `--nvim`).
The config goes in `~/.config` even if `$XDG_CONFIG_HOME` points elsewhere, because starship and the tmux
reload key (prefix, then `q`) only look there.

Before replacing a file, the script copies it to `~/.omatheme-backup/<timestamp>/` under the same path, for
example `~/.omatheme-backup/<timestamp>/.config/tmux/tmux.conf`. Whatever was there before the very first
install is also kept in `~/.omatheme-backup/original/`.

**Undo:** `bash ~/Omatheme/termux/setup.sh --uninstall` removes the `.bashrc` block, puts back the files you
had before the first install, and deletes the ones it created. The font goes back to yours, or to Termux's
default if you had none. A file you changed after installing is kept, and the script tells you where your
original is, if you had one. If the omatheme marker lines in `~/.bashrc` no longer form one begin/end pair,
install and uninstall both stop without changing anything and say which marker lines to fix. The backups
stay in `~/.omatheme-backup`; delete that folder when you no longer need them. Undo also works after a
`git pull` and over an install made by the kit's first version: files it installed are recognized from the
clone's git history, and your originals from that version's backups.

## Using it

- `t` attaches to (or creates) the tmux session `Work`, as on Omarchy.
- tmux prefix is **Ctrl+Space**; the **PFX** key in Termux's extra-keys row sends it in one tap.
  After the prefix: `h` split top/bottom, `v` split left/right, `x` close pane, `c` new window,
  `n`/`p` next/previous window. Mouse is on, so tapping a pane focuses it.
- Omarchy's Alt-based shortcuts (Alt+Enter to split, Alt+1..9 for windows) need a hardware keyboard.
- `ff` finds a file with a bat preview; `eff` opens the one you pick in `$EDITOR`: yours if set, otherwise
  the first of nvim, vim, nano and vi that is installed.

## Tiling next to another app (optional)

Open Termux, then Recents → tap Termux's icon → **Open in split screen view** → pick a browser, chat or
notes app. Terminal in one tile, any app in the other, tmux panes inside the terminal tile.

## Not included

- **btop**: Omarchy's screenshots show it, but Termux packages it only in its root repository
  (`root-packages/btop`), which holds "programs for rooted devices".
- **Hyprland and the Omarchy shell** (its bar, launcher and notifications): desktop Wayland software;
  not applicable on Android.
