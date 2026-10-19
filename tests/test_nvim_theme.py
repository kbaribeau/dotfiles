"""Offline startup with absent, available, and broken theme/runtime fixtures."""
import unittest
from test_nvim_config import NVIM, NvimFixture


@unittest.skipUnless(NVIM, "requires Neovim 0.12+")
class ThemeStartupTests(unittest.TestCase):
    def setUp(self):
        self.fixture = NvimFixture()
        self.addCleanup(self.fixture.close)

    def check(self, code, bootstrap="vim.pack = {add=function() end}\n"):
        # Keep the real colorscheme loader; only package acquisition is inert.
        result = self.fixture.run(code, real=True, bootstrap=bootstrap)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONFIG TEST OK", result.stdout + result.stderr)

    def theme(self, contents):
        colors = self.fixture.config / "colors"
        colors.mkdir()
        (colors / "catppuccin-mocha.lua").write_text(contents)

    def test_missing_theme_uses_builtin_colors_and_can_save(self):
        self.check('''
assert(vim.v.errmsg == "", vim.v.errmsg)
assert(vim.g.colors_name == "default", tostring(vim.g.colors_name))
edit("fallback file.txt")
vim.api.nvim_buf_set_lines(0, 0, -1, false, {"usable without theme installation"})
vim.cmd.write()
assert(vim.fn.readfile(root .. "/fallback file.txt")[1] == "usable without theme installation")
''')
        self.assertFalse(any((self.fixture.root / "data/nvim/site/pack").glob("**/.git")))

    def test_available_theme_is_selected_with_its_highlights(self):
        self.theme('''vim.g.colors_name = "catppuccin-mocha"
vim.g.fixture_theme_loaded = true
vim.api.nvim_set_hl(0, "Normal", {fg=0xcdd6f4, bg=0x1e1e2e})
''')
        self.check('''
assert(vim.v.errmsg == "", vim.v.errmsg)
assert(vim.g.colors_name == "catppuccin-mocha" and vim.g.fixture_theme_loaded)
local normal = vim.api.nvim_get_hl(0, {name="Normal", link=false})
assert(normal.fg == 0xcdd6f4 and normal.bg == 0x1e1e2e)
''')

    def test_broken_available_theme_error_is_not_hidden(self):
        self.theme('error("fixture-broken-theme")\n')
        self.check('assert(vim.v.errmsg:find("fixture-broken-theme", 1, true), vim.v.errmsg)')

    def test_unrelated_package_error_is_not_hidden(self):
        self.check('assert(vim.v.errmsg:find("fixture-broken-package", 1, true), vim.v.errmsg)',
                   bootstrap='vim.pack = {add=function() error("fixture-broken-package") end}\n')


if __name__ == "__main__":
    unittest.main()
