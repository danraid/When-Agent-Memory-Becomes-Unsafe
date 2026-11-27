"""R01 chronological public-source replay negative controls."""
import json
import unittest
from scripts.r01_replay_case002_008_chronology import CASES,audit

class TimelineTests(unittest.TestCase):
    def fixture(self):
        docs={}
        for cid,(pr,issue) in CASES.items():
            docs[f"https://api.github.com/repos/python/cpython/pulls/{pr}"]={
                "number":pr,"created_at":"2025-10-21T00:00:00Z",
                "closed_at":"2026-05-18T12:00:00Z",
                "merged_at":None,
                "base":{"repo":{"full_name":"python/cpython"}},
                "html_url":f"https://github.com/python/cpython/pull/{pr}"}
            docs[f"https://api.github.com/repos/python/cpython/issues/{issue}"]={
                "number":issue,"created_at":"2025-10-20T00:00:00Z",
                "html_url":f"https://github.com/python/cpython/issues/{issue}"}
        return docs
    def test_two_real_records_do_not_become_gold(self):
        docs=self.fixture()
        report=audit(fetch=lambda url:json.dumps(docs[url]).encode())
        self.assertEqual(report["real_event_pairs"],2)
        self.assertEqual(report["qualifying_new_gold_actions"],0)
        self.assertFalse(report["historical_body_immutability_proven"])
        self.assertTrue(all(x["operational_gold_action"] is None for x in report["cases"]))
    def test_future_issue_fails(self):
        docs=self.fixture()
        u="https://api.github.com/repos/python/cpython/issues/140344"
        docs[u]["created_at"]="2026-11-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"ISSUE_WAS_CREATED_AFTER_PR"):
            audit(fetch=lambda url:json.dumps(docs[url]).encode())
    def test_wrong_original_repo_fails(self):
        docs=self.fixture()
        u="https://api.github.com/repos/python/cpython/pulls/133654"
        docs[u]["base"]["repo"]["full_name"]="untrusted/fork"
        with self.assertRaisesRegex(ValueError,"NON_ORIGINAL_PR"):
            audit(fetch=lambda url:json.dumps(docs[url]).encode())
