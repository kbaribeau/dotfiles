# Dotfiles

Personal configuration and [self-contained reference skills](skills/README.md).

## Philosophy: skill ownership

Dotfiles owns the shared Codex, Cursor, and Claude Code framework and the personal
skills maintained in this repository. Each repository-owned skill has one canonical
source, linked individually into the tools' discovery directories.

**Third-party skills belong to the operator of each laptop.** The operator chooses,
installs, authenticates, updates, and removes them using their upstream guidance.
Dotfiles does not vendor third-party skills or acquire them through downloaders,
submodules, bootstrap commands, or manifest entries. It does not manage their
runtime dependencies, credentials, or optional hooks. A new laptop therefore needs
its own deliberate third-party skill setup; cloning dotfiles does not reproduce it.

Repository-owned and operator-managed skills must coexist: never take ownership of
an entire shared skills directory or overwrite user material. Unrelated skills and
settings stay untouched; colliding destinations require separate reconciliation.
See [skills/README.md](skills/README.md) for the installation layout, discovery
evidence, and verification. This policy concerns skills, not a change to the
separately documented editor/plugin dependencies below.

## GNU Stow installation

Requires **GNU Stow** (tested with 2.4.1) and Bash 3.2+. Install prerequisites
separately; this repository never bootstraps dependencies. [`packages/`](packages)
is the inventory: every immediate directory is one application/coherent package,
and all packages are passed to Stow together. No manifest or generated tree exists.
Herdr and other configuration outside that tree are not installed.

```sh
# Create a disposable target first; use absolute physical paths.
./install.sh --home /absolute/test-home --dry-run
./install.sh --home /absolute/test-home
./install.sh --home /absolute/test-home --restow --dry-run
./install.sh --home /absolute/test-home --restow
./install.sh --home /absolute/test-home --unstow --dry-run
./install.sh --home /absolute/test-home --unstow
# Omitting --home selects $HOME. Live apply requires separate authorization.
```

Run (do not source) the script directly from its clone; script symlink aliases are
not supported. Working directory does not select sources. Keep the installing
clone at its original path for the lifetime of its links. Paths with spaces work.
The target must already exist and not resolve to `/`. Use trusted, non-overlapping
clone/target directories and serialize operations; this is not a transaction or
protection against concurrent filesystem changes. Stow diagnostics/status are
propagated, not translated into the retired installer's error contract.

The wrapper fixes `--no-folding --dotfiles --verbose`. Ambient `$HOME/.stowrc`,
`packages/.stowrc`, and `$HOME/.stow-global-ignore` are refused because options such
as `--adopt` can change safety even with explicit arguments. If needed, use an
existing empty disposable directory as invocation `HOME` and set `--home` explicitly;
do not move or edit live Stow settings just to run this installer.
Custom XDG/tool-directory overrides do not change the package destinations.

### Deliberate Stow semantics

- Real directories are merged at file granularity, not rejected wholesale. Shared
  `.config` and tool skills roots stay real directories; unrelated material stays
  untouched. Ordinary file/wrong/dangling link conflicts abort the whole plan.
- Existing relative Stow-owned links work; equivalent **absolute** legacy links
  conflict in 2.4.1. Do not use `--adopt`, overrides or blanket deletion to fix them.
- Foreign symlinked shared ancestors conflict in the prototype. Unlike the old
  installer, no custom blanket ancestor checker exists: supply physical target
  paths and review Stow's complete dry-run, especially with preexisting links.
- Unstow removes owned links but can leave empty real directories under
  `--no-folding`. It preserves unrelated files; no custom pruning is added.
- Existing file edits are visible immediately. **New files need another Stow run**
  in real destination directories. All three tools' tracked per-skill aliases point
  through the package to canonical `skills/` directories, so new skill files remain
  visible immediately. This small exception preserves Codex directory discovery.
- Vim now mirrors `.vimrc`, `.gvimrc`, `.vim/` directly. RSpec's `.rspec-config`
  is a tracked relative alias to `.rspec-config.rb`, not a content copy. Git's
  `dot-gitignore` becomes the intentional home `.gitignore` via `--dotfiles`,
  retaining Stow's default ignores without a local ignore override. The root
  `.gitignore` is now solely repository policy; the home policy retains its content.

### Private/runtime policy

**Package trees are public installation input, not runtime storage.** Stow does
not consult Git's ignore rules: even gitignored files in packages can be installed.
Keep Neovim `local.lua`, Treehouse `hooks/<origin-basename>-post-create.sh`, Vim
plugin checkouts/backups/swap/undo, and tool-managed skills in target-side real
directories, never in package trees. Existing Git ignore rules are only a secondary
commit guard, not an installation filter. Inspect package trees for ignored/untracked
material before installing from a previously used clone. Do not generate local
files there. No parallel Git/Stow ignore inventory is maintained.

Neovim's native data/state/cache remain target-side; its tracked package lockfile
is linked configuration (an explicit plugin update can edit that source). Vim's
tracked legacy Vundle files remain unchanged. Treehouse's hooks directory retains
a tracked placeholder; create missing target-side runtime directories as needed.
This installer invokes no shell config, editor, plugin, hook, skill or settings API.
See [migration and rollback](docs/stow-migration.md) **before updating a clone
that currently supplies home links**. No live-home switch is authorized here.

## Neovim daily baseline (incremental migration)

The installer links files from [`packages/nvim/.config/nvim`](packages/nvim/.config/nvim)
into the real `~/.config/nvim` directory; no additional plugin links are needed. `init.lua` loads the
`options`, `keymaps`, `autocmds`, and `plugins` modules under `lua/config/`.

Requires **Neovim 0.12+ and Git** for native `vim.pack`. These packages are pinned
to full commits in `plugins.lua`; `nvim-pack-lock.json` is generated by Neovim
0.12.5 in an isolated home, not handwritten from newer web documentation:

| Package | Workflow |
| --- | --- |
| [mini.pick](https://github.com/nvim-mini/mini.pick) | Git-aware cwd-scoped `\f` (unchanged) |
| [MRU](https://github.com/yegappan/mru) | `:MRU`, filter with `:MRU pattern`, Enter opens, `o`/`O` split, `t` tab |
| [Fugitive](https://github.com/tpope/vim-fugitive) | `:Git`, `:Gdiffsplit`, `:Git blame`, `:Gclog`, `:Ggrep` |
| [Surround](https://github.com/tpope/vim-surround) | `ysiw"`, `cs"'`, `ds"`, visual `S` |
| [indent-object](https://github.com/michaeljsmith/vim-indent-object) | `ii`/`ai`/`iI`/`aI` indentation text objects; e.g. `vii`, `>ii` |

Initial plugin installation retains `vim.pack.add()`'s normal confirmation.
Declining leaves the native configuration usable, but uninstalled plugin commands
are unavailable. No `vim-repeat` enhancement is added; test basic operators without
assuming plugin-aware dot-repeat. MRU's legacy GUI menu is disabled: it can leave
an E328 menu error in Neovim, and a GUI is not part of this terminal baseline.
Plugins live under Neovim's `stdpath('data')/site/pack/core/opt`, never `~/.vim`.
Data/state/cache remain in Neovim's standard paths; the native lockfile is config.

**`\f`** runs mini.pick's explicit Git file tool in the **editor's current
working directory**, including window/tab-local cwd. It lists tracked files
(including tracked files matching ignore rules) plus nonignored untracked files,
including eligible dotfiles. It neither expands to repository root nor switches
to a filesystem finder outside Git; a non-repository invocation has no Git results.
Ctrl-N/P move, Enter opens, Ctrl-C/Esc cancel, and Tab toggles the built-in preview.
No fzf, rg, fd, icons, external previewer, or language tooling is required.

This replaces only Selecta's file-picker entry point in Neovim. **MRU remains a
separate recent-file workflow**, not a picker/oldfiles/frecency replacement. Its
history is configured before package loading under Neovim state, never Vim's
`~/.vim_mru_files`. Command-T shortcuts remain excluded. Vim's Selecta wrapper,
MRU history and plugin configuration are unchanged.

The Git source is line-oriented with `core.quotepath=false`: spaces, Unicode and
Ex-special filenames are exercised by integration tests, but Git-quoted names
containing tabs, newlines, backslashes or double quotes are not guaranteed to open
correctly. This is an inherited exceptional-filename limitation, not a lossless
NUL-path implementation. Matching uses mini.pick's algorithm, not Selecta's ranking.
Native opening keeps unsaved buffers rather than discarding their changes.

For a deliberate later plugin update, change the pinned revision, restart, then
use `:lua vim.pack.update({'mini.pick'})` and review/confirm the native update
buffer with `:write` (or discard with `:quit`). Review the generated lockfile diff
alongside the declaration and rerun isolated integration tests. For another package,
substitute its name from `:lua vim.print(vim.pack.get())`. `vim.pack.add()`
does not reset an already installed checkout to a changed pin on every startup;
updates remain explicit. See installed `:help vim.pack` for version-matched API.

### Native workflows and state

Backslash is the leader. Native Unimpaired-style bracket mappings remain in charge;
no Unimpaired plugin or extra bracket-map layer is added.

| Controls | Behavior |
| --- | --- |
| Ctrl-H/J/K/L | Move between splits (Ctrl-L intentionally no longer clears/redraws) |
| Ctrl-Left/Right | Previous/next tab; actual terminal/tmux key delivery varies |
| `%%` / `%f` on command line | Escaped current file's directory / absolute filename |
| `\e` / `\v` | Start edit/view beside the current file; type a filename and Enter |
| `\h` / `\l` | Toggle search highlighting / this window's cursorline |
| `\r` | Re-edit every window, with normal modified-buffer protection; not reload/discard |
| `\\` (Normal/Insert) | Save all; Insert first exits to Normal |
| Ctrl-Z (Normal/Insert) | Save all, then suspend; a failed write or remaining dirty buffer prevents suspension |
| `\s` / `\ls` | Save/restore one private Neovim session slot |
| `\rn` | Prompt for a checked file rename (limits below) |
| F1 / Q / K | F1 escapes in Normal; Q disabled in Normal; K disabled in Normal/Visual/operator-pending |

Existing prefix pairs (`\l`/`\ls`, `\r`/`\rn`) can incur the normal mapping
ambiguity timeout. No keys are reassigned to deferred tooling. Native netrw, tags,
quickfix/location lists, `=`, `gq`, and explicit `"+y`/`"+p` remain available.
Clipboard stays empty: ordinary yanks/deletes do not automatically replace the
system clipboard. Explicit access requires a working provider (e.g. macOS
pbcopy/pbpaste); remote hosts may need their own provider. Tests use an in-memory
mock and never touch the system clipboard.

Search uses ignorecase/smartcase/magic. The explicit Vim preferences are two-space
indentation, expandtab, softtabstop=0, nowrap, line numbers, list, showmode,
scrolloff=3, winwidth=120, cursorline, block virtual editing, alphabetic/hex numeric
increments, autoread and silent bells. Filetypes can override buffer-local defaults;
real-tab formats still use their bundled runtime. `winwidth` is a preference, not a
terminal resize. Native path-focused statusline and the built-in theme remain.

Persistent undo is enabled with native Neovim undo/swap/ShaDa paths. Trial HOME/XDG
paths must all be isolated: `NVIM_APPNAME` alone does not repair literal paths in
private overrides. MRU and netrw receive private state subdirectories before load.
For Vim parity, **backup and writebackup are both off**: undo/swap do not replace
backups, and disabling writebackup reduces protection against failed file writes.
Ordinary files restore valid last-cursor marks; special buffers and invalid marks
are skipped. Sessions can subsequently restore their own views.

Sessions live in `stdpath('state')/sessions/last.vim` (0700 directory, 0600 file),
not shared `/tmp`. Saving atomically replaces that single slot; simultaneous Neovim
sessions are last-writer-wins, not a named-session manager. Sessions are executable
Vimscript with potentially sensitive paths: restore only your own trusted file.
The loader rejects symlinks, foreign ownership and group/world file permissions.
Native session/view options remain unchanged; the Sensible-only delta is deferred.
A config revert does not delete history, sessions, swap or undo recovery files.

### Bundled runtime, small abbreviations and local configuration

Use bundled syntax/ftplugin/indent support for Ruby, Python, JavaScript, Vue,
Markdown, LESS and Clojure; no old language package, LSP, parser or provider install
is implied. Native Ctrl-N/P keywords, Ctrl-X Ctrl-F filenames and filetype-owned
Ctrl-X Ctrl-O omnifunc remain manual. Python omni may require a separately installed
Python provider; simply editing Python/Ruby does not. The explicit `complete+=i`
override is retained without adding Sensible or its other nonnative defaults.

Ruby-only `rdebug`, `rpry`, `byebug`, `debug` insert the exact old debugging text;
changing filetype removes the abbreviations. These do not configure a debugger or
install project gems. In particular, `byebug` still inserts `require 'debug'; byebug`
(an unverified legacy API combination), `rdebug` needs legacy ruby-debug, `rpry`
needs pry, and `debug` uses `binding.break`. Expansion is tested; execution against
project libraries is not. Custom extension aliases (including `.prawn`), old Vue/JS
rules, Ruby syntax preferences and the global XML performance guard are excluded.

An optional **`stdpath('config')/local.lua`** loads last. The default linked path
`~/.config/nvim/local.lua` is target-only; never commit private settings or copy/source
`~/.vimrc.local`. A custom app name/config path needs its own ignore policy. Missing
local config is normal; errors in an existing override are visible. **Restart
Neovim after config edits.** Lua modules are cached; sourcing init.lua is not a hot
reload. Owned autocmds use named clear/redefine groups and do not erase others.
There are no config-save reload hooks or package installs triggered on save.

### Checked rename, not privileged write

`\rn` uses macOS `renamex_np(RENAME_EXCL)` or Linux libc
`renameat2(RENAME_NOREPLACE)` through LuaJIT FFI. If the symbol/kernel/filesystem
cannot perform atomic no-clobber rename, it refuses; **no ordinary overwriting
rename, copy/delete fallback, shell rm or privileged operation** is used. Only
clean, non-readonly ordinary file buffers with one filesystem link are supported.
Cancel/empty/same resolved name are no-ops. Existing destinations (including dangling
symlinks), competing buffer names, symlink/hardlink sources, case-only changes,
missing parents, control bytes and cross-filesystem moves are refused. Spaces,
Unicode, quotes, backslashes and Ex/shell metacharacters are literal filename data.

Destination no-clobber protection is atomic even if another file appears after
preflight. Use trusted directories without concurrent source/ancestor renames;
this is not a hostile-filesystem transaction. Neovim may reuse an existing buffer
when opening a symlink alias; the helper acts on the actual buffer name shown by
Neovim, not the alias originally typed. It preserves buffer identity/content and
never silently saves/discards edits. Before moving it checks the clean buffer against
disk (temporarily using autoread); an external change reloads the buffer and refuses
the rename so you can inspect and retry. This is ordinary timestamp/size change
detection, not protection against hostile source mutation. On a buffer-name hook failure it restores the
file only with the same no-clobber primitive, or reports the retained destination
if restoration is impossible. A post-hook error after a successful rename reports
that both file and buffer moved. Review that message before continuing.

Rename does not stage Git changes; Fugitive's explicit Git commands remain separate.
Reverting config cannot undo filesystem/index operations. No `w!!`/sudo-write helper
is migrated. Test on disposable files before any separately approved daily-use trial.

### Scope and rollout

Align/mini.align, Endwise, indent guides, Sensible-only defaults, Syntastic,
additional language packages, LSP/Tree-sitter/diagnostics, automatic completion,
snippets, GUI, extra themes and vim-repeat are not part of this batch. Badwolf is
excluded; choosing another theme is deferred. Each plugin has a separate declaration
and lock entry, and native configuration/rename changes are separate reversible
increments. Removing a plugin requires reverting its declaration and lock change,
not deleting another editor's package tree. Validate increments and the combined
set in isolated directories; broad implementation is not one required live switch.

Vim's sources and links remain independent and unchanged. Continue invoking `vim`
and `nvim` separately; aliases and `EDITOR`/`VISUAL` are not changed. Behavioral
migration remains tracked in https://github.com/kbaribeau/dotfiles/issues/9.
For a separately approved live installation, inspect the dry-run above first and
reconcile any existing Neovim destination separately; the installer never replaces
it. This change performs no live installation.

## Shared skills: Codex, Cursor, Claude Code

The [skill installation guide](skills/README.md) owns the per-tool discovery paths,
canonical source/reference layout, coexistence behavior, and live-verification
limits. The [ownership policy](#philosophy-skill-ownership) above defines the boundary
between repository-owned personal skills and operator-managed third-party skills.

## Validation

```sh
/bin/bash -n install.sh
shellcheck install.sh                         # optional development lint
python3 -B -m unittest discover -s tests -v   # Python 3.8+, no third-party modules
python3 -B tests/check_codex_discovery.py      # optional, requires installed Codex
# Opt-in: downloads/executes the pinned baseline only inside disposable fixture homes
RUN_NVIM_PICKER_TESTS=1 python3 -B -m unittest discover -s tests -p test_nvim_picker.py -v
RUN_NVIM_BASELINE_TESTS=1 python3 -B -m unittest discover -s tests -p test_nvim_plugins.py -v
```

Tests use synthetic clones and temporary homes under the clone only; they never
copy private config contents or install into the real home. Neovim config copies
exclude `local.lua`; synthetic-override regressions in
[`tests/test_nvim_fixture_isolation.py`](tests/test_nvim_fixture_isolation.py)
cover the installer smoke test and opt-in picker fixture. The offline Neovim smoke
test copies public configuration and stubs plugin loading to verify startup wiring without network or
writes to the config clone; it is skipped if `nvim` is unavailable. The opt-in real
integration test uses isolated HOME/XDG paths under the worktree, native vim.pack
confirmation/installation, and disposable Git repositories. It checks pinned plugin
loading, root/local subdirectory scope, tracked/untracked/hidden/ignored membership,
matching and opening supported filenames, cancellation, empty results, no filesystem
fallback, and preservation of unsaved buffers. It requires Neovim 0.12+, Git and
network access; no live links or plugin stores are touched. The baseline plugin suite
covers native install/decline, pinned loading without startup errors, MRU persistence,
filter/split/tab/stale entries, Fugitive's index/diff/blame/history/grep workflows,
Surround, indent-object and retained native brackets. Offline executable tests cover
options/maps, literal path expansions, explicit mock clipboard, buffer-local Ruby
abbreviations/manual completion, local overrides, undo/marks/private sessions, swap
collisions, and save failures. The Unix PTY fixture supplies its own job-control shell
and terminal-query responses to exercise Normal/Insert Ctrl-Z, actual stop/continue,
and saved buffers after resumption. Rename tests exercise literal filenames, no-ops,
collisions (including a destination created after preflight), permissions, unsaved
buffers, symlinks/hardlinks and buffer-hook failure recovery.

These results do not establish normal installation, actual terminal/tmux special-key
delivery, real clipboard availability, visual contrast or a completed daily-use trial.
The rename no-clobber primitive is exercised on macOS; Linux support remains subject
to its libc/kernel/filesystem and must fail closed when unavailable. No CI bypass is
implied by local tests.

Real-Stow fixture tests cover intended destinations, aliases, ignore behavior,
spaces, dry-run/repeat/restow/unstow, conflicts across packages, shared skill
references, private/runtime coexistence, and a synthetic legacy migration/rollback.
New file discovery is tested with a subsequent Stow invocation. Retired manifest,
atomic-link-engine and bespoke diagnostic tests are gone. Permission tests in the
Neovim suite require an unprivileged user.

The opt-in Codex probe starts its own isolated stdio app-server with temporary `HOME`
and `CODEX_HOME`, using the documented [initialize / skills/list protocol](https://developers.openai.com/codex/app-server/).
It checks both canonical user-scope skill paths, an existing disabled-skill setting,
and an unrelated managed skill. It sends **no model turn or skill invocation** and
changes no live settings. Filesystem checks read references through both installed and
reported paths; the unit suite also verifies all six tool-destination links,
shared-source updates, standalone copied skill directories, and conflict refusal
across all three skill roots. Unrelated operator-installed skill directories and
symlinks, their supporting files, and tool settings are preserved across repeat runs.

Validation on macOS with system Bash 3.2 and **codex-cli 0.153.4** confirms
both repository-owned skills' live fixture discovery. Cursor and Claude
executables were unavailable; see the manual discovery checks in
[skills/README.md](skills/README.md). Documentation/layout checks are static evidence;
filesystem reads are not proof of model-driven reads inside every sandbox or
compatibility with every agent/version. No live-home installation has been performed
by this change.

Design proposal: https://github.com/kbaribeau/dotfiles/issues/6. Its earlier
root-note canonicalization workaround is superseded by the self-contained references.
