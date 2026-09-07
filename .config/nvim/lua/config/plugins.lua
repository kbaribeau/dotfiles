-- Native vim.pack requires Neovim 0.12+. Keep initial installation confirmation.
vim.pack.add({
  {
    src = "https://github.com/nvim-mini/mini.pick",
    version = "b27dc13b3d6dafc10e868b6ddc682cc4f047f4d1",
  },
})

-- Declining installation should leave the rest of Neovim usable.
local ok, pick = pcall(require, "mini.pick")
if ok then
  pick.setup()
end
