#!/usr/bin/env python3
"""Fresh install smoke tests for Quick Ask."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_quick_ask_ui import QuickAskHarness, ROOT


class FreshInstallSmokeTests(unittest.TestCase):
    def test_builds_into_temp_home_and_gates_first_run_cleanly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="quick-ask-install-") as temp_home:
            temp_home_path = Path(temp_home)
            env = os.environ.copy()
            env["HOME"] = str(temp_home_path)
            env["QUICK_ASK_SKIP_LAUNCH_AGENT"] = "1"

            build = subprocess.run(
                ["./build-quick-ask"],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, msg=build.stderr or build.stdout)

            app_binary = temp_home_path / "Applications/Quick Ask.app/Contents/MacOS/Quick Ask"
            backend_path = temp_home_path / "Applications/Quick Ask.app/Contents/Resources/quick_ask_backend.py"
            shared_path = temp_home_path / "Applications/Quick Ask.app/Contents/Resources/quick_ask_shared.py"
            launch_agent = temp_home_path / "Library/LaunchAgents/app.quickask.mac.plist"

            self.assertTrue(app_binary.exists(), msg="Fresh build did not create the app binary.")
            self.assertTrue(backend_path.exists(), msg="Fresh build did not bundle the backend.")
            self.assertTrue(shared_path.exists(), msg="Fresh build did not bundle the shared helper.")
            self.assertTrue(launch_agent.exists(), msg="Fresh build did not create the LaunchAgent plist.")

            with QuickAskHarness(
                initial_setup_complete=False,
                seed_archive_dir=False,
                app_binary=app_binary,
                launch_agents=[],
                seed_defaults_enabled=False,
                extra_env={"HOME": str(temp_home_path)},
            ) as app:
                initial = app.read_state()
                self.assertFalse(initial["setupRequired"])
                self.assertTrue(initial["historyEnabled"])

                shown = app.command("show_panel")
                self.assertTrue(shown["panelVisible"])
                self.assertFalse(shown["settingsWindowVisible"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
