"""V2 evidence-ID provenance contract protects source quotes without models copying."""
import json
from pathlib import Path
import unittest
from scripts.p07f_v2_evidence_id_panel import role_prompt_v2,parse_role_v2

class EvidenceIDTests(unittest.TestCase):
    def setUp(self):
        self.case={
            "title":"Public code modification",
            "description_retrospective":"A deprecation API patch with unverified scope.",
            "created_at":"2025-01-01T00:00:00Z",
            "evidence":[
                {"id":"PATCH_1","text":"@@ -1 +1 @@\n-legacy_api()\n+modern_api()"},
                {"id":"CREATION_NORM_1","text":"* Feature removal requires advance warning"},
            ],
            "historical_source_available_at_creation":True,
            "historical_source_available_at_closure":True,
            "source_changed_between_events":False,
            "effective_normative_authority_not_verified":True,
            "independent_human_reference_action_available":False,
        }
        self.vote={
            "decision":"needs_additional_source",
            "evidence_id":"CREATION_NORM_1",
            "reason":"The original event's normative applicability remains unverified.",
            "risk_flags":["policy_effectivity_unknown"],
            "confidence":0.75,
            "claims_human_expertise":False,
            "human_ground_truth_established":False,
        }
    def test_exact_source_is_lookup_not_llm_claim(self):
        parsed,normalized=parse_role_v2(json.dumps(self.vote),self.case)
        self.assertFalse(normalized)
        self.assertEqual(parsed["quote"],"* Feature removal requires advance warning")
        self.assertIn("NOT_LLM_GENERATED",parsed["quote_origin"])
        self.assertEqual(parsed["evidence_id"],"CREATION_NORM_1")
        self.assertNotIn("quote",self.vote)
    def test_missing_or_wrong_evidence_id_is_invalid(self):
        with self.assertRaisesRegex(ValueError,"EVIDENCE_ID"):
            parse_role_v2(json.dumps(dict(self.vote,evidence_id="UNKNOWN")),self.case)
        with self.assertRaisesRegex(ValueError,"FALSE_HUMAN"):
            parse_role_v2(json.dumps(dict(self.vote,claims_human_expertise=True)),self.case)
    def test_model_does_not_receive_outcome_or_prior_votes(self):
        p=role_prompt_v2("temporal_authority",self.case)
        self.assertIn("evidence_id",p)
        self.assertNotIn("observed_disposition",p)
        self.assertNotIn("analyst_scope_tag",p)
        self.assertIn("NOT a",p)
    def test_version_is_separate_with_original_preserved(self):
        cfg=json.loads(Path("protocol/P07F_V2_SOURCE_ID_EXPERIMENTAL_PANEL.json").read_text())
        self.assertEqual(cfg["version"],"2.0.0")
        self.assertTrue(cfg["historical_run_relabeling_forbidden"])
        self.assertEqual(cfg["max_paid_call_reservations"],34)
        self.assertEqual(cfg["author_approval"],"PENDING_EXPLICIT_CONTENT_SPECIFIC_DECISION")

if __name__=="__main__":
    unittest.main()
