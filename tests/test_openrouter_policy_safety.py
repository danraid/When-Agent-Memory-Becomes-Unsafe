"""Policy-safety multi-model benchmark is bounded and gold-isolated."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from study.openrouter_policy_safety import load_config, indicators, SafetyPilotError
from study.tasks import generate_episode
from study.prompts import decision_prompt, compaction_prompt, ALL_CONDITIONS


class PolicySafetyTests(unittest.TestCase):
    def test_model_matrix_is_predeclared_finite_and_development_only(self):
        c, digest = load_config(Path("study/openrouter_policy_models.json"))
        self.assertEqual(len(c["decision_models"]), 4)
        self.assertFalse(c["confirmatory_allowed"])
        self.assertLessEqual(c["episodes"] * ((c["steps"]-1)//3 + c["steps"]*4*4),
                             c["max_calls"])
        self.assertEqual(len(digest), 64)

    def test_reference_labels_not_in_compactor_or_decision(self):
        ep=generate_episode("WAMBU-OPENROUTER-POLICY-DEVELOPMENT-V1-PUBLIC",
                            "development",0,18)
        for item in ep["items"]:
            for arm in ("full_history","recent_window","recursive_summary","pinned_ledger"):
                prompt=decision_prompt(item,arm,"summary without gold")
                self.assertNotIn("reference_action",prompt)
                self.assertNotIn("reference_policy",prompt)
            prompt=compaction_prompt("summary",item["history_before"])
            self.assertNotIn("reference_action",prompt)
            self.assertNotIn("reference_policy",prompt)

    def test_expected_arm_pairings_are_enforced(self):
        c,_=load_config(Path("study/openrouter_policy_models.json"))
        with self.assertRaisesRegex(SafetyPilotError,"MISSING_OR_EXTRANEOUS"):
            indicators([],c["decision_models"],c["episodes"],c["steps"])


if __name__ == "__main__":
    unittest.main()
