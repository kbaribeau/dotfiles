local M = {}

function M.save_all(suspend)
  local ok, err = pcall(vim.cmd, "wall")
  -- :wall may skip special buffers. Never report success while edits remain.
  for _, buf in ipairs(vim.api.nvim_list_bufs()) do
    if vim.api.nvim_buf_is_loaded(buf) and vim.bo[buf].modified then
      ok, err = false, err or "A buffer still has unsaved changes"
      break
    end
  end
  if not ok then
    vim.notify("Save all failed; not suspending: " .. tostring(err), vim.log.levels.ERROR)
    return false
  end
  if suspend then vim.cmd("suspend") end
  return true
end

function M.refresh()
  -- Deliberate all-window refresh, not :edit! or a config reload.
  vim.cmd("windo edit")
end

return M
