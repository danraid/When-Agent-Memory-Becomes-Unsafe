"""Source and split guards for the expanded R02 development diagnostic."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class R02DevelopmentContract(unittest.TestCase):
    def test_fixture_is_unlabelled_and_bounded(self):
        d=json.loads((ROOT/"fixtures/R02_EXPANDED_LIVE_DEV_2026-11-18.json").read_text())
        self.assertEqual(d["schema"],"WAMBU-R02-EXPANDED-DEV-CASES-V1")
        self.assertEqual(len(d["classifier_cases"]),20)
        self.assertEqual(len(d["safety_margin_cases"]),6)
        self.assertFalse(d["original_benchmark_equivalent"])
        self.assertEqual(len({x["id"] for x in d["classifier_cases"]+d["safety_margin_cases"]}),26)
        for x in d["classifier_cases"]+d["safety_margin_cases"]:
            self.assertNotIn("gold",x)
            self.assertNotIn("correct_action",x)
            self.assertNotIn("independent_adjudication",x)
            self.assertTrue(x["text"])
    def test_live_run_requires_pinned_octen_lane(self):
        code=(ROOT/"scripts/r02_expanded_octen_dev.py").read_text()
        self.assertIn('R02_REQUIRE_LANE',code)
        self.assertIn('"OCTEN_VENDOR_AND_ORIGINAL_LLM"',code)
        self.assertIn("original_paper_benchmark_reproduced",code)
        self.assertIn("source_safety_margin_sha256",code)
        self.assertNotIn("ADAPTED_OPENROUTER",code)
if __name__=="__main__":
    unittest.main()
