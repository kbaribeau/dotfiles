"""Exercise isolated startup workflows with a synthetic private override."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import test_install
import test_nvim_picker

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("nvim"), "requires Neovim")
class FixtureIsolationTests(unittest.TestCase):
    def exercise(self, case):
        with tempfile.TemporaryDirectory(prefix=".nvim-isolation-", dir=ROOT) as tmp:
            root = Path(tmp)
            source = root / "synthetic-config"
            copytree = shutil.copytree
            copytree(ROOT / "packages/nvim/.config/nvim", source,
                     ignore=shutil.ignore_patterns("local.lua"))
            marker = root / "override-executed"
            (source / "local.lua").write_text(
                'vim.fn.writefile({"executed"}, ' + json.dumps(str(marker)) + ')\n')
            destinations = []

            def copy_config(src, dst, *args, **kwargs):
                if Path(src) == ROOT / "packages/nvim/.config/nvim":
                    src = source
                    destinations.append(Path(dst))
                    result = copytree(src, dst, *args, **kwargs)
                    self.assertFalse((Path(dst) / "local.lua").exists())
                    self.assertTrue((Path(dst) / "init.lua").is_file())
                    return result
                return copytree(src, dst, *args, **kwargs)

            result = unittest.TestResult()
            with patch.object(shutil, "copytree", side_effect=copy_config):
                case.run(result)
            self.assertFalse(result.skipped, result.skipped)
            self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
            self.assertEqual(len(destinations), 1)
            self.assertFalse(marker.exists())

    def test_installer_excludes_private_override(self):
        self.exercise(test_install.InstallerTests("test_nvim_headless_startup_isolated"))

    @unittest.skipUnless(os.environ.get("RUN_NVIM_PICKER_TESTS") == "1" and
                         shutil.which("git"), "requires opt-in real picker coverage")
    def test_picker_excludes_private_override(self):
        self.exercise(test_nvim_picker.PickerIntegrationTests("test_real_git_picker"))


if __name__ == "__main__":
    unittest.main()
