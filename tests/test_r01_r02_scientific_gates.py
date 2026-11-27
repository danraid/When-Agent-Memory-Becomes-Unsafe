"""R01/R02 regression: no synthetic promotion or false full-method parity."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.r01_qualify_public_policy_actions import inspect as r01_inspect
from scripts.r02_audit_original_kt_parity import assess as r02_assess, ROOT


class R01Tests(unittest.TestCase):
    def test_real_cases_are_documentary_only(self):
        report=r01_inspect()
        self.assertEqual(report["case_count"],8)
        self.assertEqual(report["direct_documentary_candidates"],5)
        self.assertEqual(report["excluded_current_document_pairs"],3)
        self.assertEqual(report["qualified_action_gold"],0)
        self.assertTrue(all(x["correct_action"] is None and
                            not x["confirmatory_eligible"] for x in report["cases"]))

    def test_no_self_attested_action_can_be_promoted(self):
        fabricated={"P07D-CODE-001":{
          "issuer":"someone","rule":"rule","published_at":"2020-01-01",
          "effective_at":"2020-01-01","scope":"all","exceptions":"none",
          "source_revision":"abcdef","source_sha256":"abc",
          "evidence_url":"https://example.invalid",
          "independently_source_verified":True,"policy_in_force_at_decision":True,
          "actor_permission_verified":True,"decision_action":"approve",
          "adjudication_provenance":"AI-generated assertion"}}
        report=r01_inspect(authorities=fabricated)
        row=next(x for x in report["cases"] if x["case_id"]=="P07D-CODE-001")
        self.assertEqual(row["correct_action"],None)
        self.assertEqual(row["admission_reason"],
                         "STRUCTURE_COMPLETE_AWAITING_INDEPENDENT_EVIDENCE_AUDIT")
        self.assertEqual(report["qualified_action_gold"],0)

    def test_future_or_nonmatching_rule_cannot_be_promoted(self):
        report=r01_inspect()
        excluded={x["case_id"] for x in report["cases"]
                  if not x["direct_topic_candidate"]}
        self.assertEqual(excluded,{"P07D-CODE-005","P07D-CODE-006","P07D-CODE-007"})


class R02Tests(unittest.TestCase):
    def test_original_comparator_is_not_misrepresented(self):
        r=r02_assess()
        self.assertFalse(r["full_original_knowledge_triage_replication"])
        self.assertFalse(r["original_cascade_executed"])
        self.assertEqual(r["new_model_calls"],0)
        self.assertGreaterEqual(len(r["missing_or_adapted_methods"]),6)
        self.assertEqual(r["strict_original_model_identity_required"]["encoder"],
                         "octen-embedding-8b")

    def test_missing_source_fails_closed(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"R02_SOURCE_OR_SPEC_MISSING"):
                r02_assess(Path(d))


if __name__=="__main__":
    unittest.main()
