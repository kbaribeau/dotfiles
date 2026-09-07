#!/usr/bin/env python3
"""Opt-in local Codex discovery probe; no model turn, skill invocation, or live settings.

Uses documented app-server initialize/initialized and skills/list messages:
https://developers.openai.com/codex/app-server/
"""
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import tempfile
import time

from test_install import ROOT, SKILLS, fixture


def main():
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("Codex is required for this optional integration check")
    version = subprocess.check_output([codex, "--version"], text=True).strip()
    with tempfile.TemporaryDirectory(prefix=".dotfiles-codex-", dir=ROOT) as temp:
        root = Path(temp).resolve()
        repo, home, cwd = fixture(root)
        codex_home = home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        disabled = repo / "skills/consulting-principles/SKILL.md"
        config.write_text('[analytics]\nenabled = false\n[[skills.config]]\n'
                          f'path = {json.dumps(str(disabled))}\nenabled = false\n')
        before = config.read_bytes()
        managed = home / ".agents/skills/fixture-managed"
        managed.mkdir(parents=True)
        (managed / "SKILL.md").write_text(
            "---\nname: fixture-managed\ndescription: Inert discovery fixture.\n---\n")
        # Do not inherit real credentials, tool-directory overrides, or configuration.
        env = {"PATH": os.environ["PATH"], "HOME": str(home),
               "CODEX_HOME": str(codex_home), "TMPDIR": str(root),
               "XDG_CONFIG_HOME": str(home / ".config"),
               "XDG_CACHE_HOME": str(home / ".cache"),
               "XDG_DATA_HOME": str(home / ".local/share")}
        subprocess.run([str(repo / "install.sh"), "--home", str(home)],
                       cwd=cwd, env=env, check=True, capture_output=True)
        assert config.read_bytes() == before
        # stderr remains private to the fixture and is never printed (may contain
        # ambient admin configuration). No thread/start or turn/start is sent.
        with (root / "server.stderr").open("w") as errors:
            server = subprocess.Popen([codex, "app-server", "--listen", "stdio://"],
                                      cwd=cwd, env=env, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=errors)
            selector = selectors.DefaultSelector()
            selector.register(server.stdout, selectors.EVENT_READ)
            buffer = b""

            def send(message):
                server.stdin.write((json.dumps(message) + "\n").encode())
                server.stdin.flush()

            def response(request_id):
                nonlocal buffer
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        message = json.loads(line)
                        if message.get("id") == request_id:
                            if "error" in message:
                                raise RuntimeError("Codex discovery RPC failed (details suppressed)")
                            return message["result"]
                    if selector.select(max(0, deadline - time.monotonic())):
                        chunk = os.read(server.stdout.fileno(), 65536)
                        if not chunk:
                            raise RuntimeError("Codex app-server closed before discovery completed")
                        buffer += chunk
                raise TimeoutError("Codex discovery timed out")

            try:
                send({"method": "initialize", "id": 1, "params": {
                    "clientInfo": {"name": "dotfiles_fixture_check", "version": "1.0"}}})
                response(1)
                send({"method": "initialized", "params": {}})
                send({"method": "skills/list", "id": 2,
                      "params": {"cwds": [str(cwd)], "forceReload": True}})
                result = response(2)
                data = next(item for item in result["data"] if item["cwd"] == str(cwd))
                skills = {item["name"]: item for item in data["skills"]}
                for name in SKILLS:
                    skill = skills[name]
                    expected = repo / "skills" / name / "SKILL.md"
                    assert skill["path"] == str(expected), "Expected canonical fixture skill path"
                    assert skill["scope"] == "user"
                    assert skill["enabled"] == (name != "consulting-principles")
                    # Filesystem proof from both the reported path and linked path.
                    # This is not a model-driven/sandboxed supporting-file read.
                    ref, = re.findall(r"\]\((references/[^)]+)\)", expected.read_text())
                    linked = home / ".agents/skills" / name
                    assert (linked / "SKILL.md").read_bytes() == expected.read_bytes()
                    assert (linked / ref).read_bytes() == (Path(skill["path"]).parent / ref).read_bytes()
                assert "fixture-managed" in skills
                assert config.read_bytes() == before
            finally:
                selector.close()
                server.stdin.close()
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=10)
                server.stdout.close()
        print(f"{version}: all three user skills discovered at canonical fixture paths; "
              "references readable; disabled setting and managed skill preserved. "
              "No model turn or skill invocation.")


if __name__ == "__main__":
    main()
