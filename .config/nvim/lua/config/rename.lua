-- A deliberately small, no-clobber rename for clean regular files.
local M = {}
local uv = vim.uv
local ffi = require("ffi")
ffi.cdef([[
  int renamex_np(const char *, const char *, unsigned int);
  int renameat2(int, const char *, int, const char *, unsigned int);
  char *strerror(int);
]])

local function move(old, new)
  local os = uv.os_uname().sysname
  local available, primitive = pcall(function()
    if os == "Darwin" then return ffi.C.renamex_np end
    if os == "Linux" then return ffi.C.renameat2 end
  end)
  if not available or not primitive then
    return nil, "No supported atomic no-clobber rename on this platform"
  end
  -- macOS RENAME_EXCL / Linux RENAME_NOREPLACE: an existence check alone
  -- would race and ordinary rename() would overwrite the destination.
  local rc
  if os == "Darwin" then rc = primitive(old, new, 4)
  else rc = primitive(-100, old, -100, new, 1) end -- AT_FDCWD
  if rc ~= 0 then return nil, ffi.string(ffi.C.strerror(ffi.errno())) end
  return true
end

local function canonical(path)
  local parent = uv.fs_realpath(vim.fs.dirname(path))
  if parent then return parent .. "/" .. vim.fs.basename(path) end
end

function M.rename(target, buf)
  buf = buf or vim.api.nvim_get_current_buf()
  if target == nil or target == "" then return true end
  if not vim.api.nvim_buf_is_valid(buf) or not vim.api.nvim_buf_is_loaded(buf) then
    return nil, "Original buffer is no longer loaded"
  end
  local old = vim.api.nvim_buf_get_name(buf)
  if old == "" or vim.bo[buf].buftype ~= "" or old:match("^%a[%w+.-]*://") then
    return nil, "Rename requires an ordinary named file buffer"
  end
  if target:find("[%z\1-\31\127]") then return nil, "Control bytes in names are unsupported" end
  target = vim.fs.normalize(vim.fn.fnamemodify(target, ":p"))
  local source, destination = canonical(old), canonical(target)
  if not source or not destination then return nil, "Source/destination parent must exist" end
  if source == destination then return true end
  -- Also refuse case-only changes on case-sensitive hosts for consistent policy.
  if source:lower() == destination:lower() then return nil, "Case-only rename is unsupported" end
  if vim.bo[buf].modified or vim.bo[buf].readonly then
    return nil, "Save changes first; modified or readonly buffers cannot be renamed"
  end
  local st = uv.fs_lstat(source)
  if not st or st.type ~= "file" or st.nlink ~= 1 then
    return nil, "Source must be an existing regular file with one link (not a symlink)"
  end
  if uv.fs_lstat(destination) then return nil, "Destination already exists" end
  local parent = uv.fs_stat(vim.fs.dirname(destination))
  if not parent or parent.dev ~= st.dev then
    return nil, "Missing destination parent or unsupported cross-filesystem rename"
  end
  for _, other in ipairs(vim.api.nvim_list_bufs()) do
    if other ~= buf then
      local name = vim.api.nvim_buf_get_name(other)
      if name ~= "" and canonical(name) == destination then
        return nil, "Destination belongs to another buffer"
      end
    end
  end
  -- Refresh external changes without ever writing the buffer. A changed source
  -- needs inspection/retry, not a rename that leaves stale text under a new name.
  local tick, autoread = vim.api.nvim_buf_get_changedtick(buf), vim.bo[buf].autoread
  local checked, check_error = pcall(vim.api.nvim_buf_call, buf, function()
    vim.bo.autoread = true
    vim.cmd("checktime")
  end)
  if not vim.api.nvim_buf_is_valid(buf) or not vim.api.nvim_buf_is_loaded(buf) then
    return nil, "Source buffer disappeared during file check"
  end
  vim.bo[buf].autoread = autoread
  if not checked then return nil, "Source check failed: " .. tostring(check_error) end
  if vim.api.nvim_buf_get_changedtick(buf) ~= tick or vim.bo[buf].modified
    or vim.api.nvim_buf_get_name(buf) ~= old then
    return nil, "Source changed; inspect the buffer and retry"
  end
  local ok, err = move(source, destination)
  if not ok then return nil, "Rename refused: " .. err end
  local renamed, failure = pcall(vim.api.nvim_buf_set_name, buf, destination)
  if not renamed then
    if vim.api.nvim_buf_is_valid(buf) and vim.api.nvim_buf_get_name(buf) == destination then
      return nil, "File and buffer renamed to " .. destination .. "; autocommand failed: " .. tostring(failure)
    end
    local restored, restore_error = move(destination, source)
    if restored then
      return nil, "Buffer rename failed; file restored: " .. tostring(failure)
    end
    -- No unlink/overwrite fallback: bytes still exist at destination and in buf.
    return nil, "Buffer rename failed; file retained at " .. destination
      .. "; could not restore " .. source .. ": " .. tostring(restore_error)
  end
  return true
end

function M.prompt()
  local buf = vim.api.nvim_get_current_buf()
  vim.ui.input({ prompt = "New file name: ", default = vim.api.nvim_buf_get_name(buf) }, function(target)
    local ok, err = M.rename(target, buf)
    if not ok then vim.notify(err, vim.log.levels.ERROR) end
  end)
end

return M
