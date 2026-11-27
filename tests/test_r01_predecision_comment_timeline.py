"""Fail-closed chronological source constraints for R01 cases 002 and 008."""
import json
from datetime import datetime
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"evidence/R01_CASE002_008_PREDECISION_COMMENT_TIMELINE_2026-11-19.json"


def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))


class R01TimedSourceCases(unittest.TestCase):
    def test_source_boundaries_and_no_gold(self):
        d=json.loads(DATA.read_text())
        self.assertEqual({c["id"] for c in d["cases"]},{"P07D-CODE-002","P07D-CODE-008"})
        for c in d["cases"]:
            event=dt(c["pr_created"])
            self.assertLess(dt(c["issue_created"]),event)
            self.assertGreater(dt(c["current_issue_body_last_updated"]),event)
            self.assertIsNone(c["independent_correct_action"])
            for x in c["source_comments"]:
                self.assertEqual(x["pre_pr"],dt(x["created"])<=event)
                if x.get("edited") and x["pre_pr"]:
                    self.assertLessEqual(dt(x["updated"]),event)
        self.assertEqual(d["gate"]["qualified_operational_actions"],0)
        self.assertFalse(d["gate"]["holdout_access"])
        self.assertFalse(d["gate"]["external_submission"])
    def test_reviewer_feedback_is_post_PR_for_002(self):
        c=next(x for x in json.loads(DATA.read_text())["cases"] if x["id"].endswith("002"))
        self.assertTrue(all(not k["pre_pr"] for k in c["source_comments"]))
        self.assertTrue(c["later_policy_debate_for_followup_decision"])

if __name__=="__main__":
    unittest.main()
