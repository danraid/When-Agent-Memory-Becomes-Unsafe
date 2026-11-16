"""Real historical source intake and simulated expert-role boundaries."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.p07c_collect_real_governance import build, materialise
from scripts.p07c_simulated_expert_panel import (
    ROLES, parse_vote, reviewer_prompt,
)
from scripts.p07c_detached_real_governance_audit import check_manifest


class P07CRealGovernanceTests(unittest.TestCase):
    def config(self):
        return Path("protocol/P07C_REAL_GOVERNANCE_SOURCE_MATRIX.json")

    def fake_transport(self,url):
        if "/issues/" in url:
            return [{"created_at":"2025-01-10T12:00:00Z",
                     "body":"Review asks for clearer scope and source provenance.",
                     "html_url":"https://github.com/example#comment"}]
        num=int(url.split("/pulls/")[1])
        cfg=json.loads(self.config().read_text())
        index=next(i for i,c in enumerate(cfg["cases"]) if c["number"]==num)
        is_merged=index<5
        return {
            "number":num,"state":"closed",
            "title":"A real-style software governance proposal with recorded history",
            "body":"The proposal introduces a controlled change with documented scope and feedback.",
            "created_at":"2025-01-01T00:00:00Z",
            "closed_at":"2025-02-01T00:00:00Z",
            "merged_at":"2025-02-01T00:00:00Z" if is_merged else None,
            "html_url":f"https://github.com/example/repo/pull/{num}",
            "head":{"sha":"head"},"base":{"sha":"base"},
        }

    def test_casebook_has_eight_actual_event_slots_with_no_outcome_leak(self):
        cfg=json.loads(self.config().read_text())
        self.assertEqual(len(cfg["cases"]),8)
        self.assertEqual(len(set(ROLES.values())),3)
        with TemporaryDirectory() as dirname:
            inputs,sidecar,raw=build(self.config(),self.fake_transport)
            self.assertEqual(inputs["case_count"],8)
            self.assertEqual(len(sidecar["observed_outcomes"]),8)
            self.assertFalse(inputs["historical_predecision_snapshot_guaranteed"])
            self.assertEqual(len(raw["original_api_payloads"]),8)
            for c in inputs["cases"]:
                self.assertNotIn("observed_disposition",c)
                self.assertNotIn("merged_at",c)
                self.assertNotIn("closed_at",c)
                self.assertFalse(c["source_body_historically_frozen"])
                self.assertEqual(len(c["predecision_discussion"]),1)
            out=Path(dirname)/"cases"
            counts=materialise(self.config(),out,self.fake_transport)
            self.assertEqual(counts["merged"],5)
            self.assertEqual(counts["closed_without_merge"],3)
            self.assertEqual(counts["qualified_human_adjudications"],0)
            h,n=check_manifest(out)
            self.assertEqual(n,3)
            self.assertEqual(len(h),64)

    def test_roles_must_quote_original_model_visible_evidence(self):
        c={
            "question":"Predict",
            "title":"Proposal to alter Python compatibility guidance",
            "proposal_excerpt":"The policy needs a review before implementation.",
            "created_at_utc":"2025-01-01T00:00:00Z",
            "predecision_discussion":[],
        }
        for role in ROLES:
            p=reviewer_prompt(role,c)
            self.assertNotIn("observed_disposition",p)
            self.assertIn("SIMULATED AI specialist",p)
        v={
            "disposition":"insufficient_evidence",
            "evidence_quote":"The policy needs a review",
            "reason":"The text presents an idea without adequate decision evidence.",
            "confidence":0.5,
            "claims_to_be_human_expert":False,
        }
        fence=chr(96)*3
        got,wrapped=parse_vote(fence+"json\n"+json.dumps(v)+"\n"+fence,c)
        self.assertTrue(wrapped)
        self.assertEqual(got,v)
        v["claims_to_be_human_expert"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_HUMAN"):
            parse_vote(json.dumps(v),c)

    def test_tampering_is_rejected_before_interpretation(self):
        with TemporaryDirectory() as dirname:
            out=Path(dirname)/"original"
            materialise(self.config(),out,self.fake_transport)
            (out/"model_inputs_no_outcome.json").write_text("{INVALID")
            with self.assertRaisesRegex(ValueError,"TAMPER"):
                check_manifest(out)


if __name__=="__main__":
    unittest.main()
