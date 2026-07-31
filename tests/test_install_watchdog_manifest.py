import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "strategy-watchdog" / "scripts" / "install_watchdog.py"


class StrategyWatchdogManifestTest(unittest.TestCase):
    def test_manifest_distinguishes_identity_from_operator_amendments(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            evidence = Path(tmp) / "evidence"
            workspace.mkdir()
            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--workspace",
                    str(workspace),
                    "--run-date",
                    "2026-07-31",
                    "--entry-time",
                    "10:30",
                    "--strategy-id",
                    "strategy_a",
                    "--account-profile",
                    "shared_live",
                    "--evidence-dir",
                    str(evidence),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads((evidence / "manifest.json").read_text())

        self.assertEqual(manifest["schema_version"], 2)
        self.assertIn("account_profile", manifest["immutable_execution_fields"])
        self.assertIn("direction", manifest["immutable_execution_fields"])
        self.assertNotIn("entry_at", manifest["immutable_execution_fields"])
        self.assertIn("catch_up_deadline", manifest["operator_amendable_fields"])
        self.assertIn("price_tolerance", manifest["operator_amendable_fields"])
        self.assertIn("package_count", manifest["operator_amendable_fields"])


if __name__ == "__main__":
    unittest.main()
