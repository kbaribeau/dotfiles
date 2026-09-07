-- Never share writable history with Vim or put it in the linked config tree.
local M = {}

function M.directory(name)
  local path = vim.fn.stdpath("state") .. "/" .. name
  local st = vim.uv.fs_lstat(path)
  if st and st.type ~= "directory" then
    error("Neovim state directory is not a real directory: " .. path)
  end
  vim.fn.mkdir(path, "p", 448) -- 0700; parents follow the operator's XDG layout.
  assert(vim.uv.fs_chmod(path, 448))
  return path
end

vim.g.MRU_File = M.directory("mru") .. "/files"
vim.g.netrw_home = M.directory("netrw")
return M
