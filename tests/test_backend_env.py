#!/usr/bin/env python3
"""Backend environment regression tests for Quick Ask."""

from __future__ import annotations

import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import quick_ask_backend as backend


class ProviderRuntimeEnvTests(unittest.TestCase):
    def test_provider_runtime_env_includes_resolved_command_dirs(self) -> None:
        with mock.patch.object(backend, "subscription_only_env", return_value={}):
            with mock.patch.object(backend, "login_shell_path_entries", return_value=("/Users/test/.nvm/versions/node/v24/bin",)):
                with mock.patch.object(backend, "command_path") as command_path:
                    command_path.side_effect = lambda name: {
                        "gemini": "/opt/homebrew/bin/gemini",
                        "node": "/Users/test/.nvm/versions/node/v24/bin/node",
                    }.get(name)

                    env = backend.provider_runtime_env("gemini", "node")
                    path_entries = env["PATH"].split(":")

                    self.assertIn("/opt/homebrew/bin", path_entries)
                    self.assertIn("/Users/test/.nvm/versions/node/v24/bin", path_entries)


if __name__ == "__main__":
    unittest.main(verbosity=2)
