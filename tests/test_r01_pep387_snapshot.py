"""R01 historical PEP 387 snapshots must precede the evaluated PRs."""
import json
from datetime import datetime
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
def dt(s):return datetime.fromisoformat(s.replace("Z","+00:00"))
class PEPHistory(unittest.TestCase):
 def test_snapshots_are_before_pr(self):
  v=json.loads((ROOT/"evidence/R01_PEP387_PREDECISION_IMMUTABLE_V1.json").read_text())
  self.assertEqual(v["qualified_action_gold"],0)
  self.assertFalse(v["confirmatory_holdout"])
  self.assertFalse(v["external_submission"])
  for x in v["cases"]:
   self.assertLess(dt(x["source_commit_time"]),dt(x["cutoff_utc"]))
   self.assertEqual(len(x["source_blob_sha"]),40)
   self.assertIn(x["last_source_commit"],x["source_url"])
   self.assertTrue(x["in_source"])
if __name__=="__main__":unittest.main()
