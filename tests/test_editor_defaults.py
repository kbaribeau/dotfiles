"""Fresh-shell and Git dispatch in synthetic homes; never source private startup."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHELLS = [("bash", ".profile"), ("zsh", ".zshrc")]


class EditorDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".editor-defaults-", dir=ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.bin = self.home / "bin"
        self.bin.mkdir()
        self.repo = self.root / "repo with spaces"
        self.repo.mkdir()
        # Do not inherit real Git/editor/XDG settings or executable startup hooks.
        self.env = dict(HOME=str(self.home), ZDOTDIR=str(self.home),
                        PATH=f"{self.bin}:/usr/bin:/bin", TERM="dumb",
                        XDG_CONFIG_HOME=str(self.home / ".config"),
                        GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
                        FIXTURE_ROOT=str(self.root))
        shutil.copyfile(ROOT / "packages/git/.gitconfig", self.home / ".gitconfig")
        subprocess.run(["/usr/bin/git", "init", "-q", str(self.repo)],
                       env=self.env, check=True, capture_output=True)
        for name in ("nvim", "vim", "alternate"):
            script = self.bin / name
            script.write_text(f"#!{sys.executable}\n" + '''import json, os, pathlib, sys, time
root = pathlib.Path(os.environ["FIXTURE_ROOT"])
(root / "dispatch.json").write_text(json.dumps([pathlib.Path(sys.argv[0]).name, *sys.argv[1:]]))
if os.environ.get("WAIT_EDITOR") == "1":
    deadline = time.monotonic() + 10
    while not (root / "release").exists():
        if time.monotonic() > deadline:
            sys.exit(90)
        time.sleep(0.01)
    with open(sys.argv[-1], "a") as target:
        target.write("\\n# fixture edit completed\\n")
    (root / "finished").touch()
''')
            script.chmod(0o755)
        # Execute the complete public shell configs, redirecting legacy absolute
        # home paths into the fixture and stubbing unrelated machine bootstraps.
        # No editor/default/alias lines are extracted, filtered or replaced.
        for shell, filename in SHELLS:
            source = (ROOT / "packages/shell" / filename).read_text()
            source = source.replace("/Users/kbaribeau", "${HOME}")
            source = source.replace("/opt/homebrew/bin/brew", "brew")
            stubs = "brew() { :; }; nodenv() { :; }; pyenv() { :; }; stty() { :; }\n"
            (self.home / filename).write_text(stubs + source)
        # Bash's interactive startup normally needs an operator-selected owner
        # (.bashrc/.bash_profile); this repository owns .profile, not those files.
        (self.home / "bashrc").write_text('. "$HOME/.profile"\n')

    def command(self, shell, script, login=False):
        executable = shutil.which(shell)
        if not executable:
            self.skipTest(f"requires {shell}")
        script = 'export PATH="$HOME/bin:$PATH"\n' + script
        if shell == "zsh":
            return [executable, "-d", "-ilc" if login else "-ic", script]
        return [executable, "--noprofile", "--rcfile", str(self.home / "bashrc"), "-ic", script]

    def run_shell(self, shell, script, overrides=None, login=False):
        result = subprocess.run(self.command(shell, script, login), cwd=self.repo,
                                env=dict(self.env, **(overrides or {})),
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_fixture_editors_take_precedence_after_shell_startup(self):
        competing_bin = self.home / "competing bin"
        competing_bin.mkdir()
        for name in ("vim", "nvim"):
            executable = competing_bin / name
            executable.write_text("#!/bin/sh\nexit 91\n")
            executable.chmod(0o755)
        startup = f'export PATH={shlex.quote(str(competing_bin))}:"$PATH"\n'
        (self.home / ".profile.local").write_text(startup)
        (self.home / ".zlogin").write_text(startup)
        for shell, _ in SHELLS:
            for login in ((False, True) if shell == "zsh" else (False,)):
                for name in ("vim", "nvim"):
                    with self.subTest(shell=shell, login=login, editor=name):
                        (self.root / "dispatch.json").unlink(missing_ok=True)
                        self.run_shell(shell, f'{name} "file with spaces"', login=login)
                        self.assertEqual(json.loads((self.root / "dispatch.json").read_text()),
                                         [name, "file with spaces"])

    def test_defaults_exported_to_children_and_direct_vim_unchanged(self):
        for shell, _ in SHELLS:
            for login in ((False, True) if shell == "zsh" else (False,)):
                with self.subTest(shell=shell, login=login):
                    out = self.run_shell(shell, '''
/bin/sh -c 'printf "%s/%s\\n" "$EDITOR" "$VISUAL"'
command -v vm >/dev/null 2>&1 && exit 31
alias vim >/dev/null 2>&1 && exit 32
alias vi >/dev/null 2>&1 && exit 33
alias view >/dev/null 2>&1 && exit 34
alias vimdiff >/dev/null 2>&1 && exit 35
vim --literal 'file with spaces'
''', login=login)
                    self.assertEqual(out, "nvim/nvim")
                    self.assertEqual(json.loads((self.root / "dispatch.json").read_text()),
                                     ["vim", "--literal", "file with spaces"])
                    for variable in ("EDITOR", "VISUAL"):
                        self.run_shell(shell, f'"${variable}" +12 "file with spaces"', login=login)
                        self.assertEqual(json.loads((self.root / "dispatch.json").read_text()),
                                         ["nvim", "+12", "file with spaces"])

    def test_inherited_empty_and_private_environment_overrides(self):
        for shell, _ in SHELLS:
            with self.subTest(shell=shell):
                script = 'printf "%s/%s" "$EDITOR" "$VISUAL"'
                self.assertEqual(self.run_shell(shell, script,
                                 {"EDITOR": "alternate --flag", "VISUAL": "alternate"}),
                                 "alternate --flag/alternate")
                self.assertEqual(self.run_shell(shell, script, {"EDITOR": "", "VISUAL": ""}),
                                 "nvim/nvim")
                self.assertEqual(self.run_shell(shell, script, {"EDITOR": "alternate"}),
                                 "alternate/nvim")
                (self.home / ".profile.local").write_text(
                    "export EDITOR=local-editor VISUAL=local-visual\n")
                self.assertEqual(self.run_shell(shell, script), "local-editor/local-visual")
                (self.home / ".profile.local").unlink()

    def test_git_selection_and_override_precedence_without_alias(self):
        for shell, _ in SHELLS:
            with self.subTest(shell=shell):
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR"), "nvim")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR",
                                 {"EDITOR": "alternate", "VISUAL": "alternate"}), "nvim")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR",
                                 {"GIT_EDITOR": "alternate --invocation"}), "alternate --invocation")
                (self.home / ".gitconfig.local").write_text("[core]\n editor = alternate --private\n")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR"), "alternate --private")
                self.run_shell(shell, "command git config core.editor 'alternate --repository'")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR"), "alternate --repository")
                self.assertEqual(self.run_shell(shell,
                    "command git -c core.editor='alternate --command' var GIT_EDITOR"), "alternate --command")
                self.run_shell(shell, "command git config --unset core.editor")
                (self.home / ".gitconfig.local").unlink()
                # Git falls through to the environment without the tracked Git config.
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR",
                                 {"GIT_CONFIG_GLOBAL": "/dev/null"}), "nvim")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR",
                    {"GIT_CONFIG_GLOBAL": "/dev/null", "TERM": "xterm",
                     "VISUAL": "alternate --visual", "EDITOR": "alternate --editor"}), "alternate --visual")
                self.assertEqual(self.run_shell(shell, "command git var GIT_EDITOR",
                    {"GIT_CONFIG_GLOBAL": "/dev/null", "TERM": "dumb",
                     "VISUAL": "alternate --visual", "EDITOR": "alternate --editor"}), "alternate --editor")

    def test_git_edit_passes_arguments_and_waits_for_editor(self):
        for shell, _ in SHELLS:
            for override in (False, True):
                with self.subTest(shell=shell, override=override):
                    for marker in ("dispatch.json", "release", "finished"):
                        (self.root / marker).unlink(missing_ok=True)
                    env = dict(self.env, WAIT_EDITOR="1")
                    if override:
                        env["GIT_EDITOR"] = "alternate --flag 'two words'"
                    process = subprocess.Popen(self.command(shell, "command git config --edit"),
                        cwd=self.repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    try:
                        deadline = time.monotonic() + 10
                        while not (self.root / "dispatch.json").exists():
                            if process.poll() is not None or time.monotonic() > deadline:
                                self.fail("Git did not invoke the fixture editor")
                            time.sleep(0.01)
                        self.assertIsNone(process.poll(), "Git must wait for the editor")
                        self.assertFalse((self.root / "finished").exists())
                        (self.root / "release").touch()
                        stdout, stderr = process.communicate(timeout=10)
                        self.assertEqual(process.returncode, 0, stdout + stderr)
                        self.assertTrue((self.root / "finished").exists())
                        args = json.loads((self.root / "dispatch.json").read_text())
                        self.assertEqual(args[:-1], ["alternate", "--flag", "two words"] if override else ["nvim"])
                        target = Path(args[-1])
                        if not target.is_absolute():
                            target = self.repo / target
                        self.assertEqual(target.resolve(), (self.repo / ".git/config").resolve())
                        self.assertIn("# fixture edit completed", target.read_text())
                    finally:
                        if process.poll() is None:
                            process.kill()
                            process.communicate()

    @unittest.skipUnless(Path("/usr/bin/vim").is_file(), "requires system Vim fallback")
    def test_explicit_original_vim_runs_without_neovim_config(self):
        target = self.root / "fallback file.txt"
        script = 'if has("nvim") | cquit | endif\ncall setline(1, "original Vim")\nwq\n'
        commands = self.root / "fallback.vim"
        commands.write_text(script)
        for shell, _ in SHELLS:
            with self.subTest(shell=shell):
                self.run_shell(shell, "/usr/bin/vim -Nu NONE -i NONE -n -es -S " +
                               shlex.quote(str(commands)) + " -- " + shlex.quote(str(target)))
                self.assertEqual(target.read_text(), "original Vim\n")
                target.unlink()


if __name__ == "__main__":
    unittest.main()
