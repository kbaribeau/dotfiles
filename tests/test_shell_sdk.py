"""Exercise only the SDK initialization lines, never the full personal shell config."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("zsh"), "requires zsh")
class ShellSdkTests(unittest.TestCase):
    def test_optional_sdk_under_home_with_spaces(self):
        source = (ROOT / "packages/shell/.zshrc").read_text()
        lines = [line for line in source.splitlines() if "$HOME/google-cloud-sdk/" in line]
        self.assertEqual(len(lines), 2)
        self.assertNotIn("Downloads/google-cloud-sdk", source)
        with tempfile.TemporaryDirectory(prefix=".sdk-shell-", dir=ROOT) as tmp:
            home = Path(tmp) / "home with spaces"
            home.mkdir()
            env = {"HOME": str(home), "ZDOTDIR": str(home), "PATH": os.defpath}
            for installed in (False, True):
                with self.subTest(installed=installed):
                    if installed:
                        sdk = home / "google-cloud-sdk"
                        sdk.mkdir()
                        (sdk / "path.zsh.inc").write_text("export FIXTURE_SDK_PATH=yes\n")
                        (sdk / "completion.zsh.inc").write_text("export FIXTURE_SDK_COMPLETION=yes\n")
                    # Execute only the two reviewed initializer lines with inert stubs.
                    script = "\n".join(lines) + '\nprintf "%s/%s" "${FIXTURE_SDK_PATH-no}" "${FIXTURE_SDK_COMPLETION-no}"\n'
                    result = subprocess.run([shutil.which("zsh"), "-f", "-c", script],
                                            cwd=home, env=env, capture_output=True,
                                            text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "yes/yes" if installed else "no/no")


if __name__ == "__main__":
    unittest.main()
