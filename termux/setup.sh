#!/data/data/com.termux/files/usr/bin/bash
# Omarchy "Tokyo Night" for Termux: colors, JetBrainsMono Nerd Font, tmux, starship and shell aliases.
#
#   bash ~/Omatheme/termux/setup.sh                install (safe to re-run)
#   bash ~/Omatheme/termux/setup.sh --nvim         also install Neovim with the tokyonight-night colorscheme
#   bash ~/Omatheme/termux/setup.sh --uninstall    undo: remove what it installed and put your own files back
#   bash ~/Omatheme/termux/setup.sh --export-font  save the font to Downloads/Omatheme, for widget and launcher apps
#
# Before replacing a file it copies it to ~/.omatheme-backup/<timestamp>/<same path>. What was there before the
# very first install is also kept in ~/.omatheme-backup/original/ and is what --uninstall puts back.
set -euo pipefail

FONT_URL="https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/JetBrainsMonoNerdFontMono-Regular.ttf"
FONT_NAME="JetBrainsMonoNerdFontMono-Regular.ttf"
PACKAGES=(tmux starship eza zoxide fzf bat git curl)
MARK_BEGIN="# >>> omatheme (Omarchy Tokyo Night) >>>"
MARK_END="# <<< omatheme <<<"
STORAGE_WAIT="${OMATHEME_STORAGE_WAIT:-30}" # seconds to wait for Android's storage permission dialog

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# starship only reads ~/.config/starship.toml and Omarchy's tmux reload key hard-codes ~/.config/tmux,
# so ~/.config is used even if $XDG_CONFIG_HOME points elsewhere.
config_home="$HOME/.config"
backup_root="$HOME/.omatheme-backup"
backup_dir="$backup_root/$(date +%Y%m%d-%H%M%S)"
orig_dir="$backup_root/original"
rc="$HOME/.bashrc"
font_dst="$HOME/.termux/font.ttf"
font_sum="$config_home/omatheme/font.sha256" # identifies the font this script installed

mode=install
with_nvim=0
for arg in "$@"; do
  case "$arg" in
    --nvim) with_nvim=1 ;;
    --uninstall) mode=uninstall ;;
    --export-font) mode=export-font ;;
    -h | --help) awk 'NR > 1 && /^#/ { print; next } NR > 1 { exit }' "${BASH_SOURCE[0]}"; exit 0 ;;
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

# ---------------------------------------------------------------- backups

rel() { printf '%s' "${1#"$HOME"/}"; }

backup_file() { # copy an existing file into this run's backup folder, keeping its path under $HOME
  local src="$1" dest
  [[ -e "$src" ]] || return 0
  dest="$backup_dir/$(rel "$src")"
  mkdir -p "$(dirname "$dest")"
  cp -p "$src" "$dest"
  say "backed up $src -> $dest"
}

remember_original() { # the first time a path is touched, keep what was there (or note that nothing was)
  local orig
  orig="$orig_dir/$(rel "$1")"
  [[ -e "$orig" || -e "$orig.absent" ]] && return 0
  mkdir -p "$(dirname "$orig")"
  if [[ -e "$1" ]]; then cp -p "$1" "$orig"; else : > "$orig.absent"; fi
}

install_file() { # src dst
  local src="$1" dst="$2"
  remember_original "$dst"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then backup_file "$dst"; fi
  install -m 0644 "$src" "$dst"
}

restore_original() { # put back what was at dst before the first install, or remove dst if nothing was
  local dst="$1" orig
  orig="$orig_dir/$(rel "$dst")"
  if [[ -e "$orig" ]]; then
    mkdir -p "$(dirname "$dst")"
    mv -f "$orig" "$dst"
    say "restored your original $dst"
  elif [[ -e "$dst" ]]; then
    rm -f "$dst"
    say "removed $dst"
  fi
  rm -f "$orig.absent"
}

uninstall_file() { # ours dst: undo one installed file, unless it was changed after install
  local ours="$1" dst="$2" orig
  orig="$orig_dir/$(rel "$dst")"
  if [[ -e "$dst" ]] && cmp -s "$ours" "$dst"; then
    restore_original "$dst"
  elif [[ -e "$orig" || -e "$orig.absent" ]]; then # installed by us, then changed or deleted
    if [[ -e "$dst" ]]; then
      local note=""
      [[ -e "$orig" ]] && note="; your original is $orig"
      warn "kept $dst: it changed since install$note"
    else
      restore_original "$dst"
    fi
  fi
}

# ---------------------------------------------------------------- ~/.bashrc block

block_state() { # none | ok | broken
  [[ -f "$rc" ]] || { echo none; return 0; }
  local begins ends
  begins="$(grep -cxF -- "$MARK_BEGIN" "$rc" || true)"
  ends="$(grep -cxF -- "$MARK_END" "$rc" || true)"
  if [[ "$begins" == 0 && "$ends" == 0 ]]; then
    echo none
  elif [[ "$begins" == 1 && "$ends" == 1 ]] \
    && (($(grep -nxF -- "$MARK_BEGIN" "$rc" | cut -d: -f1) < $(grep -nxF -- "$MARK_END" "$rc" | cut -d: -f1))); then
    echo ok
  else
    echo broken
  fi
}

check_bashrc() {
  [[ "$(block_state)" != broken ]] && return 0
  warn "$rc has an unmatched or repeated omatheme marker line. Fix or delete the lines"
  warn "  $MARK_BEGIN"
  warn "  $MARK_END"
  warn "by hand, then run this again. Nothing was changed."
  return 1
}

strip_bashrc_block() { # drop our marked block (and the blank line before it), after backing up .bashrc
  check_bashrc || return 1
  [[ "$(block_state)" == ok ]] || return 0
  backup_file "$rc"
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

# ---------------------------------------------------------------- font

download_font() { # dest: fetch the Nerd Font and check it really is a TrueType file
  local dest="$1"
  curl -fL --retry 3 --connect-timeout 20 -o "$dest" "$FONT_URL" \
    && [[ "$(stat -c %s "$dest")" -gt 1000000 ]] \
    && [[ "$(head -c 4 "$dest" | od -An -tx1 | tr -d ' \n')" == "00010000" ]]
}

font_is_ours() {
  [[ -e "$font_dst" && -e "$font_sum" ]] \
    && [[ "$(sha256sum "$font_dst" | cut -d' ' -f1)" == "$(cat "$font_sum")" ]]
}

export_font() { # download a fresh, verified copy into Downloads/Omatheme
  local downloads="$HOME/storage/downloads" waited=0 tmp
  if [[ ! -d "$downloads" ]]; then
    say "Asking Android for storage access: tap Allow in the dialog"
    termux-setup-storage || true
    while [[ ! -d "$downloads" && $waited -lt $STORAGE_WAIT ]]; do
      sleep 1
      waited=$((waited + 1))
    done
  fi
  if [[ ! -d "$downloads" ]]; then
    warn "No storage access yet. Allow it (termux-setup-storage), then run this again."
    return 1
  fi
  say "Downloading $FONT_NAME (about 2.5 MB)"
  tmp="$(mktemp)"
  if ! download_font "$tmp"; then
    rm -f "$tmp"
    warn "Font download failed or is not a TrueType file."
    return 1
  fi
  mkdir -p "$downloads/Omatheme"
  cp -f "$tmp" "$downloads/Omatheme/$FONT_NAME"
  rm -f "$tmp"
  say "Saved Downloads/Omatheme/$FONT_NAME (in My Files: Downloads > Omatheme)"
}

reload() {
  if command -v termux-reload-settings &>/dev/null; then termux-reload-settings || true; fi
}

# ---------------------------------------------------------------- modes

if [[ "$mode" == export-font ]]; then
  export_font || exit 1
  exit 0
fi

if [[ "$mode" == uninstall ]]; then
  say "Removing the shell hook from $rc"
  strip_bashrc_block || exit 1
  for name in "${!FILES[@]}"; do
    uninstall_file "$here/$name" "${FILES[$name]}"
  done
  uninstall_file "$here/nvim-init.lua" "$NVIM_DST"
  if font_is_ours; then
    restore_original "$font_dst"
  elif [[ -e "$font_sum" && -e "$font_dst" ]]; then
    warn "kept $font_dst: it changed since install"
  fi
  rm -f "$font_sum"
  reload
  say "Done. Timestamped backups stay in $backup_root (delete it when you no longer need them)."
  exit 0
fi

check_bashrc || exit 1

say "Installing packages: ${PACKAGES[*]}"
pkg install -y "${PACKAGES[@]}" # also refreshes the package lists
if ((with_nvim)); then pkg install -y neovim; fi

say "Downloading JetBrainsMono Nerd Font Mono (about 2.5 MB)"
font_tmp="$(mktemp)"
if download_font "$font_tmp"; then
  install_file "$font_tmp" "$font_dst"
  mkdir -p "$(dirname "$font_sum")"
  sha256sum "$font_dst" | cut -d' ' -f1 > "$font_sum"
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
