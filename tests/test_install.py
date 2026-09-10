#!/usr/bin/env python3
"""Repository integration with real GNU Stow; all writes stay in disposable homes."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("consulting-principles", "organizational-lifecycle")
SKILL_ROOTS = (".agents/skills", ".cursor/skills", ".claude/skills")
CANONICAL = Path("skills")


def fixture(root):
    repo = root / "clone with spaces"
    repo.mkdir()
    shutil.copy2(ROOT / "install.sh", repo)
    # Only tracked paths; never copy ignored/private material from the worker clone.
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", "packages", "skills"],
                                    cwd=ROOT).decode().split("\0")
    for name in filter(None, paths):
        source, dest = ROOT / name, repo / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            dest.symlink_to(os.readlink(source))
        elif name.startswith("skills/") or source.name.startswith(".stow-"):
            shutil.copy2(source, dest)
        else:
            dest.write_text("fixture configuration\n")
    home = root / "temporary home"
    home.mkdir()
    cwd = root / "unrelated cwd"
    cwd.mkdir()
    return repo, home, cwd


def snapshot(root):
    """Content and links, without traversing linked directories or timestamp noise."""
    return {str(p.relative_to(root)): ("link", os.readlink(p)) if p.is_symlink()
            else ("file", p.read_bytes()) if p.is_file() else ("directory",)
            for p in sorted(root.rglob("*"))}


@unittest.skipUnless(shutil.which("stow"), "integration requires GNU Stow")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".dotfiles-tests-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo, self.home, self.cwd = fixture(self.root)

    def run_install(self, *args, code=0, env=None):
        result = subprocess.run([str(self.repo / "install.sh"), "--home", str(self.home), *args],
                                cwd=self.cwd, env={**os.environ, "HOME": str(self.home), **(env or {})},
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def test_destinations_aliases_ignore_and_lifecycle(self):
        self.run_install("--dry-run")
        self.assertEqual(snapshot(self.home), {})
        self.run_install()
        for path in [".zshrc", ".profile", ".git-completion.bash", ".gitconfig", ".gitignore",
                     ".gitexcludes", ".tmux.conf", ".irbrc", ".rspec", ".rspec-config",
                     ".rspec-config.rb", ".rdebugrc", ".psqlrc", ".vimrc", ".gvimrc",
                     ".vim/plugins.vim", ".vim/autoload/pathogen.vim",
                     ".config/nvim/init.lua", ".config/nvim/nvim-pack-lock.json",
                     ".config/treehouse/config.toml", ".config/treehouse/post-create.sh",
                     ".pi/agent/extensions/herdr-context.ts"]:
            self.assertTrue((self.home / path).is_file(), path)
        self.assertEqual((self.home / ".rspec-config").resolve(),
                         (self.home / ".rspec-config.rb").resolve())
        self.assertEqual((self.home / ".gitignore").resolve(),
                         self.repo / "packages/git/dot-gitignore")
        for directory in [".config", ".config/nvim", ".vim", ".pi/agent/extensions", *SKILL_ROOTS]:
            self.assertFalse((self.home / directory).is_symlink(), directory)
        before = snapshot(self.home)
        self.run_install()
        self.assertEqual(before, snapshot(self.home))
        self.run_install("--restow", "--dry-run")
        self.assertEqual(before, snapshot(self.home))
        self.run_install("--restow")
        self.assertEqual(before, snapshot(self.home))
        self.assertFalse(any(p.name in (".git", ".stow-local-ignore", "AGENTS.md")
                             for p in self.home.rglob("*")))
        self.run_install("--unstow", "--dry-run")
        self.assertEqual(before, snapshot(self.home))
        self.run_install("--unstow")
        self.assertTrue(all(value == ("directory",) for value in snapshot(self.home).values()))

    def test_coexistence_private_runtime_and_removal(self):
        paths = [".config/nvim/local.lua", ".config/treehouse/hooks/fixture-post-create.sh",
                 ".config/other/settings", ".vim/bundle/fixture/plugin.vim", ".vim/undo/history",
                 ".vim/backups/fixture", ".vim/swap/fixture", ".viminfo", ".codex/config.toml",
                 ".pi/agent/extensions/herdr-agent-state.ts", ".pi/agent/settings.json"]
        paths += [f"{root}/operator-owned/SKILL.md" for root in SKILL_ROOTS]
        for name in paths:
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("sanitized target-only fixture\n")
        for root in SKILL_ROOTS:
            (self.home / root / "operator-alias").symlink_to("operator-owned")
        before = snapshot(self.home)
        sources = snapshot(self.repo)
        self.run_install()
        self.run_install()
        self.run_install("--restow")
        for name, value in before.items():
            self.assertEqual(snapshot(self.home)[name], value)
        self.run_install("--unstow")
        after = snapshot(self.home)
        for name, value in before.items():
            self.assertEqual(after[name], value)
        self.assertTrue(all(value == ("directory",) for name, value in after.items() if name not in before))
        self.assertEqual(sources, snapshot(self.repo))

    def test_conflicts_across_packages_and_skill_roots(self):
        for name in [".zshrc", ".config/nvim/init.lua", ".pi/agent/extensions/herdr-context.ts"] + [f"{r}/{n}/SKILL.md"
                    for r in SKILL_ROOTS for n in SKILLS]:
            with self.subTest(name=name):
                path = self.home / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("existing user material")
                before = snapshot(self.home)
                self.run_install(code=1)
                self.run_install("--dry-run", code=1)
                self.assertEqual(before, snapshot(self.home))
                self.assertFalse((self.home / ".tmux.conf").exists())
                shutil.rmtree(self.home)
                self.home.mkdir()

    def test_existing_links_and_symlinked_shared_ancestor(self):
        path = self.home / ".zshrc"
        source = self.repo / "packages/shell/.zshrc"
        for target in [str(source), "missing", str(self.repo / "packages/git/.gitconfig")]:
            path.symlink_to(target)
            before = snapshot(self.home)
            self.run_install(code=1)
            self.assertEqual(before, snapshot(self.home))
            path.unlink()
        path.symlink_to(os.path.relpath(source, self.home))
        self.run_install()
        self.run_install("--unstow")
        shutil.rmtree(self.home)
        self.home.mkdir()
        outside = self.root / "outside fixture"
        outside.mkdir()
        for name in [".config", *SKILL_ROOTS]:
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(outside)
            self.run_install(code=1)
            self.assertEqual(list(outside.iterdir()), [])
            path.unlink()

    def test_skills_canonical_references_and_new_files(self):
        self.run_install()
        for name in SKILLS:
            source = self.repo / CANONICAL / name
            standalone = self.root / name
            shutil.copytree(source, standalone)
            for root in SKILL_ROOTS:
                installed = self.home / root / name
                self.assertEqual((installed / "SKILL.md").resolve(), (source / "SKILL.md").resolve())
                for ref in source.glob("references/*.md"):
                    self.assertEqual((installed / "references" / ref.name).read_bytes(), ref.read_bytes())
                    self.assertEqual((standalone / "references" / ref.name).read_bytes(), ref.read_bytes())
                for relative in re.findall(r'\]\((references/[^)]+)\)', (installed / "SKILL.md").read_text()):
                    self.assertTrue((installed / relative).is_file())
            existing = next(source.glob("references/*.md"))
            existing.write_text(existing.read_text() + "\nFixture update.\n")
            for root in SKILL_ROOTS:
                self.assertEqual((self.home / root / name / "references" / existing.name).read_bytes(),
                                 existing.read_bytes())
            (source / "references/new file.md").write_text("new fixture reference")
            for root in SKILL_ROOTS:
                self.assertEqual((self.home / root / name / "references/new file.md").read_text(),
                                 "new fixture reference")
        # Ordinary non-alias package directories need restow for new files.
        new_config = self.repo / "packages/nvim/.config/nvim/new file.lua"
        new_config.write_text("-- public fixture")
        self.assertFalse((self.home / ".config/nvim/new file.lua").exists())
        self.run_install("--restow")
        self.assertEqual((self.home / ".config/nvim/new file.lua").read_text(), "-- public fixture")
        for name in SKILLS:
            for root in SKILL_ROOTS:
                self.assertEqual((self.home / root / name / "references/new file.md").read_text(),
                                 "new fixture reference")

    def test_legacy_switch_and_rollback(self):
        # Operator sequence, not a reusable migration engine. Old clone stays put.
        old = self.root / "retained legacy clone"
        (old / ".config/nvim").mkdir(parents=True)
        (old / ".zshrc").write_text("synthetic dirty tracked source")
        (old / ".config/nvim/init.lua").write_text("old tracked config")
        (old / ".config/nvim/local.lua").write_text("synthetic private override")
        (self.home / ".config").mkdir()
        (self.home / ".zshrc").symlink_to(old / ".zshrc")
        (self.home / ".config/nvim").symlink_to(old / ".config/nvim")
        (self.home / ".config/unrelated").write_text("preserve")
        original = snapshot(self.home)
        old_sources = snapshot(old)
        self.run_install("--dry-run", code=1)
        self.assertEqual(original, snapshot(self.home))
        backup = self.root / "private backup"
        backup.mkdir()
        # Preserve exact link entries, and separately back up actual source data.
        shutil.copytree(old, backup / "source data")
        (self.home / ".zshrc").rename(backup / "shell link")
        (self.home / ".config/nvim").rename(backup / "nvim link")
        (self.home / ".config/nvim").mkdir()
        shutil.copy2(old / ".config/nvim/local.lua", self.home / ".config/nvim/local.lua")
        self.run_install("--dry-run")
        self.run_install()
        self.assertEqual((self.home / ".config/nvim/local.lua").read_text(),
                         "synthetic private override")
        (self.home / ".config/nvim/local.lua").write_text("synthetic post-switch edit")
        self.run_install("--unstow", "--dry-run")
        self.run_install("--unstow")
        self.assertEqual(old_sources, snapshot(old))
        shutil.copy2(self.home / ".config/nvim/local.lua", backup / "post-switch local.lua")
        (self.home / ".config/nvim/local.lua").unlink()
        # Only empty fixture directories, never user contents, are removed.
        for directory in sorted(self.home.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if directory.is_dir() and not directory.is_symlink() and not any(directory.iterdir()):
                directory.rmdir()
        (backup / "shell link").rename(self.home / ".zshrc")
        (backup / "nvim link").rename(self.home / ".config/nvim")
        self.assertEqual(original, snapshot(self.home))
        self.assertEqual(snapshot(backup / "source data"), snapshot(old))
        self.assertEqual((backup / "post-switch local.lua").read_text(), "synthetic post-switch edit")
        self.assertEqual((self.home / ".zshrc").read_text(), "synthetic dirty tracked source")

    def test_ambient_stow_configuration_refused(self):
        for path in [self.home / ".stowrc", self.repo / "packages/.stowrc",
                     self.home / ".stow-global-ignore"]:
            path.write_text("--adopt\n")
            before = snapshot(self.home)
            self.assertIn("Ambient Stow", self.run_install(code=1).stderr)
            self.assertEqual(before, snapshot(self.home))
            path.unlink()
        # Invocation-directory config isn't loaded: wrapper changes into packages.
        (self.cwd / ".stowrc").write_text("--adopt\n")
        self.run_install()

    @unittest.skipUnless(shutil.which("nvim"), "headless smoke test requires Neovim")
    def test_nvim_headless_startup_isolated(self):
        # Offline wiring smoke test. Real vim.pack/picker coverage is opt-in in
        # test_nvim_picker.py; this test must never download plugins.
        shutil.copytree(ROOT / "packages/nvim/.config/nvim", self.repo / "packages/nvim/.config/nvim",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("local.lua"))
        self.run_install()
        before = snapshot(self.repo)
        env = {"PATH": os.environ["PATH"], "HOME": str(self.home),
               "XDG_CONFIG_HOME": str(self.home / ".config"),
               "XDG_CONFIG_DIRS": str(self.root / "config-dirs"),
               "XDG_DATA_DIRS": str(self.root / "data-dirs")}
        for kind in ["DATA", "STATE", "CACHE", "RUNTIME"]:
            directory = self.root / kind.lower()
            directory.mkdir(mode=0o700)
            env["XDG_" + kind + ("_DIR" if kind == "RUNTIME" else "_HOME")] = str(directory)
        check = self.cwd / "check.lua"
        check.write_text('''local ok, err = pcall(function()
  assert(vim.fn.resolve(vim.env.MYVIMRC) ==
         vim.fn.resolve(vim.env.XDG_CONFIG_HOME .. "/nvim/init.lua"))
  assert(vim.v.errmsg == "", vim.v.errmsg)
  for _, name in ipairs({"options", "keymaps", "autocmds", "plugins"}) do
    assert(package.loaded["config." .. name], name .. " was not loaded")
  end
end)
if not ok then
  io.stderr:write(tostring(err))
  vim.cmd("cquit")
else
  vim.cmd("qa!")
end
''')
        bootstrap = self.cwd / "offline.lua"
        bootstrap.write_text('''vim.pack = { add = function() end }
-- The existing config selects an external theme; do not download it in offline tests.
vim.cmd.colorscheme = function() end
package.preload["mini.pick"] = function()
  return { setup = function() end }
end
''')
        result = subprocess.run([shutil.which("nvim"), "--headless",
                                 "--cmd", "luafile offline.lua", "-c", "luafile check.lua"],
                                cwd=self.cwd, env=env, capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, snapshot(self.repo))


if __name__ == "__main__":
    unittest.main()
