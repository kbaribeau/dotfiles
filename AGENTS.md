# Agent notes

`packages/` is the GNU Stow inventory; `install.sh` only orchestrates it. See `README.md` for usage, target-only private/runtime policy and fixture validation. Never apply against the real home without explicit authorization; conflicts require separate reconciliation.

Keep shared `~/.config` and tool skills roots real; use Stow's no-folding policy and only per-skill aliases. Canonical personal skills stay in `skills/` with their own `references/`; see `skills/README.md` for discovery/coexistence and `README.md` for ownership policy.

Treehouse `post_create` is user-level only. The registered hook is `packages/treehouse/.config/treehouse/post-create.sh`, which runs `hooks/<origin-basename>-post-create.sh` when that file is executable and otherwise exits 0. Per-project scripts under `hooks/` are local-only and gitignored. Add one on a machine as `~/.config/treehouse/hooks/<origin-basename>-post-create.sh` (executable); do not commit it. A fresh clone still has the `hooks/` path via the tracked gitignore there.

## Confidentiality policy

Treat identifying or descriptive non-public project information as secrets. Never commit or push it in configuration, comments, paths, URLs, examples, tests, filenames, commit messages, or PR descriptions. This includes names, repository locations, customer identities, internal domains, architecture, and operational details.

Verified open-source references are permitted, including Firstmate, no-mistakes, and Treehouse, but not associated private deployments, credentials, or unpublished details. When public status is uncertain, omit it and ask. Use generic placeholders and ignored machine-local configuration instead.

For local overrides, prefer tracked config that loads optional private files and commit only sanitized templates or pointers to the authoritative public config. Ignore rules do not protect files that are already tracked; remove or sanitize tracked content before relying on `.gitignore`.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
