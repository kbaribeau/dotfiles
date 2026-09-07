require("config.state") -- Pre-load paths must precede vim.pack.

local opt = vim.opt
opt.ignorecase = true
opt.smartcase = true
opt.magic = true
opt.hlsearch = true
opt.autoread = true
opt.tabstop = 2
opt.shiftwidth = 2
opt.softtabstop = 0
opt.expandtab = true
opt.wrap = false
opt.showmode = true
opt.number = true
opt.list = true
opt.scrolloff = 3
opt.winwidth = 120
opt.cursorline = true
opt.nrformats = { "alpha", "hex" }
opt.virtualedit:append("block")
opt.belloff = "all"
-- Preserve explicit clipboard registers; ordinary yanks/deletes stay local.
opt.clipboard = ""
-- Vim parity, not a backup strategy. Native Neovim XDG paths remain in use.
opt.backup = false
opt.writebackup = false
opt.undofile = true
-- This was an explicit override in plugins.vim, not a Sensible-only default.
opt.complete:append("i")
vim.g.netrw_list_hide = ",\\~$,^tags$"
