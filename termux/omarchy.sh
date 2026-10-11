# shellcheck shell=bash
# Omarchy's shell feel, for Termux: prompt, aliases, fuzzy finder, directory jumping.
# Adapted from https://github.com/basecamp/omarchy  (default/bash/{aliases,envs,init,shell}; MIT, (c) David Heinemeier Hansson).
# Left out: the Omarchy-only helpers (omarchy-launch-*, agent/docker/rails aliases, mise, xdg-open).

# History control
shopt -s histappend
HISTCONTROL=ignoreboth
HISTSIZE=32768
HISTFILESIZE="${HISTSIZE}"

# Use the terminal's own (Tokyo Night) colors for bat instead of a fixed theme
export BAT_THEME=ansi

# Editor for `eff`: keep yours, otherwise the first one installed (Omarchy always sets one)
if [[ -z "${EDITOR:-}" ]]; then
  for candidate in nvim vim nano vi; do
    if command -v "$candidate" &>/dev/null; then
      export EDITOR="$candidate"
      break
    fi
  done
fi

# Directory jumping, set up unconditionally as upstream does: `cd` below relies on it
command -v zoxide &>/dev/null && eval "$(zoxide init bash)"

# Prompt and fuzzy finder (interactive shells on a real terminal only)
if [[ $- == *i* ]] && [[ ${TERM:-} != "dumb" ]]; then
  command -v starship &>/dev/null && eval "$(starship init bash --print-full-init)"
  command -v fzf &>/dev/null && eval "$(fzf --bash)"
fi

# File system
if command -v eza &>/dev/null; then
  alias ls='eza -lh --group-directories-first --icons=auto'
  alias lsa='ls -a'
  alias lt='eza --tree --level=2 --long --icons --git'
  alias lta='lt -a'
fi

alias ff="fzf --preview 'bat --style=numbers --color=always {}'"

# Open a fuzzy-found file in $EDITOR. A function, not upstream's alias: with no editor set, the alias
# would run the chosen file instead of opening it.
eff() {
  if [[ -z "${EDITOR:-}" ]]; then
    echo "eff: no editor found; set EDITOR or install one (bash ~/Omatheme/termux/setup.sh --nvim)" >&2
    return 1
  fi
  local file
  file="$(fzf --preview 'bat --style=numbers --color=always {}')" || return
  [[ -n "$file" ]] || return
  # shellcheck disable=SC2086  # EDITOR may carry arguments, as upstream's alias allows
  $EDITOR "$file"
}

if command -v zoxide &>/dev/null; then
  alias cd="zd"
  zd() {
    if (( $# == 0 )); then
      builtin cd ~ || return
    elif [[ -d $1 ]]; then
      builtin cd "$1" || return
    else
      if ! z "$@"; then
        echo "Error: Directory not found"
        return 1
      fi

      printf "\U000F17A9 "
      pwd
    fi
  }
fi

# Directories
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Tools: `t` attaches to (or starts) the tmux session, like on Omarchy
alias t='tmux attach || tmux new -s Work'
n() { if [ "$#" -eq 0 ]; then command nvim . ; else command nvim "$@"; fi; }

# Git
alias g='git'
alias gcm='git commit -m'
alias gcam='git commit -a -m'
alias gcad='git commit -a --amend'
