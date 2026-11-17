"""Posthoc chair recovery cannot rewrite original four invalid votes or author decision."""
import json
import unittest
from scripts.p10_ai_scientific_independent_panel import chair_prompt
from scripts.p10_recover_original_ai_chair_once import valid_chair, ORIGINAL_RUN, ORIGINAL_ARTIFACT

class P10RecoveryTests(unittest.TestCase):
    def test_exact_original_identities_and_null_author_verdict(self):
        self.assertEqual(ORIGINAL_RUN,44009705898)
        self.assertEqual(ORIGINAL_ARTIFACT,14296356384)
        d={"advisory_recommendation":"major_revision",
           "critical_objections":["Original source science requires independent review"],
           "minority_positions":["A reviewer favoured exploratory circulation"],
           "required_repairs":["Obtain genuine reference labels"],
           "confidence_caveat":"This AI role is not a human reviewer",
           "author_final_decision":None,
           "human_independent_review_completed":False,
           "confirmatory_validated":False}
        self.assertEqual(valid_chair(json.dumps(d)),d)
        with self.assertRaisesRegex(ValueError,"FALSE_SCIENCE"):
            valid_chair(json.dumps(dict(d,author_final_decision="approved")))

    def test_absent_original_review_does_not_crash_chair(self):
        row={"reviewer_id":"science","requested_model":"example/model",
             "response_id":"original-id","review":None,
             "original_response_text":"critical original evidence, invalid strict schema",
             "error":"ORIGINAL_REVIEW_NOT_SINGLE_JSON"}
        prompt=chair_prompt("a"*64,[row])
        self.assertIn("parsed_recommendation",prompt)
        self.assertIn("null",prompt)
        self.assertIn("ORIGINAL_REVIEW_NOT_SINGLE_JSON",prompt)

if __name__=="__main__":
    unittest.main()
