import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "strategy-watchdog" / "scripts" / "launch_watchdog.py"
SPEC = importlib.util.spec_from_file_location("launch_watchdog", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StrategyWatchdogPromptTest(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "strategy_ids": ["strategy_a"],
            "environment": "live",
            "account_profile": "shared_live",
            "entry_at": "2026-07-31T10:30:00-04:00",
            "workspace": "/workspace/example",
            "evidence_dir": "/workspace/example/reports/watchdog",
            "allow_repair": True,
        }

    def test_post_prompt_prioritizes_repair_and_execution(self):
        prompt = MODULE.prompt_for(self.manifest, "post", Path("/tmp/manifest.json"))

        self.assertIn("primary job is to restore and complete", prompt)
        self.assertIn("fix in-scope scheduler, process, configuration, and code defects", prompt)
        self.assertIn("explicitly amends the\nentry/catch-up window, price tolerance", prompt)
        self.assertIn("ExecutionGateway/operator-recovery entry point", prompt)
        self.assertNotIn("occur inside the original\nentry window", prompt)
        self.assertNotIn("classify STOPPED_SAFE", prompt)

    def test_post_prompt_uses_occ_side_not_global_account_occupancy(self):
        prompt = MODULE.prompt_for(self.manifest, "post", Path("/tmp/manifest.json"))

        self.assertIn("Do not use broad account occupancy as a collision gate", prompt)
        self.assertIn("unrelated contracts do not conflict", prompt)
        self.assertIn("same-OCC,\nsame-side exposure may proceed", prompt)
        self.assertIn("same-OCC opposite-side", prompt)
        self.assertIn("for this strategy/idempotency key", prompt)

    def test_prompt_keeps_attribution_and_risk_controls(self):
        prompt = MODULE.prompt_for(self.manifest, "post", Path("/tmp/manifest.json"))
        normalized = " ".join(prompt.split())

        self.assertIn("never use a raw broker SDK", prompt)
        self.assertIn("strategy ownership or risk controls", prompt)
        self.assertIn("Do not cancel or modify unrelated orders", normalized)


if __name__ == "__main__":
    unittest.main()
