"""Opt-in pinned-plugin execution; network and all editor/Git state are isolated."""
import json
import os
import subprocess
import unittest
from test_nvim_config import NVIM, NvimFixture, ROOT


@unittest.skipUnless(NVIM and os.environ.get("RUN_NVIM_BASELINE_TESTS") == "1",
                     "set RUN_NVIM_BASELINE_TESTS=1 (Neovim 0.12+, Git, network)")
class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = NvimFixture()
        cls.addClassCleanup(cls.fixture.close)
        result = cls.fixture.run('assert(vim.v.errmsg == "", vim.v.errmsg)', real=True,
                                 bootstrap="vim.fn.confirm = function() return 1 end\n", timeout=120)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def check(self, code):
        result = self.fixture.run('assert(vim.v.errmsg == "", vim.v.errmsg)\n' + code, real=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_decline_then_pinned_startup(self):
        declined = NvimFixture()
        self.addCleanup(declined.close)
        result = declined.run('assert(_G.asked > 0); assert(vim.v.errmsg == "", vim.v.errmsg)',
                              real=True, bootstrap="_G.asked=0; vim.fn.confirm=function() _G.asked=_G.asked+1; return 2 end")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(any((declined.root / "data/nvim/site/pack").glob("**/.git")))
        # Lockfile is the serialized native package contract, not an implementation-text test.
        expected = json.loads((ROOT / "packages/nvim/.config/nvim/nvim-pack-lock.json").read_text())["plugins"]
        self.check('local expected = vim.json.decode(' + json.dumps(json.dumps(expected)) + r''')
local packages = vim.pack.get()
assert(#packages == 5)
for _, p in ipairs(packages) do
  assert(expected[p.spec.name].rev == p.rev)
  assert(vim.startswith(p.path, root .. "/data/nvim/"))
end
-- Regression: the old MRU menu path left E328 even in otherwise usable startup.
assert(vim.fn.exists(":MRU") == 2 and vim.v.errmsg == "", vim.v.errmsg)
''')

    def test_mru_restart_filter_split_tab_and_stale_file(self):
        for name in ("recent-alpha.txt", "recent-beta.txt", "stale.txt"):
            (self.fixture.root / name).write_text(name + "\n")
        self.check('edit("recent-alpha.txt"); edit("recent-beta.txt"); edit("stale.txt")')
        self.assertFalse((self.fixture.root / "home/.vim_mru_files").exists())
        self.check(r'''
vim.cmd("MRU recent-")
assert(vim.bo.buftype == "nofile")
assert(vim.fn.search("recent-alpha", "w") > 0)
keys("o")
assert(vim.api.nvim_buf_get_name(0) == root .. "/recent-alpha.txt")
assert(#vim.api.nvim_tabpage_list_wins(0) == 2)
vim.cmd.MRU(); assert(vim.fn.search("recent-beta", "w") > 0); keys("t")
assert(vim.api.nvim_buf_get_name(0) == root .. "/recent-beta.txt")
assert(#vim.api.nvim_list_tabpages() == 2)
''')
        (self.fixture.root / "stale.txt").unlink()
        self.check(r'''
vim.cmd.MRU()
if vim.fn.search("stale.txt", "w") > 0 then keys("<CR>") end
assert(vim.fn.filereadable(root .. "/stale.txt") == 0)
assert(not vim.bo.modified)
''')

    def test_fugitive_git_index_diff_blame_history_and_grep(self):
        repo = self.fixture.root / "repo"
        repo.mkdir(exist_ok=True)
        def git(*args):
            return subprocess.run(["git", "-C", str(repo), *args], env=self.fixture.env,
                                  check=True, capture_output=True, text=True)
        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (repo / "review.txt").write_text("original needle\n")
        git("add", "review.txt")
        git("commit", "-qm", "Fixture baseline")
        (repo / "review.txt").write_text("changed needle\n")
        self.check(r'''
vim.cmd.cd(root .. "/repo"); edit("repo/review.txt")
local buf = vim.api.nvim_get_current_buf()
local function git(args)
  return vim.system(vim.list_extend({"git", "-C", root .. "/repo"}, args), {text=true}):wait().stdout
end
vim.cmd("Git add -- review.txt")
assert(vim.wait(5000, function() return git({"diff", "--cached", "--name-only"}):find("review.txt", 1, true) end))
vim.cmd("Git reset -- review.txt")
assert(vim.wait(5000, function() return git({"diff", "--cached", "--name-only"}) == "" end))
vim.cmd.Gdiffsplit(); assert(#vim.api.nvim_tabpage_list_wins(0) >= 2)
vim.cmd("only!"); vim.api.nvim_set_current_buf(buf)
vim.cmd("Git blame")
assert(vim.wait(5000, function() return vim.bo.filetype == "fugitiveblame" end))
vim.cmd.close(); vim.api.nvim_set_current_buf(buf) -- leave blame's fixed-buffer window
vim.cmd("Ggrep needle")
assert(vim.wait(5000, function() return #vim.fn.getqflist() > 0 end))
assert(vim.fn.getqflist()[1].lnum == 1)
vim.cmd.Gclog(); assert(vim.wait(5000, function() return #vim.fn.getqflist() > 0 end))
vim.cmd.cclose(); vim.api.nvim_set_current_buf(buf)
vim.api.nvim_buf_set_lines(buf, 0, -1, false, {"unsaved Git review"})
vim.cmd.Git()
assert(vim.bo.filetype == "fugitive")
assert(vim.bo[buf].modified and vim.api.nvim_buf_get_lines(buf, 0, -1, false)[1] == "unsaved Git review")
''')
        self.assertEqual(git("diff", "--cached", "--name-only").stdout, "")

    def test_surround_indent_objects_and_native_brackets(self):
        self.check(r'''
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"word"})
keys([[ysiw"]]); assert(vim.fn.getline(1) == [["word"]])
keys([[cs"']]); assert(vim.fn.getline(1) == [['word']])
keys([[ds']]); assert(vim.fn.getline(1) == "word")
keys("u"); assert(vim.fn.getline(1) == [['word']])
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"word"}); keys([[viwS)]])
assert(vim.fn.getline(1) == "(word)")
local lines = {"outer", "  inner", "", "    leaf", "next"}
vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
vim.api.nvim_win_set_cursor(0, {2, 2}); keys("vii")
assert(vim.fn.line("v") == 2 and vim.fn.line(".") == 4)
keys("<Esc>"); vim.api.nvim_win_set_cursor(0, {2, 2})
keys("dii"); assert(vim.fn.getline(2) == "next")
keys("u"); assert(vim.deep_equal(vim.api.nvim_buf_get_lines(0, 0, -1, false), lines))
vim.bo.modified = false
edit("native-a.txt"); local a = vim.api.nvim_get_current_buf()
edit("native-b.txt"); local b = vim.api.nvim_get_current_buf()
keys("[b"); assert(vim.api.nvim_get_current_buf() == a)
keys("]b"); assert(vim.api.nvim_get_current_buf() == b)
''')


if __name__ == "__main__":
    unittest.main()
