vim.g.mapleader = "\\"

vim.keymap.set("n", "<leader>f", function()
  require("mini.pick").builtin.files({ tool = "git" }, {
    source = { cwd = vim.fn.getcwd() },
  })
end, { desc = "Find Git files in current directory" })
