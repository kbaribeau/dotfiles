#!/usr/bin/env python3
"""Installer contract tests. Only synthetic clones and disposable homes are touched."""
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = [tuple(line.split("\t")) for line in
            (ROOT / "install/links.tsv").read_text().splitlines()
            if line and not line.startswith("#")]
SKILLS = ("consulting-principles", "organizational-lifecycle")
SKILL_ROOTS = (".agents/skills", ".cursor/skills", ".claude/skills")
DIRECTORIES = {"vim/.vim", ".config/treehouse", ".config/nvim"} | {
    "skills/" + name for name in SKILLS}


def fixture(root):
    repo = root / "clone with spaces"
    repo.mkdir()
    shutil.copy2(ROOT / "install.sh", repo)
    (repo / "install").mkdir()
    shutil.copy2(ROOT / "install/links.tsv", repo / "install/links.tsv")
    # Never copy, source, or print personal configuration contents.
    for source, _ in MAPPINGS:
        path = repo / source
        path.parent.mkdir(parents=True, exist_ok=True)
        if source in DIRECTORIES:
            path.mkdir(exist_ok=True)
        else:
            path.write_text("fixture configuration\n")
    shutil.copytree(ROOT / "skills", repo / "skills", dirs_exist_ok=True)
    home = root / "temporary home"
    cwd = root / "unrelated cwd"
    cwd.mkdir()
    return repo, home, cwd


def snapshot(root):
    """No symlink traversal; captures content and link spelling/inode/mtime."""
    result = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        if path.is_symlink():
            value = os.readlink(path)
        elif path.is_file():
            value = path.read_bytes()
        else:
            value = None
        result[str(path.relative_to(root))] = (info.st_mode, info.st_ino,
                                               info.st_mtime_ns, value)
    return result


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".dotfiles-tests-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo, self.home, self.cwd = fixture(self.root)

    def run_install(self, *args, code=0, script=None, env=None, explicit=True):
        command = [str(script or self.repo / "install.sh")]
        if explicit:
            command += ["--home", str(self.home)]
        result = subprocess.run(command + list(args), cwd=self.cwd,
                                env={**os.environ, "HOME": str(self.home), **(env or {})},
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def preserve_failure(self, code=1, *args):
        before = snapshot(self.home)
        result = self.run_install(*args, code=code)
        self.assertEqual(before, snapshot(self.home))
        return result

    def test_full_inventory_default_home_and_repeat(self):
        self.assertEqual(len(MAPPINGS), 24)
        self.assertEqual(len({s for s, _ in MAPPINGS}), 19)
        for source, _ in MAPPINGS:
            self.assertTrue((ROOT / source).exists(), "A manifest source is missing from the clone")
            self.assertTrue(os.access(ROOT / source, os.R_OK))
        self.assertEqual(dict((d, s) for s, d in MAPPINGS), {
            ".zshrc": ".zshrc", ".gitconfig": ".gitconfig", ".gitignore": ".gitignore",
            ".irbrc": ".irbrc", ".psqlrc": ".psqlrc", ".rspec": ".rspec",
            ".rspec-config": ".rspec-config.rb", ".rspec-config.rb": ".rspec-config.rb",
            ".tmux.conf": ".tmux.conf", ".vimrc": "vim/.vimrc", ".vim": "vim/.vim",
            ".gvimrc": "vim/.gvimrc", ".config/treehouse": ".config/treehouse",
            ".config/nvim": ".config/nvim",
            ".profile": ".profile", ".git-completion.bash": ".git-completion.bash",
            ".gitexcludes": ".gitexcludes", ".rdebugrc": ".rdebugrc",
            **{f"{root}/{name}": f"skills/{name}"
               for root in SKILL_ROOTS for name in SKILLS},
        })
        self.run_install(explicit=False)
        for source, destination in MAPPINGS:
            self.assertEqual(os.readlink(self.home / destination), str(self.repo / source))
        self.assertEqual((self.home / ".rspec-config").resolve(),
                         (self.home / ".rspec-config.rb").resolve())
        before = snapshot(self.home)
        result = self.run_install()
        self.assertIn("0 links created, 24 links kept", result.stdout)
        self.assertEqual(before, snapshot(self.home))

    def test_explicit_home_overrides_default_and_tool_overrides_do_not_retarget(self):
        other = self.root / "not-selected-home"
        self.run_install(env={"HOME": str(other), "XDG_CONFIG_HOME": str(other / "config"),
                              "CODEX_HOME": str(other / "codex"), "ZDOTDIR": str(other / "zsh")})
        self.assertFalse(other.exists())
        self.assertTrue((self.home / ".config/treehouse").is_symlink())
        self.assertTrue((self.home / ".agents/skills/consulting-principles").is_symlink())

    def test_dry_run_no_writes_including_missing_home(self):
        before = snapshot(self.root)
        result = self.run_install("--dry-run")
        self.assertEqual(result.stdout.count("create:"), 24)
        self.assertEqual(before, snapshot(self.root))
        self.assertFalse(self.home.exists())

    def test_shared_state_and_removed_links_preserved(self):
        for relative in [f"{root}/tool-managed/SKILL.md" for root in SKILL_ROOTS] + [
                ".codex/config.toml", ".cursor/settings.json", ".claude/settings.json",
                ".config/other/settings", ".viminfo"]:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("unrelated fixture state\n")
        operator_source = self.root / "operator-skill-source"
        operator_source.mkdir()
        (operator_source / "SKILL.md").write_text("inert operator-owned skill\n")
        (operator_source / "reference.md").write_text("operator supporting document\n")
        for root in SKILL_ROOTS:
            directory = self.home / root / "operator-copied"
            shutil.copytree(operator_source, directory)
            (self.home / root / "operator-linked").symlink_to(
                os.path.relpath(operator_source, self.home / root))
        operator_before = snapshot(operator_source)
        (self.home / "bin").symlink_to("retired-missing-directory")
        hook = self.repo / ".config/treehouse/hooks/local-post-create.sh"
        hook.parent.mkdir()
        hook.write_text("fixture private hook, must not execute\n")
        before = snapshot(self.home)
        source_before = snapshot(self.repo)
        self.run_install()
        installed = snapshot(self.home)
        self.run_install()
        after = snapshot(self.home)
        self.assertEqual(installed, after)
        self.assertEqual(operator_before, snapshot(operator_source))
        for root in SKILL_ROOTS:
            for name in ["operator-copied", "operator-linked"]:
                skill = self.home / root / name
                self.assertEqual((skill / "SKILL.md").read_bytes(),
                                 (operator_source / "SKILL.md").read_bytes())
                self.assertEqual((skill / "reference.md").read_bytes(),
                                 (operator_source / "reference.md").read_bytes())
        for path, original in before.items():
            if stat.S_ISDIR(original[0]):
                self.assertEqual(original[:2], after[path][:2])
            else:
                self.assertEqual(original, after[path])
        self.assertEqual(source_before, snapshot(self.repo))
        for parent in [".agents", ".cursor", ".claude", ".config", *SKILL_ROOTS]:
            self.assertFalse((self.home / parent).is_symlink())

    def test_skill_references_linked_and_standalone(self):
        self.run_install()
        for source, destination in MAPPINGS:
            if not source.startswith("skills/"):
                continue
            linked = self.home / destination
            wrapper = (linked / "SKILL.md").read_text()
            refs = re.findall(r"\]\((references/[^)]+)\)", wrapper)
            self.assertEqual(len(refs), 1)
            ref = refs[0]
            self.assertEqual((linked / ref).read_bytes(), (self.repo / source / ref).read_bytes())
            self.assertEqual(linked.resolve(), self.repo / source)
            self.assertIn(f"name: {Path(source).name}\n", wrapper)
            self.assertIn("description:", wrapper)
            copied = self.cwd / destination
            shutil.copytree(linked, copied)
            self.assertEqual((copied / ref).read_bytes(), (linked / ref).read_bytes())
        self.assertFalse((self.repo / "notes").exists())

    def test_script_relative_path_path_lookup_and_symlink_chain(self):
        launch = self.cwd / "launch links"
        launch.mkdir()
        (launch / "second").symlink_to(os.path.relpath(self.repo / "install.sh", launch))
        (launch / "first").symlink_to("second")
        self.run_install(script=launch / "first")
        self.run_install(script="./launch links/first")
        self.run_install(script="first", env={"PATH": str(launch) + os.pathsep + os.environ["PATH"]})
        for source, destination in MAPPINGS:
            self.assertEqual(os.readlink(self.home / destination), str(self.repo / source))

    def test_bash_filename_and_symlinked_script_parent(self):
        result = subprocess.run(["/bin/bash", "install.sh", "--home", str(self.home)],
                                cwd=self.repo, capture_output=True, text=True, timeout=30,
                                env={**os.environ, "HOME": str(self.home), "PATH": "/usr/bin:/bin"})
        self.assertEqual(result.returncode, 0, result.stderr)
        linked_parent = self.cwd / "linked clone"
        linked_parent.symlink_to(self.repo)
        self.assertIn("24 links kept", self.run_install(script=linked_parent / "install.sh").stdout)

    def test_script_loop_rejected_by_os(self):
        first, second = self.cwd / "first", self.cwd / "second"
        first.symlink_to("second")
        second.symlink_to("first")
        result = subprocess.run(["/bin/bash", str(first), "--home", str(self.home)],
                                capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.home.exists())

    def test_resolver_rejects_loop_if_script_changes_after_open(self):
        # Instrument the fixture before resolution: execution has already opened
        # the file, so unlike the OS-loop test this exercises the driver's bound.
        script = self.repo / "install.sh"
        body = script.read_text().replace("script=${BASH_SOURCE[0]}",
                                         'script="$0"\nrm -- "$script"\nln -s install.sh "$script"')
        script.write_text(body)
        self.run_install(code=1)
        self.assertFalse(self.home.exists())

    def test_equivalent_absolute_relative_chained_and_directory_links(self):
        self.home.mkdir()
        (self.home / ".zshrc").symlink_to(self.repo / ".zshrc")
        (self.home / ".gitconfig").symlink_to(os.path.relpath(self.repo / ".gitconfig", self.home))
        (self.home / "hop").symlink_to(self.repo / ".profile")
        (self.home / ".profile").symlink_to("hop")
        (self.home / ".vim").symlink_to(str(self.repo / "vim/.vim") + "/./")
        before = {p: (p.lstat().st_ino, os.readlink(p)) for p in self.home.iterdir()}
        self.run_install()
        for path, original in before.items():
            self.assertEqual(original, (path.lstat().st_ino, os.readlink(path)))
        self.assertIn("24 links kept", self.run_install().stdout)

    def test_all_conflicts_reported_in_manifest_order_without_writes(self):
        self.home.mkdir()
        (self.home / ".zshrc").write_text("real file")
        (self.home / ".gitconfig").mkdir()
        (self.home / ".gitignore").symlink_to(self.repo / ".profile")
        (self.home / ".irbrc").symlink_to("missing")
        (self.home / ".psqlrc").symlink_to(".psqlrc")
        os.mkfifo(self.home / ".rspec")
        # Snapshot deliberately avoids opening the FIFO.
        before = {p.name: p.lstat() for p in self.home.iterdir()}
        result = self.run_install(code=1)
        for name in before:
            self.assertEqual(before[name], (self.home / name).lstat())
        self.assertEqual(set(before), {p.name for p in self.home.iterdir()})
        conflicts = [line.split(": ")[-1] for line in result.stderr.splitlines()]
        self.assertEqual(conflicts, [d for _, d in MAPPINGS[:6]])
        self.assertEqual(result.stderr, self.run_install("--dry-run", code=1).stderr)
        self.assertEqual(list((self.home / ".gitconfig").iterdir()), [])

    def test_nvim_directory_link_exposes_future_nested_files(self):
        self.run_install()
        linked = self.home / ".config/nvim"
        self.assertTrue(linked.is_symlink())
        before = linked.lstat()
        future = self.repo / ".config/nvim/lua/config/workflows/example.lua"
        future.parent.mkdir(parents=True)
        future.write_text("return { fixture = true }\n")
        self.assertEqual((linked / "lua/config/workflows/example.lua").read_bytes(),
                         future.read_bytes())
        self.run_install()
        self.assertEqual(before, linked.lstat())

    def test_nvim_occupied_destination_preserved(self):
        path = self.home / ".config/nvim"
        path.mkdir(parents=True)
        (path / "init.lua").write_text("-- existing fixture configuration\n")
        for args in [(), ("--dry-run",)]:
            result = self.preserve_failure(1, *args)
            self.assertIn("destination conflict: .config/nvim", result.stderr)
            self.assertFalse((self.home / ".vimrc").exists())

    @unittest.skipUnless(shutil.which("nvim"), "headless smoke test requires Neovim")
    def test_nvim_headless_startup_isolated(self):
        # Offline wiring smoke test. Real vim.pack/picker coverage is opt-in in
        # test_nvim_picker.py; this test must never download plugins.
        shutil.copytree(ROOT / ".config/nvim", self.repo / ".config/nvim",
                        dirs_exist_ok=True)
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

    def test_skill_conflict_prevents_configuration_writes(self):
        for root in SKILL_ROOTS:
            for name in SKILLS:
                for kind in ["directory", "file", "wrong-link", "dangling-link", "loop"]:
                    with self.subTest(root=root, name=name, kind=kind):
                        path = self.home / root / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        if kind == "directory":
                            path.mkdir()
                            (path / "SKILL.md").write_text("existing skill")
                        elif kind == "file":
                            path.write_text("user-owned file")
                        else:
                            target = {"wrong-link": self.cwd, "dangling-link": "missing",
                                      "loop": name}[kind]
                            path.symlink_to(target)
                        for args in [(), ("--dry-run",)]:
                            result = self.preserve_failure(1, *args)
                            self.assertIn(f"destination conflict: {root}/{name}", result.stderr)
                            self.assertFalse((self.home / ".zshrc").exists())
                        if kind == "directory":
                            shutil.rmtree(path)
                        else:
                            path.unlink()

    def test_skill_shared_source_changes_visible_in_all_tools(self):
        self.run_install()
        before = snapshot(self.home)
        for name in SKILLS:
            ref = self.repo / "skills" / name / "references/future.md"
            ref.write_text("new fixture reference\n")
            for root in SKILL_ROOTS:
                self.assertEqual((self.home / root / name / "references/future.md").read_bytes(),
                                 ref.read_bytes())
        self.run_install()
        self.assertEqual(before, snapshot(self.home))

    def test_skill_root_symlink_refused_for_every_tool(self):
        self.home.mkdir()
        outside = self.root / "outside-skills"
        outside.mkdir()
        for root in SKILL_ROOTS:
            with self.subTest(root=root):
                path = self.home / root
                path.parent.mkdir(exist_ok=True)
                path.symlink_to(outside)
                self.preserve_failure()
                self.assertEqual(list(outside.iterdir()), [])
                path.unlink()

    def test_unsafe_ancestors_and_home(self):
        self.home.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        for kind in ["file", "directory-link", "dangling", "loop"]:
            with self.subTest(kind=kind):
                path = self.home / ".config"
                if kind == "file":
                    path.write_text("not a directory")
                else:
                    path.symlink_to(outside if kind == "directory-link" else
                                    ("missing" if kind == "dangling" else ".config"))
                self.preserve_failure()
                self.assertEqual(list(outside.iterdir()), [])
                path.unlink()
        self.home.rmdir()
        self.home.symlink_to(outside)
        self.run_install(code=1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_unreadable_and_looping_sources(self):
        for kind in ["missing", "unreadable", "loop"]:
            with self.subTest(kind=kind):
                path = self.repo / ".zshrc"
                path.unlink()
                if kind == "unreadable":
                    path.write_text("unreadable fixture")
                    path.chmod(0)
                    if os.geteuid() == 0:
                        path.chmod(0o600)
                        continue
                elif kind == "loop":
                    path.symlink_to(".zshrc")
                self.preserve_failure()
                self.assertFalse(self.home.exists())
                if path.is_symlink() or path.exists():
                    path.unlink()
                path.write_text("fixture")

    def test_malformed_manifest(self):
        manifest = self.repo / "install/links.tsv"
        valid = manifest.read_text()
        bad_rows = ["no-tab", ".zshrc\t", "\t.zshrc", ".zshrc\t.x\textra",
                    "../escape\t.x", "/absolute\t.x", ".zshrc\t../escape",
                    ".zshrc\t.x/../escape", ".zshrc\t.x//y", ".zshrc\t.x/",
                    ".zshrc\t.x\r", ".zshrc\t.zshrc", ".zshrc\t.ZSHRC",
                    ".zshrc\t.config", ".zshrc\t.config/treehouse/child"]
        for row in bad_rows:
            with self.subTest(row=row):
                manifest.write_text(valid + row + "\n")
                self.preserve_failure(2)
                self.assertFalse(self.home.exists())
        manifest.write_bytes(b".zshrc\t.bad\x00name\n")
        self.preserve_failure(2)
        manifest.write_text("# empty\n")
        self.preserve_failure(2)
        manifest.unlink()
        self.preserve_failure(1)

    def test_manifest_is_data_and_spaces_are_supported(self):
        marker = self.cwd / "must-not-exist"
        source = '$(touch must-not-exist)'
        (self.repo / source).write_text("fixture")
        (self.repo / "install/links.tsv").write_text(f"{source}\ta name with spaces")
        self.run_install()
        self.assertEqual((self.home / "a name with spaces").resolve(), self.repo / source)
        self.assertFalse(marker.exists())

    @unittest.skipIf(os.geteuid() == 0, "permission checks require an unprivileged user")
    def test_unwritable_or_unsearchable_parent(self):
        self.home.mkdir()
        for mode in [0o500, 0o600]:
            with self.subTest(mode=mode):
                self.home.chmod(mode)
                try:
                    self.run_install("--dry-run", code=1)
                    self.run_install(code=1)
                finally:
                    self.home.chmod(0o700)
                self.assertEqual(list(self.home.iterdir()), [])

    def test_source_destination_overlap(self):
        self.home = self.repo
        self.preserve_failure(2)

    def test_usage(self):
        for args in [("--force",), ("--dry-run", "--dry-run"), ("--home",),
                     ("--home", "relative"), ("--home", "/"),
                     ("--home", str(self.home) + "/../escape"),
                     ("--home", str(self.home), "--home", str(self.home))]:
            with self.subTest(args=args):
                self.run_install(*args, code=2, explicit=False)
                self.assertFalse(self.home.exists())
        self.run_install("--help", explicit=False)
        self.assertFalse(self.home.exists())

    def test_partial_failure_and_rerun(self):
        tools = self.root / "tools"
        tools.mkdir()
        perl = shutil.which("perl")
        # Inject failure at the second link, without an installer-only test flag.
        stub = tools / "perl"
        stub.write_text('#!/bin/bash\ncase "${!#}" in */.gitconfig) exit 1 ;; esac\n'
                        f'exec "{perl}" "$@"\n')
        stub.chmod(0o755)
        result = self.run_install(code=1, env={"PATH": str(tools) + os.pathsep + os.environ["PATH"]})
        self.assertIn("partial progress: 1 links", result.stderr)
        self.assertTrue((self.home / ".zshrc").is_symlink())
        self.assertFalse((self.home / ".gitconfig").exists())
        self.assertIn("23 links created, 1 links kept", self.run_install().stdout)

    def test_source_rechecked_during_apply(self):
        tools = self.root / "tools"
        tools.mkdir()
        perl = shutil.which("perl")
        stub = tools / "perl"
        stub.write_text('#!/bin/bash\ncase "${!#}" in */.zshrc)\n'
                        f'rm -- "{self.repo / ".gitconfig"}" ;; esac\n'
                        f'exec "{perl}" "$@"\n')
        stub.chmod(0o755)
        result = self.run_install(code=1, env={"PATH": str(tools) + os.pathsep + os.environ["PATH"]})
        self.assertIn("source or ancestor changed; partial progress: 1 links", result.stderr)
        self.assertFalse((self.home / ".gitconfig").is_symlink())

    def test_exact_destination_no_clobber_under_directory_race(self):
        tools = self.root / "tools"
        tools.mkdir()
        perl = shutil.which("perl")
        stub = tools / "perl"
        stub.write_text('#!/bin/bash\ncase "${!#}" in */.zshrc) mkdir -- "${!#}" ;; esac\n'
                        + f'exec "{perl}" "$@"\n')
        stub.chmod(0o755)
        result = self.run_install(code=1, env={"PATH": str(tools) + os.pathsep + os.environ["PATH"]})
        self.assertIn("partial progress: 0 links", result.stderr)
        self.assertTrue((self.home / ".zshrc").is_dir())
        self.assertEqual(list((self.home / ".zshrc").iterdir()), [])

    def test_ancestor_rechecked_after_parent_creation(self):
        tools = self.root / "tools"
        tools.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        mkdir = shutil.which("mkdir")
        stub = tools / "mkdir"
        stub.write_text('#!/bin/bash\ncase "${!#}" in */.config)\n'
                        f'ln -s "{outside}" "${{!#}}"; exit 0 ;; esac\n'
                        f'exec "{mkdir}" "$@"\n')
        stub.chmod(0o755)
        self.run_install(code=1, env={"PATH": str(tools) + os.pathsep + os.environ["PATH"]})
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.home / ".profile").exists())


if __name__ == "__main__":
    unittest.main()
