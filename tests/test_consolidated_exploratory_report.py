"""Offline final editorial report contract, not peer review or science approval."""
import unittest
from scripts.check_consolidated_exploratory_report import verify


class ConsolidatedReportTests(unittest.TestCase):
    def test_claim_to_evidence_and_explicit_non_promotion(self):
        r=verify()
        self.assertTrue(r["passed"],r["checks"])
        self.assertTrue(all(r["checks"].values()))
        self.assertFalse(r["scientifically_approved"])
        self.assertFalse(r["independently_peer_reviewed"])
        self.assertFalse(r["human_case_gold_qualified"])
        self.assertFalse(r["confirmatory_touched"])
        self.assertFalse(r["journal_submission"])
        self.assertEqual(len(r["manuscript_sha256"]),64)
        self.assertEqual(len(r["claim_ledger_sha256"]),64)


if __name__=="__main__":
    unittest.main()
