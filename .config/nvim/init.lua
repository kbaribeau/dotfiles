-- Vim workflows migrate incrementally; keep Vim's runtime and state separate.
require("config.options")
require("config.keymaps")
require("config.autocmds")
require("config.plugins")

-- Machine-local code is optional, private, Neovim-specific, and deliberately last.
-- Restart after configuration edits; sourcing this file does not reload cached Lua.
local local_config = vim.fn.stdpath("config") .. "/local.lua"
if vim.fn.filereadable(local_config) == 1 then
  dofile(local_config)
end

vim.pack.add({
  { src = "https://github.com/catppuccin/nvim" },
})
 vim.cmd.colorscheme("catppuccin-mocha")
