"""Provenance-only P07b candidate tests. No invented human judgements."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class P07SourceCandidateTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/"protocol/P07_PUBLIC_SOURCE_CANDIDATES.json").read_text())
    def test_six_real_public_source_pairs_and_two_repositories(self):
        pairs=self.data["paired_documents"]
        self.assertEqual(len(pairs),6)
        self.assertEqual({x["repository"] for x in pairs},{"python/peps","rust-lang/rfcs"})
        self.assertEqual(len({x["id"] for x in pairs}),6)
        for p in pairs:
            self.assertEqual(len(p["revision"]),40)
            self.assertEqual(len(p["source_blob_sha"]),40)
            self.assertEqual(len(p["target_blob_sha"]),40)
            self.assertIsNone(p["reference_action"])
            self.assertEqual(p["human_review_status"],"PENDING")
            self.assertFalse(p["authority_chain_adjudicated"])
            self.assertFalse(p["effective_time_verified"])
    def test_no_confirmatory_or_human_gold(self):
        self.assertEqual(self.data["split"],"public_development_source_review_only")
        self.assertFalse(self.data["private_holdout_touched"])
        self.assertTrue(self.data["not_a_multi_authority_task"])
        self.assertEqual(self.data["status"],"SOURCE_CANDIDATES_NOT_HUMAN_ADJUDICATED")

if __name__=="__main__":
    unittest.main()
