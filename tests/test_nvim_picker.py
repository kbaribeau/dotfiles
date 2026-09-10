"""Opt-in real plugin integration; all downloads/state stay in a disposable home."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("RUN_NVIM_PICKER_TESTS") == "1" and
                     shutil.which("nvim") and shutil.which("git"),
                     "set RUN_NVIM_PICKER_TESTS=1 (Neovim 0.12+, Git, network required)")
class PickerIntegrationTests(unittest.TestCase):
    def test_real_git_picker(self):
        with tempfile.TemporaryDirectory(prefix=".picker-test-", dir=ROOT) as tmp:
            base = Path(tmp)
            home = base / "home"
            home.mkdir()
            config = base / "config/nvim"
            shutil.copytree(ROOT / "packages/nvim/.config/nvim", config,
                            ignore=shutil.ignore_patterns("local.lua"))
            env = {"PATH": os.environ["PATH"], "HOME": str(home),
                   "XDG_CONFIG_HOME": str(base / "config"),
                   "XDG_CONFIG_DIRS": str(base / "config-dirs"),
                   "XDG_DATA_DIRS": str(base / "data-dirs"),
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_CEILING_DIRECTORIES": str(base)}
            for kind in ("DATA", "STATE", "CACHE", "RUNTIME"):
                path = base / kind.lower()
                path.mkdir(mode=0o700)
                env["XDG_" + kind + ("_DIR" if kind == "RUNTIME" else "_HOME")] = str(path)
            repo = base / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], env=env, check=True)
            tracked = ["tracked.txt", ".tracked", "ignored-tracked.txt", "sub/tracked.txt"]
            untracked = ["space name.txt", "café.txt", "review % # | [x].txt",
                         ".untracked", ".hidden/visible.txt", "sub/new.txt", "sub/.hidden"]
            for name in tracked + untracked + ["ignored.txt", ".ignored", "sub/ignored.txt"]:
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture content\n")
            subprocess.run(["git", "-C", str(repo), "add", "--"] + tracked,
                           env=env, check=True)
            (repo / ".gitignore").write_text("ignored*\n.ignored\n")
            empty = base / "empty"
            empty.mkdir()
            subprocess.run(["git", "init", "-q", str(empty)], env=env, check=True)
            outside = base / "outside"
            outside.mkdir()
            (outside / "not-in-git.txt").write_text("must not be listed\n")
            env.update(PICKER_REPO=str(repo), PICKER_EMPTY=str(empty),
                       PICKER_OUTSIDE=str(outside))
            # Exercise native initial-install confirmation without installing.
            declined = subprocess.run(
                [shutil.which("nvim"), "--headless", "-i", "NONE",
                 "--cmd", "lua vim.fn.confirm = function() _G.asked = true; return 2 end",
                 "-c", 'lua assert(asked); assert(vim.v.errmsg == "", vim.v.errmsg)',
                 "-c", "qa!"], cwd=repo, env=env, capture_output=True,
                text=True, timeout=30)
            self.assertEqual(declined.returncode, 0, declined.stdout + declined.stderr)
            self.assertFalse((base / "data/nvim/site/pack/core/opt/mini.pick").exists())
            check = ROOT / "tests/nvim_picker.lua"
            result = subprocess.run(
                [shutil.which("nvim"), "--headless", "-i", "NONE",
                 "--cmd", "lua vim.fn.confirm = function() return 1 end",
                 "-c", "luafile " + str(check)],
                cwd=repo, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PICKER INTEGRATION OK", result.stdout + result.stderr)
            # Neither opening nor dirty-buffer handling may alter files on disk.
            self.assertEqual((repo / "tracked.txt").read_text(), "fixture content\n")
            self.assertFalse((home / ".vim").exists())
            self.assertFalse((home / ".vim_mru_files").exists())


if __name__ == "__main__":
    unittest.main()
