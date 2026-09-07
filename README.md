# Dotfiles

Personal configuration and [self-contained reference skills](skills/README.md).

## Conservative link installer

[`install/links.tsv`](install/links.tsv) is the complete, unconditional inventory:
**19 links to 18 sources** (17 configuration links and two whole skill directories).
It includes both RSpec aliases, all three special Vim mappings, and only the
Treehouse subdirectory of `.config`. There are no core/legacy groups or selection flags.

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
  remain untouched. An existing real `~/.vim` or `~/.config/treehouse` is a conflict,
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

## Codex skills

The installer links each skill individually at
`~/.agents/skills/{consulting-principles,organizational-lifecycle}`. It never replaces
`.agents` or its shared `skills` parent. [Codex documentation](https://developers.openai.com/codex/skills/)
supports user-scope discovery there and follows symlinked skill folders. This is a
shared discovery location, **not Codex exclusivity**. Existing disable settings are
preserved; discovery does not force invocation. Dedicated Cursor/Claude integration
is deferred to https://github.com/kbaribeau/dotfiles/issues/11.

Each directory carries `SKILL.md` and its own `references/` document. Reads do not
depend on root `notes/`, parent traversal, per-tool copies, or a custom loader.
Filesystem access to the clone is still required by the consuming agent/sandbox.

## Validation

```sh
/bin/bash -n install.sh
shellcheck install.sh                         # optional development lint
python3 -B -m unittest discover -s tests -v   # Python 3.8+, no third-party modules
python3 -B tests/check_codex_discovery.py      # optional, requires installed Codex
```

Tests use synthetic clones and temporary homes only; they never copy personal config
contents or install into the real home. They cover the full inventory, preservation,
repeat runs, dry runs, path/symlink resolution, malformed data, all conflict classes,
unsafe/unwritable ancestors, unavailable sources, and injected partial/racing failures.
Permission tests require an unprivileged user.

The opt-in Codex probe starts its own isolated stdio app-server with temporary `HOME`
and `CODEX_HOME`, using the documented [initialize / skills/list protocol](https://developers.openai.com/codex/app-server/).
It checks both canonical user-scope skill paths, an existing disabled-skill setting,
and an unrelated managed skill. It sends **no model turn or skill invocation** and
changes no live settings. Filesystem checks read references through both installed and
reported paths; the unit suite also verifies standalone copied skill directories.

Validation on macOS with system Bash 3.2 and **codex-cli 0.153.2** confirms live
fixture discovery. Documentation/layout checks are static evidence; filesystem reads
are not proof of model-driven reads inside every sandbox or compatibility with every
agent/version. No live-home installation has been performed by this change.

Design proposal: https://github.com/kbaribeau/dotfiles/issues/6. Its earlier
root-note canonicalization workaround is superseded by the self-contained references.
