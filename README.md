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

## Conservative link installer

[`install/links.tsv`](install/links.tsv) is the complete, unconditional inventory.
It includes both RSpec aliases, all three special Vim mappings, and only the
Treehouse and Neovim subdirectories of `.config`. There are no core/legacy groups or selection flags.

```sh
./install.sh --dry-run                 # inspect the plan for $HOME; writes nothing
./install.sh --home /absolute/test-home --dry-run
./install.sh --home /absolute/test-home
# ./install.sh                        # apply to $HOME only when deliberately requested
```

Run the script, **do not source it**. Absolute/relative invocation, Bash invocation
(`bash /path/to/clone/install.sh`), PATH lookup, and script symlink chains are supported.
Sources always come from the clone containing the **resolved installer**, not the
working directory or another preferred checkout. Keep that clone accessible for the
lifetime of the links. Paths with spaces work. Final symlink chains are bounded at
64 hops; loops fail (a loop at launch may be rejected by the OS before the script runs).

Requires Bash 3.2+, standard macOS/Unix utilities (`readlink`, `mkdir`, `tr`), and Perl.
Perl's `symlink(2)` binding provides exact-destination, atomic no-clobber creation;
portable `ln` can instead nest a link inside a directory that appears after a check.
No GNU-only `ln -T` or `readlink -f` is used. Missing dependencies are not installed.

### Safety and limits

- The manifest is data, never sourced/evaluated: exactly two tab-separated normalized
  relative paths per row, with blank lines and `#` comments allowed. No absolute paths,
  dot/parent components, empty/extra fields, or control bytes (other than tab/LF).
  Destination duplicates/ancestor overlaps are rejected, including ASCII case variants.
- Every valid mapping is preflighted before writes: source readability/type (and
  directory searchability), destination conflicts, source/destination overlap, and
  ancestor safety. Known errors are reported deterministically. Directory checks do
  not validate every contained file or establish application readiness.
- Equivalent absolute, relative, or chained correct links stay **verbatim**. Real files,
  directories, special files, and wrong/dangling/looping links are conflicts, never
  overwritten, backed up, merged, removed, or repointed. Reconcile conflicts separately.
- Only missing links and required parents are created. Existing shared directories,
  tool-managed skills, private hooks, local Vim state, and links outside the manifest
  remain untouched. An existing real `~/.vim`, `~/.config/nvim`, or `~/.config/treehouse` is a conflict,
  not permission to merge its contents. A skill conflict prevents config writes too.
- `--home` defaults to `$HOME`; it must be a normalized, non-root absolute path.
  **All destination ancestors, including the selected home, must be real directories,
  not symlinks.** Missing ancestors must have a writable existing parent. Use a physical
  path for temporary homes (on macOS `/tmp` and `/var` are often symlinks; `pwd -P`
  inside an existing temporary directory gives its physical spelling).
- Dry-run creates nothing, including parents. Apply rechecks sources, ancestors, and
  destinations; link creation cannot overwrite or nest inside an existing entry.
  Use serially in a trusted filesystem: concurrent installers/ancestor renames are
  unsupported, and rechecks are not a transaction or protection against a hostile
  concurrent filesystem actor. On runtime failure, stop with partial-progress counts
  and nonzero exit; **no rollback**. After resolving the cause, reruns converge.
- V1 uses the documented default destinations under the chosen home. Custom
  `XDG_CONFIG_HOME`, `CODEX_HOME`, `ZDOTDIR`, or other tool-directory overrides are
  **unsupported and do not change the manifest destinations**. Setting such variables
  may mean an application does not use these links.

Exit codes: **0** success/clean dry-run; **1** conflicts, unavailable sources/dependencies,
filesystem/runtime failures; **2** invalid arguments/manifest (takes precedence when
both manifest and filesystem errors are found). `--help` exits 0.

This only links files: no packages, plugins/submodules, startup sourcing, hook or
skill invocation, settings edits, private configuration generation, or old home-link
cleanup. Linking a shell file is not a claim that a particular shell loads it.

## Neovim daily baseline (incremental migration)

The installer links the whole [`.config/nvim`](.config/nvim) directory to
`~/.config/nvim`; no additional plugin links are needed. `init.lua` loads the
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
| `%%` / `%f` on command line | Escaped current directory / absolute filename |
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
`.config/nvim/local.lua` is gitignored; never commit private settings or copy/source
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
copy private config contents or install into the real home. The offline Neovim smoke
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

Fixture tests also cover occupied Neovim destinations and future
nested files becoming visible through the directory link without installer changes. They cover the full inventory, preservation,
repeat runs, dry runs, path/symlink resolution, malformed data, all conflict classes,
unsafe/unwritable ancestors, unavailable sources, and injected partial/racing failures.
Permission tests require an unprivileged user.

The opt-in Codex probe starts its own isolated stdio app-server with temporary `HOME`
and `CODEX_HOME`, using the documented [initialize / skills/list protocol](https://developers.openai.com/codex/app-server/).
It checks both canonical user-scope skill paths, an existing disabled-skill setting,
and an unrelated managed skill. It sends **no model turn or skill invocation** and
changes no live settings. Filesystem checks read references through both installed and
reported paths; the unit suite also verifies all six tool-destination links,
shared-source updates, standalone copied skill directories, and conflict refusal
across all three skill roots. Unrelated operator-installed skill directories and
symlinks, their supporting files, and tool settings are preserved across repeat runs.

Validation on macOS with system Bash 3.2 and **codex-cli 0.153.2** confirms
both repository-owned skills' live fixture discovery. Cursor and Claude
executables were unavailable; see the manual discovery checks in
[skills/README.md](skills/README.md). Documentation/layout checks are static evidence;
filesystem reads are not proof of model-driven reads inside every sandbox or
compatibility with every agent/version. No live-home installation has been performed
by this change.

Design proposal: https://github.com/kbaribeau/dotfiles/issues/6. Its earlier
root-note canonicalization workaround is superseded by the self-contained references.
