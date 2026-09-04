# Agent notes

Root-level files (`.zshrc`, `.gitconfig`, `bin/`, …) are meant to land in `$HOME` by symlink. There is no install or stow script. `vim/` is the exception: `vim/.vimrc` and `vim/.vim` map to `~/.vimrc` and `~/.vim`.

`.config/treehouse/` is the first XDG path in this repo. Do not symlink all of `~/.config`; only the `treehouse` directory (a merge does not update the live copy). After pull: `ln -snf /path/to/this/repo/.config/treehouse ~/.config/treehouse` (move an existing real directory aside first).

Treehouse `post_create` is user-level only. The registered hook is `.config/treehouse/post-create.sh`, which runs `hooks/<origin-basename>-post-create.sh` when that file is executable and otherwise exits 0. Per-project scripts under `hooks/` are local-only and gitignored. Add one on a machine as `~/.config/treehouse/hooks/<origin-basename>-post-create.sh` (executable); do not commit it. A fresh clone still has the `hooks/` path via the tracked gitignore there.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
