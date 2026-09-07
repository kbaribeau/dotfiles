-- Native vim.pack requires Neovim 0.12+. Keep initial installation confirmation.
vim.pack.add({
  {
    src = "https://github.com/nvim-mini/mini.pick",
    version = "b27dc13b3d6dafc10e868b6ddc682cc4f047f4d1",
  },
  {
    src = "https://github.com/yegappan/mru",
    version = "dcba22de1201523acda1e1a60d6fc3d9d7b6a519",
  },
  {
    src = "https://github.com/tpope/vim-fugitive",
    version = "3b753cf8c6a4dcde6edee8827d464ba9b8c4a6f0",
  },
})

-- Declining installation should leave the rest of Neovim usable.
local ok, pick = pcall(require, "mini.pick")
if ok then
  pick.setup()
end
