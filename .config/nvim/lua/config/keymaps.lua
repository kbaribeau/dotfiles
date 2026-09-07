vim.g.mapleader = "\\"

vim.keymap.set("n", "<leader>f", function()
  require("mini.pick").builtin.files({ tool = "git" }, {
    source = { cwd = vim.fn.getcwd() },
  })
end, { desc = "Find Git files in current directory" })

local map = vim.keymap.set
for key, direction in pairs({ h = "h", j = "j", k = "k", l = "l" }) do
  map("n", "<C-" .. key .. ">", "<C-w>" .. direction, { desc = "Move to adjacent split" })
end
map("n", "<C-Right>", "<Cmd>tabnext<CR>")
map("n", "<C-Left>", "<Cmd>tabprevious<CR>")
map("c", "%%", function() return vim.fn.fnameescape(vim.fn.expand("%:p:h") .. "/") end, { expr = true })
map("c", "%f", function() return vim.fn.fnameescape(vim.fn.expand("%:p")) end, { expr = true })
map("n", "<leader>e", ":edit %%", { remap = true, desc = "Edit beside current file" })
map("n", "<leader>v", ":view %%", { remap = true, desc = "View beside current file" })
map("n", "<leader>h", function() vim.o.hlsearch = not vim.o.hlsearch end)
map("n", "<leader>l", function() vim.wo.cursorline = not vim.wo.cursorline end)
map("n", "<leader>r", function() require("config.workflows").refresh() end)
map("n", "<leader>s", function() require("config.sessions").save() end)
map("n", "<leader>ls", function() require("config.sessions").load() end)
map("n", "<F1>", "<Esc>")
map("n", "Q", "<Nop>")
map({ "n", "x", "o" }, "K", "<Nop>")

map("n", "<leader><leader>", function() require("config.workflows").save_all(false) end)
map("n", "<C-z>", function() require("config.workflows").save_all(true) end)
map("i", "<leader><leader>", '<Esc><Cmd>lua require("config.workflows").save_all(false)<CR>')
map("i", "<C-z>", '<Esc><Cmd>lua require("config.workflows").save_all(true)<CR>')
