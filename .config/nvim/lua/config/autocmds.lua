local group = vim.api.nvim_create_augroup("DotfilesCursor", { clear = true })
vim.api.nvim_create_autocmd("BufReadPost", {
  group = group,
  callback = function(event)
    if vim.bo[event.buf].buftype ~= "" or vim.fn.expand("%:p"):match("^%a[%w+.-]*://") then return end
    local mark = vim.api.nvim_buf_get_mark(event.buf, '"')
    if mark[1] > 1 and mark[1] <= vim.api.nvim_buf_line_count(event.buf) then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})
-- Bundled filetype/syntax/indent and omnifuncs are the owners. No legacy global
-- FileType omnifunc hooks, XML guard, custom extension aliases or auto-reload.
