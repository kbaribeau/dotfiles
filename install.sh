#!/bin/bash
# All immediate package directories are installed together; Stow owns link lifecycle.
set -euo pipefail
usage() {
  echo 'Usage: install.sh [--home EXISTING_ABSOLUTE_DIRECTORY] [--dry-run] [--restow|--unstow]'
}
target=${HOME:?HOME is required}
action=--stow
options=(--no-folding --dotfiles --verbose)
while (($#)); do
  case "$1" in
    --home) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; target=$2; shift ;;
    --dry-run) options+=(--simulate) ;;
    --restow) action=--restow ;;
    --unstow) action=--delete ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
  shift
done
command -v stow >/dev/null || { echo 'GNU Stow is required; install it separately, then retry.' >&2; exit 1; }
[[ ! -L "$0" ]] || { echo 'Invoke install.sh directly, not through a script symlink.' >&2; exit 1; }
cd -- "$(dirname -- "$0")/packages"
packages_dir=$(pwd -P)
[[ "$target" = /* && -d "$target" && "$(cd -- "$target" && pwd -P)" != / ]] || {
  echo 'Target must be an existing absolute directory other than /.' >&2; exit 1;
}
# Stow reads these before explicit arguments; e.g. ambient --adopt is unsafe.
for config in "$HOME/.stowrc" "$packages_dir/.stowrc" "$HOME/.stow-global-ignore"; do
  [[ ! -e "$config" && ! -L "$config" ]] || {
    echo 'Ambient Stow configuration is unsupported; use a clean invocation HOME.' >&2; exit 1;
  }
done
packages=()
for package in */; do packages+=("${package%/}"); done
exec stow --dir="$packages_dir" --target="$target" "${options[@]}" "$action" "${packages[@]}"
