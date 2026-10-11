#!/data/data/com.termux/files/usr/bin/bash
# Omarchy "Tokyo Night" for Termux: colors, JetBrainsMono Nerd Font, tmux, starship and shell aliases.
#
#   bash termux/setup.sh              install (safe to re-run)
#   bash termux/setup.sh --nvim       also install Neovim with the tokyonight-night colorscheme
#   bash termux/setup.sh --uninstall  remove what this script installed
#   bash termux/setup.sh --export-font  copy the font to Downloads/Omatheme, for widget and launcher apps
#
# Existing files are backed up to ~/.omatheme-backup/<timestamp>/ before being replaced.
set -euo pipefail

FONT_URL="https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/JetBrainsMonoNerdFontMono-Regular.ttf"
PACKAGES=(tmux starship eza zoxide fzf bat git curl)
MARK_BEGIN="# >>> omatheme (Omarchy Tokyo Night) >>>"
MARK_END="# <<< omatheme <<<"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
backup_dir="$HOME/.omatheme-backup/$(date +%Y%m%d-%H%M%S)"
rc="$HOME/.bashrc"

with_nvim=0
uninstall=0
export_font=0
for arg in "$@"; do
  case "$arg" in
    --nvim) with_nvim=1 ;;
    --uninstall) uninstall=1 ;;
    --export-font) export_font=1 ;;
    -h | --help) sed -n '2,9p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*" >&2; }

if [[ "${PREFIX:-}" != *com.termux* ]]; then
  warn "This script is meant to run inside Termux (from Google Play / F-Droid). \$PREFIX is '${PREFIX:-unset}'."
  exit 1
fi

# repo file (relative to termux/) -> where it lives on the phone
declare -A FILES=(
  ["colors.properties"]="$HOME/.termux/colors.properties"
  ["termux.properties"]="$HOME/.termux/termux.properties"
  ["tmux.conf"]="$config_home/tmux/tmux.conf"
  ["starship.toml"]="$config_home/starship.toml"
  ["omarchy.sh"]="$config_home/omatheme/omarchy.sh"
)
NVIM_DST="$config_home/nvim/init.lua"

install_file() { # src dst
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    mkdir -p "$backup_dir"
    cp -p "$dst" "$backup_dir/$(printf '%s' "$dst" | tr '/' '_')"
    say "backed up $dst -> $backup_dir"
  fi
  install -m 0644 "$src" "$dst"
}

strip_bashrc_block() { # drop our marked block, plus the blank line we put in front of it
  [[ -f "$rc" ]] || return 0
  local tmp
  tmp="$(mktemp)"
  awk -v b="$MARK_BEGIN" -v e="$MARK_END" '
    $0 == b { skip = 1; held = 0; next }
    $0 == e { skip = 0; next }
    skip { next }
    { if (held) { print ""; held = 0 }
      if ($0 == "") { held = 1; next }
      print }
    END { if (held) print "" }' "$rc" > "$tmp"
  cat "$tmp" > "$rc"
  rm -f "$tmp"
}

reload() {
  if command -v termux-reload-settings &>/dev/null; then termux-reload-settings || true; fi
}

STORAGE_WAIT="${OMATHEME_STORAGE_WAIT:-30}" # seconds to wait for Android's storage permission dialog

export_font_to_downloads() { # copy the installed font where launcher and widget apps can pick it
  local font="$HOME/.termux/font.ttf" downloads="$HOME/storage/downloads" waited=0
  local dest="$downloads/Omatheme/JetBrainsMonoNerdFontMono-Regular.ttf"
  if [[ ! -f "$font" ]]; then
    warn "No font at $font yet. Run: bash termux/setup.sh"
    return 1
  fi
  if [[ ! -d "$downloads" ]]; then
    say "Asking Android for storage access: tap Allow in the dialog"
    termux-setup-storage || true
    while [[ ! -d "$downloads" && $waited -lt $STORAGE_WAIT ]]; do
      sleep 1
      waited=$((waited + 1))
    done
  fi
  if [[ ! -d "$downloads" ]]; then
    warn "No storage access yet. Allow it (termux-setup-storage), then run: bash termux/setup.sh --export-font"
    return 1
  fi
  mkdir -p "$(dirname "$dest")"
  cp -f "$font" "$dest"
  say "Copied the font to Downloads/Omatheme/ (in My Files: Downloads > Omatheme)"
}

if ((export_font)); then
  export_font_to_downloads || exit 1
  exit 0
fi

if ((uninstall)); then
  say "Removing the shell hook from $rc"
  strip_bashrc_block
  for name in "${!FILES[@]}"; do
    dst="${FILES[$name]}"
    if [[ -e "$dst" ]] && cmp -s "$here/$name" "$dst"; then
      rm -f "$dst"
      say "removed $dst"
    fi
  done
  if [[ -e "$NVIM_DST" ]] && cmp -s "$here/nvim-init.lua" "$NVIM_DST"; then rm -f "$NVIM_DST"; say "removed $NVIM_DST"; fi
  reload
  say "Done. Kept ~/.termux/font.ttf (delete it to go back to the default font), any backups in ~/.omatheme-backup, and Downloads/Omatheme if you exported the font."
  exit 0
fi

say "Installing packages: ${PACKAGES[*]}"
pkg install -y "${PACKAGES[@]}" # also refreshes the package lists
if ((with_nvim)); then pkg install -y neovim; fi

say "Downloading JetBrainsMono Nerd Font Mono (about 2.5 MB)"
font_tmp="$(mktemp)"
if curl -fL --retry 3 --connect-timeout 20 -o "$font_tmp" "$FONT_URL" \
  && [[ "$(stat -c %s "$font_tmp")" -gt 1000000 ]] \
  && [[ "$(head -c 4 "$font_tmp" | od -An -tx1 | tr -d ' \n')" == "00010000" ]]; then
  install_file "$font_tmp" "$HOME/.termux/font.ttf"
else
  warn "Font download failed or is not a TrueType file; keeping your current font."
fi
rm -f "$font_tmp"

say "Installing Tokyo Night colors, tmux, starship and shell config"
for name in "${!FILES[@]}"; do
  install_file "$here/$name" "${FILES[$name]}"
done
if ((with_nvim)); then install_file "$here/nvim-init.lua" "$NVIM_DST"; fi

hook="$config_home/omatheme/omarchy.sh"
strip_bashrc_block
{
  printf '\n%s\n' "$MARK_BEGIN"
  printf '[ -f "%s" ] && . "%s"\n' "$hook" "$hook"
  printf '%s\n' "$MARK_END"
} >> "$rc"

reload
say "Done. Close and reopen Termux (or run: exec bash). Start tmux with: t"
