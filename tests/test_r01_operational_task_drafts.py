"""Original comparator logic and R01 task isolation contracts."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
TASKS=ROOT/"fixtures/R01_SOURCE_BACKED_OPERATIONAL_TASK_DRAFTS_V1.json"

class R01TaskDraftTests(unittest.TestCase):
    def test_no_gold_and_only_prior_sources(self):
        data=json.loads(TASKS.read_text())
        self.assertEqual(data["task_count"],3)
        self.assertEqual(data["qualified_action_labels"],0)
        from datetime import datetime
        def d(s): return datetime.fromisoformat(s.replace("Z","+00:00"))
        for c in data["cases"]:
            self.assertIsNone(c["correct_action"])
            self.assertFalse(c["reference_material_visible_to_model"])
            self.assertEqual(c["independent_adjudication_status"],"NOT_DONE")
            self.assertTrue(all(d(s["published"])<=d(c["time"]) for s in c["sources"]))
        self.assertFalse(data["confirmatory_eligible"])

    def test_task_prompts_do_not_preassign_action_labels(self):
        data=json.loads(TASKS.read_text())
        for c in data["cases"]:
            self.assertNotIn("gold_action",c)
            self.assertNotIn("expected_action",c)
            self.assertGreater(len(c["action"]),60)

if __name__=="__main__":
    unittest.main()
