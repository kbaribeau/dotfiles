#!/bin/sh
# Treehouse post_create dispatcher: run a per-origin-repo hook if one exists.
set -eu
repo=$(basename -s .git "$(git remote get-url origin 2>/dev/null || echo unknown)")
h="$HOME/.config/treehouse/hooks/${repo}-post-create.sh"
[ -x "$h" ] || { echo "treehouse: no post-create hook for '$repo'; skipping" >&2; exit 0; }
exec "$h"
