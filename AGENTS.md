# Agent notes

`install.sh` and `install/links.tsv` own the complete link inventory; see `README.md` for usage, safety limits, and fixture-only validation commands. Sources come from the resolved script's clone. Never run an apply against the real home without explicit authorization; conflicts require separate reconciliation.

Link shared configuration/skill directories only at the manifest's individual subdirectories, never all of `~/.config` or any tool's skills root. Personal skills carry canonical supporting documents under their own `references/`; see `skills/README.md` for discovery/coexistence details and `README.md` for the skill ownership policy.

Treehouse `post_create` is user-level only. The registered hook is `.config/treehouse/post-create.sh`, which runs `hooks/<origin-basename>-post-create.sh` when that file is executable and otherwise exits 0. Per-project scripts under `hooks/` are local-only and gitignored. Add one on a machine as `~/.config/treehouse/hooks/<origin-basename>-post-create.sh` (executable); do not commit it. A fresh clone still has the `hooks/` path via the tracked gitignore there.

## Confidentiality policy

Treat identifying or descriptive non-public project information as secrets. Never commit or push it in configuration, comments, paths, URLs, examples, tests, filenames, commit messages, or PR descriptions. This includes names, repository locations, customer identities, internal domains, architecture, and operational details.

Verified open-source references are permitted, including Firstmate, no-mistakes, and Treehouse, but not associated private deployments, credentials, or unpublished details. When public status is uncertain, omit it and ask. Use generic placeholders and ignored machine-local configuration instead.

For local overrides, prefer tracked config that loads optional private files and commit only sanitized templates or pointers to the authoritative public config. Ignore rules do not protect files that are already tracked; remove or sanitize tracked content before relying on `.gitignore`.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
