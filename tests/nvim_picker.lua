-- Exercise the configured mapping and real mini.pick, never a simulated picker.
local function test()
  assert(vim.fn.has("nvim-0.12") == 1, "Neovim 0.12+ required")
  assert(vim.v.errmsg == "", vim.v.errmsg)
  local pick = require("mini.pick")
  local mapping = vim.fn.maparg("\\f", "n", false, true)
  assert(type(mapping.callback) == "function", "backslash-f mapping missing")
  local plugin = vim.pack.get({ "mini.pick" })[1]
  assert(plugin.rev == "b27dc13b3d6dafc10e868b6ddc682cc4f047f4d1")
  assert(vim.startswith(plugin.path, vim.fn.stdpath("data") .. "/"))

  local function keys(text)
    vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes(text, true, false, true), "t", false)
  end
  local function run(inspect, finish)
    local failure
    vim.defer_fn(function()
      local ok, err = pcall(function()
        assert(vim.wait(5000, function()
          local state = pick.get_picker_state()
          return state and not state.is_busy and pick.get_picker_items() ~= nil
        end, 10), "picker did not finish collecting files")
        inspect()
      end)
      if not ok then failure = err end
      keys(ok and (finish or "<C-c>") or "<C-c>")
    end, 50)
    mapping.callback()
    assert(not failure, failure)
    assert(not pick.is_picker_active(), "picker did not close")
  end
  local function membership(expected)
    local actual = pick.get_picker_items()
    table.sort(actual)
    table.sort(expected)
    assert(vim.deep_equal(actual, expected), vim.inspect(actual))
  end
  local repo = vim.env.PICKER_REPO
  vim.cmd.cd(repo)
  local original = vim.api.nvim_get_current_buf()
  run(function()
    membership({ "tracked.txt", ".tracked", "ignored-tracked.txt", "sub/tracked.txt",
      "space name.txt", "café.txt", "review % # | [x].txt", ".untracked",
      ".hidden/visible.txt", "sub/new.txt", "sub/.hidden", ".gitignore" })
    assert(pick.get_picker_opts().source.cwd == repo)
  end)
  assert(vim.api.nvim_get_current_buf() == original, "cancel changed target buffer")
  assert(vim.fn.getcwd() == repo)

  -- Window-local cwd must narrow the Git list rather than expand to repository root.
  vim.cmd.lcd(repo .. "/sub")
  run(function()
    membership({ "tracked.txt", "new.txt", ".hidden" })
    assert(pick.get_picker_opts().source.cwd == repo .. "/sub")
  end, "<Esc>")
  assert(vim.fn.getcwd() == repo .. "/sub")
  vim.cmd.cd(repo)

  local function choose(name)
    run(function()
      pick.set_picker_query(vim.fn.split(name, "\\zs"))
      assert(vim.wait(5000, function()
        local matches = pick.get_picker_matches()
        return matches and matches.current == name
      end, 10), "did not match " .. name)
    end, "<CR>")
    assert(vim.api.nvim_buf_get_name(0) == repo .. "/" .. name,
      "opened wrong file: " .. vim.api.nvim_buf_get_name(0))
  end
  for _, name in ipairs({ "space name.txt", "café.txt", "review % # | [x].txt" }) do
    choose(name)
  end

  choose("tracked.txt")
  local dirty = vim.api.nvim_get_current_buf()
  vim.api.nvim_buf_set_lines(dirty, 0, -1, false, { "unsaved review note" })
  choose("space name.txt")
  assert(vim.api.nvim_buf_is_valid(dirty) and vim.bo[dirty].modified)
  assert(vim.api.nvim_buf_get_lines(dirty, 0, -1, false)[1] == "unsaved review note")
  -- Native opening preserves the unsaved buffer rather than discarding its text.

  vim.cmd.cd(vim.env.PICKER_EMPTY)
  local before_empty = vim.api.nvim_get_current_buf()
  run(function() membership({}) end, "<CR>")
  assert(vim.api.nvim_get_current_buf() == before_empty)

  -- Outside Git, an ordinary filesystem file must not trigger a fallback.
  vim.cmd.cd(vim.env.PICKER_OUTSIDE)
  run(function() membership({}) end)
  assert(vim.api.nvim_get_current_buf() == before_empty)
  print("PICKER INTEGRATION OK")
end

vim.schedule(function()
  local ok, err = pcall(test)
  if not ok then
    io.stderr:write(tostring(err) .. "\n")
    vim.cmd("cquit")
  else
    vim.cmd("qa!")
  end
end)
