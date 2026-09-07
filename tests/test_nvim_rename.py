"""Filesystem-observable safe-rename regressions, never real editor files."""
import os
import sys
import unittest
from test_nvim_config import NVIM, NvimFixture


@unittest.skipUnless(NVIM and sys.platform in ("darwin", "linux"),
                     "rename supports Neovim on macOS/Linux with no-clobber libc API")
class RenameTests(unittest.TestCase):
    def setUp(self):
        self.fixture = NvimFixture()
        self.addCleanup(self.fixture.close)
        (self.fixture.root / "source.txt").write_text("original bytes\n")

    def check(self, code):
        result = self.fixture.run('local rename = require("config.rename").rename\n' + code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_literal_names_and_buffer_identity(self):
        self.check(r'''
edit("source.txt"); local buf = vim.api.nvim_get_current_buf()
for _, name in ipairs({[[space café % # | ' " ; $ [x].txt]], [[back\slash.txt]], "final.txt"}) do
  local old = vim.api.nvim_buf_get_name(buf)
  local ok, err = rename(root .. "/" .. name)
  assert(ok, err)
  assert(not vim.uv.fs_lstat(old))
  assert(vim.fn.readfile(root .. "/" .. name)[1] == "original bytes")
  assert(vim.api.nvim_get_current_buf() == buf and vim.api.nvim_buf_get_name(buf) == root .. "/" .. name)
  assert(not vim.bo.modified and vim.fn.getline(1) == "original bytes")
end
assert(rename(nil)); assert(rename("")); assert(rename(root .. "/./final.txt"))
assert(not rename(root .. "/FINAL.txt"))
''')
        files = {p.name for p in self.fixture.root.glob("*.txt")}
        self.assertEqual(files, {"final.txt"})

    def test_refusals_leave_bytes_and_unsaved_changes(self):
        root = self.fixture.root
        (root / "exists.txt").write_text("destination bytes\n")
        (root / "dangling.txt").symlink_to(root / "missing.txt")
        (root / "symbolic.txt").symlink_to(root / "source.txt")
        (root / "hard-source.txt").write_text("hard linked\n")
        os.link(root / "hard-source.txt", root / "hard-other.txt")
        self.check(r'''
edit("source.txt")
for _, name in ipairs({"exists.txt", "dangling.txt", "no-parent/file.txt", "control\nname"}) do
  assert(not rename(root .. "/" .. name), name)
end
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"unsaved"})
assert(not rename(root .. "/modified.txt"))
assert(vim.bo.modified and vim.fn.getline(1) == "unsaved")
vim.bo.modified = false
local other = vim.api.nvim_create_buf(true, false)
vim.api.nvim_buf_set_name(other, root .. "/reserved.txt")
assert(not rename(root .. "/reserved.txt"))
-- Forget the original buffer: Neovim otherwise reuses it by inode when opening its symlink.
vim.cmd("bwipeout!")
edit("symbolic.txt"); assert(not rename(root .. "/symbolic-new.txt"))
edit("hard-source.txt"); assert(not rename(root .. "/hard-new.txt"))
vim.cmd.enew(); assert(not rename(root .. "/unnamed.txt"))
edit("source.txt"); vim.bo.buftype = "nofile"; assert(not rename(root .. "/special.txt"))
''')
        self.assertEqual((root / "source.txt").read_text(), "original bytes\n")
        self.assertEqual((root / "exists.txt").read_text(), "destination bytes\n")
        self.assertTrue((root / "dangling.txt").is_symlink())
        for name in ("reserved.txt", "modified.txt", "hard-new.txt", "symbolic-new.txt", "special.txt"):
            self.assertFalse((root / name).exists())

    def test_destination_created_after_preflight_is_not_clobbered(self):
        self.check(r'''
edit("source.txt")
local dest = root .. "/race.txt"
local lstat = vim.uv.fs_lstat
vim.uv.fs_lstat = function(path, ...)
  local result = lstat(path, ...)
  if path == dest and not result then
    vim.fn.writefile({"concurrent winner"}, dest) -- appears after the observed preflight
  end
  return result
end
local ok, err = rename(dest)
vim.uv.fs_lstat = lstat
assert(not ok, err)
assert(vim.fn.readfile(dest)[1] == "concurrent winner")
assert(vim.fn.readfile(root .. "/source.txt")[1] == "original bytes")
assert(vim.api.nvim_buf_get_name(0) == root .. "/source.txt")
''')

    def test_buffer_autocommand_failure_recovery(self):
        self.check(r'''
edit("source.txt")
local group = vim.api.nvim_create_augroup("RenameFailureFixture", {clear=true})
vim.api.nvim_create_autocmd("BufFilePre", {group=group, callback=function() error("fixture failure") end})
local ok, err = rename(root .. "/new.txt")
assert(not ok and err:find("file restored", 1, true), err)
assert(vim.fn.filereadable(root .. "/source.txt") == 1)
assert(vim.fn.filereadable(root .. "/new.txt") == 0)
assert(vim.api.nvim_buf_get_name(0) == root .. "/source.txt")
vim.api.nvim_clear_autocmds({group=group})
vim.api.nvim_create_autocmd("BufFilePost", {group=group, callback=function() error("post fixture failure") end})
ok, err = rename(root .. "/new.txt")
assert(not ok and err:find("File and buffer renamed", 1, true), err)
assert(vim.fn.filereadable(root .. "/source.txt") == 0)
assert(vim.api.nvim_buf_get_name(0) == root .. "/new.txt")
assert(vim.fn.readfile(root .. "/new.txt")[1] == "original bytes")
''')

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "permission test requires non-root")
    def test_permission_failure(self):
        locked = self.fixture.root / "locked"
        locked.mkdir(mode=0o500)
        try:
            self.check(r'''
edit("source.txt"); assert(not rename(root .. "/locked/new.txt"))
assert(vim.fn.readfile(root .. "/source.txt")[1] == "original bytes")
assert(vim.api.nvim_buf_get_name(0) == root .. "/source.txt")
''')
        finally:
            locked.chmod(0o700)


if __name__ == "__main__":
    unittest.main()
