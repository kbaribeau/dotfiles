"""Execute public Neovim workflows in disposable HOME/XDG roots; no downloads."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NVIM = shutil.which("nvim")


class NvimFixture:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".nvim-test-", dir=ROOT)
        self.root = Path(self.tmp.name)
        self.config = self.root / "config/nvim"
        shutil.copytree(ROOT / "packages/nvim/.config/nvim", self.config,
                        ignore=shutil.ignore_patterns("local.lua"))
        self.env = {"PATH": os.environ["PATH"], "TERM": "xterm-256color",
                    "HOME": str(self.root / "home"), "TEST_ROOT": str(self.root),
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CEILING_DIRECTORIES": str(self.root),
                    "XDG_CONFIG_HOME": str(self.root / "config"),
                    "XDG_CONFIG_DIRS": str(self.root / "config-dirs"),
                    "XDG_DATA_DIRS": str(self.root / "data-dirs")}
        (self.root / "home").mkdir()
        for kind in ("DATA", "STATE", "CACHE", "RUNTIME"):
            path = self.root / kind.lower()
            path.mkdir(mode=0o700)
            self.env["XDG_" + kind + ("_DIR" if kind == "RUNTIME" else "_HOME")] = str(path)

    def run(self, code, *, real=False, bootstrap="", timeout=30):
        script = self.root / "check.lua"
        script.write_text('''local function check()
local root = vim.env.TEST_ROOT
local function edit(name) vim.cmd.edit(vim.fn.fnameescape(root .. "/" .. name)) end
local function keys(s)
  vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes(s, true, false, true), "xt", false)
end
''' + code + '''
end
vim.schedule(function()
  local ok, err = xpcall(check, debug.traceback)
  if not ok then io.stderr:write(err .. "\\n"); vim.cmd("cquit")
  else print("CONFIG TEST OK"); vim.cmd("qa!") end
end)
''')
        init = self.root / "bootstrap.lua"
        # External theme selection is unrelated to offline workflow assertions.
        init.write_text(("" if real else "vim.pack = { add = function() end }\n"
                        "vim.cmd.colorscheme = function() end\n") + bootstrap)
        return subprocess.run([NVIM, "--headless", "--cmd", "luafile " + str(init),
                               "-c", "luafile " + str(script)], cwd=self.root,
                              env=self.env, text=True, capture_output=True, timeout=timeout)

    def close(self):
        self.tmp.cleanup()


@unittest.skipUnless(NVIM, "requires Neovim 0.12+")
class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.fixture = NvimFixture()
        self.addCleanup(self.fixture.close)

    def check(self, code, **kwargs):
        result = self.fixture.run(code, **kwargs)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONFIG TEST OK", result.stdout + result.stderr)

    def test_options_search_navigation_and_mappings(self):
        (self.fixture.root / "space % # | café.txt").write_text("hello\nHELLO\n0x0a\na\n")
        self.check(r'''
assert(vim.v.errmsg == "", vim.v.errmsg)
assert(vim.o.shiftwidth == 2 and vim.o.tabstop == 2 and vim.o.softtabstop == 0 and vim.o.expandtab)
assert(not vim.o.wrap and vim.o.number and vim.o.list and vim.o.showmode)
assert(vim.o.scrolloff == 3 and vim.o.winwidth == 120 and vim.o.autoread)
assert(vim.o.nrformats == "alpha,hex" and vim.o.virtualedit:find("block", 1, true))
assert(vim.o.belloff == "all" and vim.o.clipboard == "")
assert(vim.o.undofile and not vim.o.backup and not vim.o.writebackup)
assert(vim.o.complete:find("i", 1, true))
edit("space % # | café.txt")
assert(vim.fn.search("hello", "W") == 2) -- ignorecase
vim.api.nvim_win_set_cursor(0, {1, 0})
assert(vim.fn.search("HELLO", "W") == 2) -- smartcase uppercase
vim.api.nvim_win_set_cursor(0, {2, 0})
assert(vim.fn.search("HELLO", "W") == 0)
keys("\\h"); assert(not vim.o.hlsearch); keys("\\h"); assert(vim.o.hlsearch)
keys("\\l"); assert(not vim.wo.cursorline); keys("\\l"); assert(vim.wo.cursorline)
vim.cmd.vsplit(); local second = vim.api.nvim_get_current_win()
keys("<C-l>"); assert(vim.api.nvim_get_current_win() ~= second)
keys("<C-h>"); assert(vim.api.nvim_get_current_win() == second)
vim.cmd.tabnew(); keys("<C-Left>"); assert(vim.fn.tabpagenr() == 1)
keys("<C-Right>"); assert(vim.fn.tabpagenr() == 2)
vim.cmd.tabclose()
keys("QK<F1>"); assert(vim.fn.mode() == "n")
vim.api.nvim_win_set_cursor(0, {3, 2}); keys("<C-a>")
assert(vim.fn.getline(3) == "0x0b")
vim.api.nvim_win_set_cursor(0, {4, 0}); keys("<C-a>")
assert(vim.fn.getline(4) == "b")
-- Command-line expansions are escaped data, including percent/hash/pipe.
keys(":let g:expanded = '" .. "%f" .. "'<CR>")
assert(vim.g.expanded == vim.fn.fnameescape(vim.api.nvim_buf_get_name(0)))
''')

    def test_edit_view_path_expansions_are_literal(self):
        folder = self.fixture.root / "space % # | <CR>"
        folder.mkdir()
        (folder / "from.txt").write_text("from\n")
        (folder / "to.txt").write_text("to\n")
        self.check(r'''
edit("space % # | <CR>/from.txt")
keys("\\eto.txt<CR>")
assert(vim.api.nvim_buf_get_name(0) == root .. "/space % # | <CR>/to.txt")
keys("\\vfrom.txt<CR>")
assert(vim.api.nvim_buf_get_name(0) == root .. "/space % # | <CR>/from.txt" and vim.bo.readonly)
''')

    def test_save_failures_refresh_and_explicit_clipboard(self):
        (self.fixture.root / "one.txt").write_text("one\n")
        (self.fixture.root / "two.txt").write_text("two\n")
        self.check(r'''
edit("one.txt"); local one = vim.api.nvim_get_current_buf()
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"changed one"})
edit("two.txt")
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"changed two"})
keys("\\\\")
assert(vim.fn.readfile(root .. "/one.txt")[1] == "changed one")
assert(vim.fn.readfile(root .. "/two.txt")[1] == "changed two")
keys("A insert save\\\\")
assert(vim.fn.readfile(root .. "/two.txt")[1] == "changed two insert save")
-- A failed write cannot suspend or discard the dirty buffer.
vim.cmd.enew(); vim.api.nvim_buf_set_lines(0, 0, -1, false, {"unsaved unnamed"})
assert(require("config.workflows").save_all(true) == false)
assert(vim.bo.modified and vim.fn.getline(1) == "unsaved unnamed")
vim.bo.modified = false; vim.cmd.bwipeout()
vim.api.nvim_set_current_buf(one)
vim.fn.writefile({"external"}, root .. "/one.txt")
require("config.workflows").refresh()
assert(vim.fn.getline(1) == "external")
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"never discard"})
assert(not pcall(require("config.workflows").refresh))
assert(vim.fn.getline(1) == "never discard" and vim.bo.modified)
-- The provider is entirely in memory; never invoke the system clipboard.
keys('"+yy'); assert(_G.copied[1] == "never discard")
_G.copied = {"clipboard Unicode café", "second line"}
keys('"+p'); assert(vim.fn.getline(2) == "clipboard Unicode café")
local previous = _G.copied
keys('yy'); assert(_G.copied == previous)
''', bootstrap=r'''
_G.copied = {}
vim.g.clipboard = { name = "fixture", cache_enabled = 0,
  copy = { ["+"] = function(lines) _G.copied = lines end, ["*"] = function() end },
  paste = { ["+"] = function() return {_G.copied, "V"} end,
            ["*"] = function() return {{""}, "v"} end } }
''')

    def test_private_overrides_and_owned_autocmds(self):
        self.check(r'''
assert(vim.o.shiftwidth == 2)
local g = vim.api.nvim_create_augroup("UnrelatedFixture", {clear=true})
vim.api.nvim_create_autocmd("BufReadPost", {group=g, callback=function() end})
for _=1,2 do package.loaded["config.autocmds"] = nil; require("config.autocmds") end
assert(#vim.api.nvim_get_autocmds({group="DotfilesCursor"}) == 1)
assert(#vim.api.nvim_get_autocmds({group=g}) == 1)
for _, p in ipairs({vim.g.MRU_File, vim.g.netrw_home, vim.o.undodir, vim.o.directory}) do
  assert(p:find(root .. "/state/nvim/", 1, true), p)
end
''')
        (self.fixture.config / "local.lua").write_text("vim.opt.shiftwidth = 6\n")
        self.check("assert(vim.o.shiftwidth == 6)")
        result = subprocess.run(["git", "check-ignore", "packages/nvim/.config/nvim/local.lua"],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_undo_marks_and_private_sessions_across_restarts(self):
        (self.fixture.root / "one.txt").write_text("before\nline two\nline three\n")
        (self.fixture.root / "two.txt").write_text("two\n")
        self.check(r'''
edit("one.txt")
vim.api.nvim_buf_set_lines(0, 0, 1, false, {"after"}); vim.cmd.write()
vim.api.nvim_win_set_cursor(0, {3, 2})
''')
        self.check(r'''
edit("one.txt"); assert(vim.fn.line(".") == 3)
vim.cmd.undo(); assert(vim.fn.getline(1) == "before"); vim.cmd.write()
vim.cmd.vsplit(); edit("two.txt"); vim.cmd.tabnew(); edit("one.txt")
require("config.sessions").save()
local st = vim.uv.fs_stat(root .. "/state/nvim/sessions/last.vim")
assert(bit.band(st.mode, 511) == 384)
assert(vim.v.this_session == root .. "/state/nvim/sessions/last.vim")
assert(bit.band(vim.uv.fs_stat(root .. "/state/nvim/sessions").mode, 511) == 448)
''')
        self.check(r'''
require("config.sessions").load()
assert(#vim.api.nvim_list_tabpages() == 2)
vim.cmd.tabfirst(); assert(#vim.api.nvim_tabpage_list_wins(0) == 2)
-- Refuse nonprivate and linked executable sessions, without sourcing them.
local target = root .. "/state/nvim/sessions/last.vim"
vim.uv.fs_chmod(target, 420)
assert(not pcall(require("config.sessions").load))
vim.uv.fs_unlink(target); vim.uv.fs_symlink(root .. "/one.txt", target)
assert(not pcall(require("config.sessions").load))
''')

    def test_invalid_cursor_mark_after_file_shrinks(self):
        file = self.fixture.root / "shrunk.txt"
        file.write_text("one\ntwo\nthree\n")
        self.check('edit("shrunk.txt"); vim.api.nvim_win_set_cursor(0, {3, 1})')
        file.write_text("short\n")
        self.check('edit("shrunk.txt"); assert(vim.fn.line(".") == 1)')

    def test_bundled_filetypes_abbreviations_and_manual_completion(self):
        self.check(r'''
for ext, ft in pairs({rb="ruby", py="python", js="javascript", vue="vue", md="markdown", less="less", clj="clojure"}) do
  edit("sample." .. ext); assert(vim.bo.filetype == ft, ext .. ": " .. vim.bo.filetype)
end
edit("sample.rb")
local expected = {
  rdebug = [[require 'ruby-debug'; debugger; puts "debugger should stop here"]],
  rpry = [[require 'pry'; binding.pry; puts "debugger should stop here"]],
  byebug = [[require 'debug'; byebug; puts 'debugger should stop here']],
  debug = [[require "debug"; binding.break; puts "debugger should stop here"]],
}
for trigger, expansion in pairs(expected) do
  vim.api.nvim_buf_set_lines(0, 0, -1, false, {""}); keys("i" .. trigger .. " <Esc>")
  assert(vim.fn.getline(1) == expansion .. " ", vim.fn.getline(1))
end
vim.bo.modified = false
vim.cmd("setfiletype text") -- use an actual FileType transition to run undo_ftplugin
vim.bo.filetype = "text"
assert(vim.fn.maparg("rdebug", "i", true) == "")
edit("plain.txt"); keys("irdebug <Esc>"); assert(vim.fn.getline(1) == "rdebug ")
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"alphabet", "alph"})
vim.api.nvim_win_set_cursor(0, {2, 3}); keys("A<C-n><Esc>")
assert(vim.fn.getline(2) == "alphabet")
vim.bo.modified = false; edit("sample.html")
assert(vim.bo.omnifunc == "htmlcomplete#CompleteTags")
edit("sample.css"); assert(vim.bo.omnifunc == "csscomplete#CompleteCSS")
edit("plain.txt"); assert(vim.bo.omnifunc == "")
vim.fn.writefile({"fixture"}, root .. "/completion-target.txt")
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"completion-t"})
vim.api.nvim_win_set_cursor(0, {1, 11}); keys("A<C-x><C-f><Esc>")
assert(vim.fn.getline(1) == "completion-target.txt")
vim.bo.modified = false; edit("Makefile")
assert(not vim.bo.expandtab)
keys("i<Tab>x<Esc>"); assert(vim.fn.getline(1) == "\tx")
''')


if __name__ == "__main__":
    unittest.main()
