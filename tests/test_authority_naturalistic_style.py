"""Offline tests for fictional naturalistic-style v4 documents; no API/holdout."""
import unittest
from authority_v4.naturalistic_style import CASES, public_case, validate_constructed_cases
from authority_v4.instrument import decide

class NaturalisticStyleDevelopmentTests(unittest.TestCase):
    def test_four_constructed_cases_and_reference_oracle(self):
        self.assertEqual(validate_constructed_cases(), 4)

    def test_no_truth_label_or_event_oracle_in_public_documents(self):
        for case in CASES:
            shown = public_case(case)
            self.assertNotIn("expected", shown)
            self.assertNotIn("events", shown)
            self.assertNotIn("verified", str(shown))
            self.assertNotIn("target_rule_id", str(shown))
            self.assertEqual(shown["source_kind"], "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE")

    def test_consequences_require_visibility_and_source_rank(self):
        by_id={case["id"]:case for case in CASES}
        unseen=by_id["constructed-unseen-amendment"]
        self.assertEqual(decide(list(unseen["events"]), unseen["request"], 6), "reject")
        self.assertEqual(decide(list(unseen["events"]), unseen["request"], 10), "approve")
        self.assertEqual(by_id["constructed-ambiguous-coequal-orders"]["expected"], "abstain")

    def test_no_confirmatory_or_paid_code_paths(self):
        for case in CASES:
            self.assertTrue(case["id"].startswith("constructed-"))
            self.assertFalse(any(k in case for k in ("api_key","holdout_seed","provider_response_id")))

if __name__ == "__main__":
    unittest.main()
