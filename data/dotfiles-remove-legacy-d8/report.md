# Legacy dotfiles cleanup

## Scope and outcome

This is repository cleanup and a **proposed installation inventory**, not an installation. The installer remains a proposal: https://github.com/kbaribeau/dotfiles/issues/6.

- Removed all three currently tracked `bin/` entries (`.gitignore`, `clone`, and the SoundFont), `.screenrc`, `.autotest`, and all four tracked `.autotest_images/` PNGs. The older audit's other bin entries were already absent from this revision.
- Removed `playmidi` and obsolete home-bin PATH wiring from both retained shell configurations, plus the profile's home-bin `hub` alias. Removed the obsolete bin example in `AGENTS.md`.
- **Retained `.profile`: current bounded static evidence is inconclusive for indirect startup loading.** Native/direct Zsh startup does not load it, but that is insufficient to approve deletion under the conditional instruction. `.git-completion.bash` is retained independently of that decision.
- No installer implemented or run; no home links, primary checkout, untracked/private files, or unrelated configuration changed. Existing home links are not removed by this patch; updating a checkout that supplies them later may leave links to deleted entries dangling. That reconciliation is separate work.
- Filed future investigation only: https://github.com/kbaribeau/dotfiles/issues/9 (Vim to Neovim). No migration investigation or changes performed.

## Startup evidence and limits

The existing `dotfiles-install-audit-n3/report.md` was read first as historical reference. The following observations were then independently made on the current machine, read-only, without sourcing or executing startup files or printing private startup contents:

- Inherited `ZDOTDIR` is unset. System `/etc/zshenv` and `/etc/zlogin`, and home `.zshenv`, `.zprofile`, and `.zlogin`, are absent. Effective home `.zshrc` is byte-identical to the pre-change tracked version.
- `/etc/zprofile` sets locale and evaluates `path_helper`; it does not source `.profile`. `/etc/zshrc` supplies defaults and optional keybinding/terminal support. The keybinding directory and the support file selected by the current `TERM_PROGRAM=tmux` are absent. Apple Terminal support was also read, but is not selected in this environment; its session restore behavior is not evidence about other terminal sessions.
- The only profile-named source in effective `.zshrc` is `.profile.local` (pre-change lines 101–103), **not `.profile`**. That optional local file is currently absent. Another guarded optional shell hook is absent. A separate source statement occurs inside a manually invoked initialization function, not a startup call.
- Startup also invokes `compinit`, evaluates Homebrew/rbenv/pyenv initialization output, and sources NVM and its completion script. The two NVM files have no `.profile` or `ZDOTDIR` references. Installed rbenv and pyenv init generators were read: their Zsh print branches emit completion loading and rehash commands, not direct `.profile` loading; profile references in installation/help branches do not establish startup use.
- **Unresolved boundary:** `FPATH` is set and the default `.zcompdump` exists. Completion caches/functions and all tool dispatch/plugin/generated-output chains were not exhaustively inspected. No dynamic init commands were run to resolve their output. Therefore this inspection rules out native and direct loading, not every indirect explicit source chain. `.profile` is retained pending stronger evidence/clarification, as required for inconclusive evidence. This is not a claim that it is used, nor a claim that it is unused in Bash, manual sessions, or other launch environments.

## Revised proposed link manifest

Source paths are repository-relative; destination paths are home-relative. Historical grouping is preserved, with authorized removals subtracted: **11 core + 6 legacy = 17 links** (21 minus bin, Screen, Autotest, and images). There are 16 distinct sources because the RSpec configuration has two destinations. If `.profile` is later approved for deletion, remove its legacy row for 16 links.

```text
# group  source                         destination
core     .zshrc                         .zshrc
core     .gitconfig                     .gitconfig
core     .gitignore                     .gitignore
core     .irbrc                         .irbrc
core     .psqlrc                        .psqlrc
core     .rspec                         .rspec
core     .rspec-config.rb               .rspec-config
core     .tmux.conf                     .tmux.conf
core     vim/.vimrc                     .vimrc
core     vim/.vim                       .vim
core     .config/treehouse              .config/treehouse
legacy   .profile                       .profile
legacy   .git-completion.bash           .git-completion.bash
legacy   .gitexcludes                   .gitexcludes
legacy   .rspec-config.rb               .rspec-config.rb
legacy   .rdebugrc                      .rdebugrc
legacy   vim/.gvimrc                    .gvimrc
```

These are proposed link destinations, not files actually touched today, and groups do not establish application usage. Preserve individual Treehouse linking (never all of `~/.config`), special Vim mappings, both RSpec aliases, existing local Vim state, and ignored private hooks. Notes and personal skills remain uninstalled; no application/plugin provisioning or whole shared-directory replacement is proposed. Excluding a manifest row never authorizes removing its existing home link.

## Validation

- `/bin/zsh -f -n .zshrc` and `/bin/bash --noprofile --norc -n .profile`: syntax-only checks passed; live configuration was not sourced.
- `git diff --check HEAD`: passed.
- Tracked-reference scan: removed bundled command/asset names and home-bin paths have no remaining shell configuration references.
- Static inventory assertions: all requested deletion paths are absent from the index and worktree; `.profile` and `.git-completion.bash` remain; all 17 manifest destinations are unique and all sources exist.
- No runtime shell startup, installer, hooks, or application tests were run, and no extra review pipeline was invoked.
