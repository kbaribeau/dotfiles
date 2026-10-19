-- Vim workflows migrate incrementally; keep Vim's runtime and state separate.
require("config.options")
require("config.keymaps")
require("config.autocmds")
require("config.plugins")

-- Machine-local code is optional, private, and Neovim-specific.
-- Restart after configuration edits; sourcing this file does not reload cached Lua.
local local_config = vim.fn.stdpath("config") .. "/local.lua"
if vim.fn.filereadable(local_config) == 1 then
  dofile(local_config)
end

vim.pack.add({
  { src = "https://github.com/catppuccin/nvim" },
})
-- Declining installation leaves the theme absent; do not hide loader errors
-- from an available theme or change the package-installation choice.
if #vim.api.nvim_get_runtime_file("colors/catppuccin-mocha.lua", false) > 0
  or #vim.api.nvim_get_runtime_file("colors/catppuccin-mocha.vim", false) > 0 then
  vim.cmd.colorscheme("catppuccin-mocha")
else
  vim.cmd.colorscheme("default")
end
