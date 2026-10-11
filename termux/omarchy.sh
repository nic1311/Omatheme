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
command -v nvim &>/dev/null && export EDITOR="${EDITOR:-nvim}"

# Prompt, directory jumping and fuzzy finder (interactive shells only)
if [[ $- == *i* ]] && [[ ${TERM:-} != "dumb" ]]; then
  command -v starship &>/dev/null && eval "$(starship init bash --print-full-init)"
  command -v zoxide &>/dev/null && eval "$(zoxide init bash)"
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
alias eff='$EDITOR "$(ff)"'

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
