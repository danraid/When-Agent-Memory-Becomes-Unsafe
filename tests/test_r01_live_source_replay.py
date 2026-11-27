"""Recorded public primary-source snapshots for deterministic R01 replay tests."""
import json
from unittest import TestCase
from scripts.r01_replay_case001_authority import PR,SC,WG,SC_ISSUE,audit,APPROVAL,ACK

class Case001ReplayTests(TestCase):
    def source(self):
        base={"pr":{
           "number":133080,"created_at":"2025-04-28T11:41:01Z",
           "base":{"repo":{"full_name":"python/cpython"}},
           "body":"PEP 387 exception: https://github.com/python/steering-council/issues/288"},
           "sc":{"id":2828390956,"user":{"login":"emilyemorehouse"},
                 "body":APPROVAL,"created_at":"2025-04-24T17:46:12Z",
                 "updated_at":"2025-04-24T17:46:12Z"},
           "wg":{"body":ACK,"created_at":"2025-04-28T11:41:40Z"},
           "issue":{"number":288,"created_at":"2025-04-23T13:27:30Z"}}
        return {PR:base["pr"],SC:base["sc"],WG:base["wg"],SC_ISSUE:base["issue"]}

    def test_public_statement_before_change_but_no_gold(self):
        source=self.source()
        report=audit(fetch=lambda url:json.dumps(source[url]).encode())
        self.assertTrue(report["passed"],report["checks"])
        self.assertTrue(report["does_not_establish_agent_action_gold"])
        self.assertEqual(report["independent_human_experiment_reviews"],0)

    def test_future_or_edited_statement_fails(self):
        source=self.source()
        source[SC]["created_at"]="2025-04-29T00:00:00Z"
        self.assertFalse(audit(fetch=lambda url:json.dumps(source[url]).encode())["passed"])
        source=self.source()
        source[SC]["updated_at"]="2025-04-30T00:00:00Z"
        self.assertFalse(audit(fetch=lambda url:json.dumps(source[url]).encode())["passed"])

    def test_wrong_authority_or_quote_fails(self):
        source=self.source()
        source[SC]["body"]="Someone might approve someday"
        source[SC]["user"]["login"]="unknown"
        report=audit(fetch=lambda url:json.dumps(source[url]).encode())
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["sc_literal_approval"])
        self.assertFalse(report["checks"]["sc_comment_identity"])
