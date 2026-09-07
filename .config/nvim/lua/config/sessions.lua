local M = {}
local function path()
  return require("config.state").directory("sessions") .. "/last.vim"
end

function M.save()
  local target = path()
  -- Generate privately, then atomically replace our single Neovim session slot.
  local tmp = target .. "." .. vim.uv.os_getpid() .. "." .. vim.uv.hrtime()
  local fd, err = vim.uv.fs_open(tmp, "wx", 384) -- 0600
  if not fd then error(err) end
  vim.uv.fs_close(fd)
  local ok, failure = pcall(function()
    vim.cmd("mksession! " .. vim.fn.fnameescape(tmp))
    assert(vim.uv.fs_chmod(tmp, 384))
    assert(vim.uv.fs_rename(tmp, target))
  end)
  if not ok then
    vim.uv.fs_unlink(tmp)
    error(failure)
  end
  vim.v.this_session = target
  vim.notify("Saved Neovim session: " .. target)
end

function M.load()
  local target = path()
  local st = vim.uv.fs_lstat(target)
  -- Sessions execute code. Never source a symlink or a group/world-accessible file.
  if not st or st.type ~= "file" or bit.band(st.mode, 63) ~= 0
    or st.uid ~= vim.uv.os_get_passwd().uid then
    error("No private, owned Neovim session at " .. target)
  end
  vim.cmd("source " .. vim.fn.fnameescape(target))
end

return M
