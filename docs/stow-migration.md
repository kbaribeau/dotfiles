# Stow migration: decision record and live switch plan

Scope: https://github.com/kbaribeau/dotfiles/issues/22. This change only moves
sources in an isolated worker clone. It does **not** authorize live installation,
reconciliation, source relocation in the primary checkout, or dependency installation.

## Responsibility and simplification

| Responsibility | Owner |
| --- | --- |
| Inventory, traversal, destination layout | Immediate `packages/` application trees |
| Planning, conflicts, links, repeat/restow/unstow | GNU Stow |
| Simulation and verbose diagnostics | GNU Stow |
| Prerequisite, clone location, target, compatibility flags | Thin `install.sh` |
| Shared skills and RSpec fan-out | Seven tracked relative aliases; canonical content only |
| Unsafe ambient Stow settings | Wrapper refuses rc/global-ignore files |
| Legacy links/private data relocation and rollback | Separately authorized operator procedure below |

The 228-line link engine and 25-line manifest are replaced by a 36-line
wrapper, with no helper engine, generated trees or second operational inventory.
Package selection is simply every immediate directory. No generated aliases or
per-file mapping code are needed. The six personal-skill directory aliases point
outside the Stow tree to existing canonical `skills/` directories: the optional
Codex probe did not discover individually symlinked SKILL.md files. This small
tracked layout preserves discovery without folding shared roots or adding a helper. The wrapper retains only argument translation,
an actionable prerequisite error, stable clone-relative execution, an existing
non-root target check, refusal of script symlink invocation and ambient config.
The latter prevents ambient destructive flags that Stow itself permits; the
former avoids retaining a symlink-chain resolver. See README for accepted Stow
behavior differences rather than an exact emulation of the old safety contract.

The installer suite shrinks from 533 to 296 lines of real-Stow integration tests;
application and discovery tests remain. There is one package/private-file
policy, no local Stow ignore files and no dependency bootstrap. The former dual-use
Git ignore file is intentionally split into home policy and repository policy.
Moving source files does not change application configuration contents.

## Disposable evidence

Initial bounded GNU Stow 2.4.1 experiments used two packages together, physical
paths with spaces and real target directories. Fresh/repeat/simulate/restow/delete,
`--no-folding` and tracked relative aliases worked. A real file, wrong or dangling
link, equivalent absolute link and foreign symlinked `.config` conflicted without
installing the other package. An existing relative owned link worked. Package
integration additionally covers all applications, all three personal-skill roots,
canonical reference reads, unrelated skills/settings and target-only runtime data.
Stow leaves some empty directories on deletion; deliberately no custom cleanup.
The initial skill file-link prototype was rejected based on real Codex discovery;
all three tools now receive per-skill directory aliases instead.

Validation on macOS: `bash -n install.sh`, `shellcheck install.sh`, and
`git diff --check` passed. `python3 -B -m unittest discover -s tests -v` ran 29
tests: 23 passed, six network/plugin opt-ins skipped. The isolated Codex probe
passed with codex-cli 0.153.4: both canonical user skills discovered, references
readable, disabled setting and unrelated managed skill preserved; no model turn
or skill invocation. Reproduce with the commands in README. Network/plugin-install suites remain opt-in and are
not required to install dependencies for this migration. The existing external
Neovim theme selection is stubbed along with plugin loading in offline fixtures;
application files are unchanged, and these tests do not establish theme readiness.

## Separately authorized live migration

Do not run this procedure automatically. Keep the primary `~/projects/dotfiles`
checkout and the managed task clone separate. A temporary worker checkout is not
a durable installation source. In particular, **do not pull these source moves
into a clone currently serving home links before inventory/backup**.

1. Obtain authorization for the specific target home, durable installing clone,
   affected destinations and backup location. Ensure GNU Stow is already available.
   Quiesce editors/config writers for the switch; do not drive unrelated services.
2. Before source moves, inventory each currently installed destination privately:
   entry type, exact `readlink` spelling, resolved source clone and source revision.
   Include all old manifest destinations at the pre-migration revision. Record which
   directories are real versus links, and inventory dirty tracked **and ignored**
   files in the source clones. Do not put this inventory in Git, logs or the PR.
3. Make a verified private backup outside both source and target trees. Preserve
   original links **as links**, permissions and dirty/ignored source data; retain
   a usable old source tree at the paths those links resolve through. A clean Git
   clone or commit alone is not a backup. Verify restoration on a disposable home
   before proceeding. Do not copy private contents into this repository or fixtures.
4. Prepare the new public package clone at its durable path independently. Review
   package trees for untracked/ignored files (Stow would consider them). Compare the
   full Stow preview with the private inventory; ordinary old absolute links will
   conflict. Approval to preview is not approval to reconcile those destinations.
5. With explicit reconciliation approval, back up/move **only individually reviewed
   affected entries** out of the way; do not recursively delete shared roots.
   For old whole-directory links, replace the affected subdirectory with a real
   directory and transfer only the inventoried private/runtime contents there:
   Neovim `local.lua`, Treehouse local hooks, Vim local plugins/state. Do not copy
   old tracked config files into the target where they would conflict with Stow.
   Preserve unrelated real contents and tool settings in place. Resolve same-name
   personal skill conflicts explicitly, never overwrite an operator's skill.
6. Run `./install.sh --home /absolute/approved-home --dry-run` against the complete
   package set. Stop on any unexpected plan/conflict. Once that exact plan is
   approved, apply, rerun dry-run, check aliases and references through each tool,
   and verify editor startup and private hook locations without invoking hooks.
   No `--adopt`, overrides, blanket deletion or forced ownership is part of this plan.

## Rollback (also requires approval)

Keep both old and new source clones plus the private inventory/backups until the
trial is accepted. Before rollback, preserve new target-side private/runtime edits.
Preview `--unstow --dry-run` using the **same new clone and target**, then unstow.
It removes its owned links, not unrelated data, and may leave empty directories.
Reconcile only the inventoried affected subdirectories: preserve their private
contents, remove only reviewed empty directories if necessary, restore original
entries/link text and old source locations from backup. Restore or reconcile
private data to its recorded old locations, retaining post-switch edits too.
Verify original link resolution, settings and editor startup. If sources were moved
in place despite the recommended separate-clone procedure, restore that source
layout **before** restoring links. A Git revert alone does not repair home links.

`test_legacy_switch_and_rollback` rehearses the procedure with synthetic old links,
dirty source content, target-only data, link-preserving backups, preview/conflict,
Stow installation and restoration. It is evidence for the sequence, not a live
inventory or a generic migration program.
