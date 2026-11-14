"""Public development narrative fixtures, never independently human adjudicated."""
import json
import unittest
from authority_v4.casebook import assemble,CASES

class P07Casebook(unittest.TestCase):
    def test_twelve_cases_and_separate_references(self):
        public,reference=assemble()
        self.assertEqual(len(public),12)
        self.assertEqual(len(reference),12)
        self.assertEqual({x["case_id"] for x in public},{x["case_id"] for x in reference})
        self.assertTrue(all(x["human_adjudicated"] is False for x in reference))
        self.assertTrue(all(x["source_authenticity_proved"] is False for x in reference))
        self.assertTrue(all(x["simulator_reference"]==x["reference_action"] for x in reference))
        self.assertEqual(len(set(x[0] for x in CASES)),12)
    def test_no_gold_or_family_in_public_text(self):
        public,reference=assemble()
        blob=json.dumps(public,sort_keys=True)
        for banned in ("reference_action","simulator_reference","fixture_family",
                       "human_adjudicated","adjudicator_id","answer_key"):
            self.assertNotIn(banned,blob)
        for case in public:
            self.assertNotIn("reference_action",json.dumps(case))
    def test_deterministic_and_no_holdout(self):
        self.assertEqual(assemble(),assemble())
        for split in ("pilot","confirmatory","holdout"):
            with self.assertRaisesRegex(ValueError,"P07_ONLY_PUBLIC_DEVELOPMENT_ALLOWED"):
                assemble(split=split)
if __name__=="__main__":
    unittest.main()
