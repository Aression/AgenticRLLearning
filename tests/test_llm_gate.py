"""The LLM kill switch must block model calls without breaking offline commands."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import llm_gate  # noqa: E402


class LlmGateTests(unittest.TestCase):
    def test_disabled_policy_exits_with_paused_code(self):
        with patch.object(llm_gate, "llm_policy", return_value={"enabled": False, "disabledReason": "test pause"}):
            with self.assertRaises(SystemExit) as ctx:
                llm_gate.require_llm_enabled("cards")
        self.assertEqual(ctx.exception.code, llm_gate.PAUSED_EXIT_CODE)

    def test_enabled_policy_passes(self):
        with patch.object(llm_gate, "llm_policy", return_value={"enabled": True}):
            llm_gate.require_llm_enabled("cards")  # must not raise

    def test_missing_policy_defaults_to_enabled(self):
        with patch.object(llm_gate, "llm_policy", return_value={}):
            llm_gate.require_llm_enabled("cards")  # must not raise

    def test_env_override_wins_both_directions(self):
        with patch.dict(os.environ, {llm_gate.ENV_OVERRIDE: "1"}):
            self.assertTrue(llm_gate.llm_enabled({"enabled": False}))
        with patch.dict(os.environ, {llm_gate.ENV_OVERRIDE: "0"}):
            self.assertFalse(llm_gate.llm_enabled({"enabled": True}))

    def test_repository_policy_is_readable(self):
        # The pause itself is temporary state, so it is reported rather than asserted:
        # a test that requires "paused" would fail the moment the switch is resumed.
        policy = llm_gate.llm_policy()
        self.assertIn("enabled", policy)
        self.assertIsInstance(llm_gate.llm_enabled(policy), bool)


if __name__ == "__main__":
    unittest.main()
