"""PTY job control with a tiny fixture shell; no real shell/editor settings."""
import os
import pty
import re
import select
import signal
import sys
import time
import unittest
from test_nvim_config import NVIM, NvimFixture


@unittest.skipUnless(NVIM and sys.platform in ("darwin", "linux"), "requires Unix PTY and Neovim")
class TerminalTests(unittest.TestCase):
    def test_save_suspend_resume_normal_insert_and_swap(self):
        for mode in ("normal", "insert"):
            with self.subTest(mode=mode):
                fixture = NvimFixture()
                try:
                    self.exercise(fixture, mode)
                finally:
                    fixture.close()

    def exercise(self, fixture, mode):
        root = fixture.root
        for name in ("one.txt", "two.txt"):
            (root / name).write_text("before\n")
        bootstrap = root / "terminal-bootstrap.lua"
        bootstrap.write_text("vim.pack = {add=function() end}\n")
        start = root / "terminal-start.lua"
        start.write_text(r'''
for _, name in ipairs({"one.txt", "two.txt"}) do
  vim.cmd.edit(vim.fn.fnameescape(vim.env.TEST_ROOT .. "/" .. name))
  vim.api.nvim_buf_set_lines(0, 0, -1, false, {"changed " .. name})
  vim.cmd.preserve()
end
vim.fn.writefile({"ready"}, vim.env.TEST_ROOT .. "/ready")
''')
        shell, master = pty.fork()
        if shell == 0:
            # A distinct shell process group in the same controlling session makes
            # the editor's SIGTSTP non-orphaned, just like interactive job control.
            try:
                signal.signal(signal.SIGTTOU, signal.SIG_IGN)
                reader, writer = os.pipe()
                child = os.fork()
                if child == 0:
                    os.close(writer)
                    os.setpgid(0, 0)
                    os.read(reader, 1)  # Wait until the shell gives us the terminal.
                    os.close(reader)
                    for sig in (signal.SIGTSTP, signal.SIGTTIN, signal.SIGTTOU):
                        signal.signal(sig, signal.SIG_DFL)
                    os.execve(NVIM, [NVIM, "--cmd", "luafile " + str(bootstrap),
                                     "-c", "luafile " + str(start)], fixture.env)
                os.close(reader)
                os.setpgid(child, child)
                os.tcsetpgrp(0, child)
                (root / "editor-pid").write_text(str(child))
                os.write(writer, b"1")
                os.close(writer)
                while True:
                    _, status = os.waitpid(child, os.WUNTRACED)
                    if os.WIFSTOPPED(status):
                        with (root / "stopped").open("a") as output:
                            output.write(str(os.WSTOPSIG(status)) + "\n")
                        os.killpg(child, signal.SIGCONT)
                    else:
                        os._exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)
            except BaseException:
                os._exit(2)
        output = bytearray()
        reaped = False
        answered = 0
        queries = re.compile(rb"\x1b\[(?:0?c|6n)|\x1b\]11;\?(?:\x07|\x1b\\)")

        def drain():
            nonlocal answered
            if select.select([master], [], [], 0.03)[0]:
                try:
                    output.extend(os.read(master, 65536))
                    # Neovim waits for a terminal DA acknowledgement while suspending.
                    # Answer only the harmless terminal queries used by this fixture.
                    for match in queries.finditer(output, answered):
                        query = match.group()
                        response = (b"\x1b]11;rgb:0000/0000/0000\x07" if b"]11;" in query
                                    else b"\x1b[1;1R" if query.endswith(b"6n") else b"\x1b[?1;2c")
                        os.write(master, response)
                        answered = match.end()
                except OSError:
                    pass

        def wait(predicate):
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if predicate():
                    return
                drain()
            self.fail("PTY deadline: " + output.decode(errors="replace")[-3000:])

        try:
            wait(lambda: (root / "ready").exists())
            # A second isolated process observes swap without touching Vim state.
            if mode == "normal":
                result = fixture.run(r'''
local hit = false
vim.api.nvim_create_autocmd("SwapExists", {callback=function() hit=true; vim.v.swapchoice="q" end})
pcall(edit, "one.txt")
assert(hit, "expected collision with the fixture editor's swap")
''')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            os.write(master, b"\x1a" if mode == "normal" else b"A insert\x1a")
            wait(lambda: (root / "stopped").exists())
            self.assertEqual((root / "one.txt").read_text(), "changed one.txt\n")
            self.assertEqual((root / "two.txt").read_text(),
                             "changed two.txt" + (" insert" if mode == "insert" else "") + "\n")
            # After resumption, use :qa (not forced) to prove no dirty buffer remains.
            os.write(master, b":qa\r")
            status = None
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                pid, status = os.waitpid(shell, os.WNOHANG)
                if pid:
                    reaped = True
                    break
                drain()
            self.assertTrue(reaped, output.decode(errors="replace")[-3000:])
            self.assertTrue(os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0)
            stops = (root / "stopped").read_text().splitlines()
            self.assertEqual(len(stops), 1)
        finally:
            if not reaped:
                pid_file = root / "editor-pid"
                if pid_file.exists():
                    try:
                        os.killpg(int(pid_file.read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                try:
                    os.kill(shell, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                os.waitpid(shell, 0)
            os.close(master)


if __name__ == "__main__":
    unittest.main()
