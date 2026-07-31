import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "strategy-watchdog" / "scripts" / "check_occ_conflicts.py"
SPEC = importlib.util.spec_from_file_location("check_occ_conflicts", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckOccConflictsTest(unittest.TestCase):
    def classify(self, existing):
        return MODULE.classify(
            {
                "strategy_id": "target",
                "idempotency_key": "target-20260731-QQQ",
                "candidate": [
                    {"occ": "QQQ260731P00677000", "side": "sell"},
                    {"occ": "QQQ260731P00667000", "side": "buy"},
                ],
                "existing": existing,
            }
        )

    def test_unrelated_other_strategy_order_does_not_block(self):
        result = self.classify(
            [{"occ": "SPY260731C00640000", "side": "sell", "strategy_id": "other"}]
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(len(result["unrelated"]), 2)

    def test_same_occ_same_side_other_strategy_does_not_block(self):
        result = self.classify(
            [{"occ": "QQQ260731P00677000", "side": "short", "strategy_id": "other"}]
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(len(result["same_direction"]), 1)

    def test_same_occ_opposite_side_blocks_netting(self):
        result = self.classify(
            [{"occ": "QQQ260731P00677000", "side": "buy", "strategy_id": "other"}]
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(len(result["opposite_conflicts"]), 1)

    def test_same_strategy_idempotency_key_is_duplicate(self):
        result = self.classify(
            [
                {
                    "occ": "QQQ260731P00677000",
                    "side": "sell",
                    "strategy_id": "target",
                    "idempotency_key": "target-20260731-QQQ",
                }
            ]
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(len(result["duplicates"]), 1)


if __name__ == "__main__":
    unittest.main()
