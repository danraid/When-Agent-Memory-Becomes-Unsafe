"""P10 AI-only review contracts. No credential, provider or holdout access."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.p10_ai_scientific_independent_panel import (
    config_and_evidence, prompts, interpret, chair_prompt,
)
from study.openrouter_comparison import digest

CONFIG=Path("protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json")


class P10PanelTests(unittest.TestCase):
    def test_four_distinct_provider_roles_and_author_only_final(self):
        cfg,raw,paper,ledger,novelty,receipts=config_and_evidence(CONFIG)
        self.assertEqual(len(cfg["reviewers"]),4)
        self.assertEqual(cfg["max_calls"],5)
        self.assertEqual(cfg["author_final_decision"],None)
        self.assertEqual(cfg["independent_human_reviewers"],0)
        self.assertFalse(cfg["confirmatory_experiment_authorised"])
        self.assertEqual(len(set(r["model"].split("/")[0]
            for r in cfg["reviewers"]+[cfg["chair"]])),5)
        self.assertEqual(len(receipts),len(ledger["claims"]))
        self.assertTrue(all(len(x["source_sha256"])==64 for x in receipts.values()))

    def test_blind_source_specific_review_and_verbatim_objections(self):
        cfg,raw,ledger,receipts,items=prompts(CONFIG)
        paper=(Path(cfg["manuscript"])).read_text()
        self.assertEqual(len(items),4)
        for role,p,selected in items:
            self.assertIn("NOT a real human reviewer",p)
            self.assertNotIn("other reviewers' votes",p)
            self.assertEqual(len(selected),len(role["claims"]))
            self.assertEqual(len(digest(p.encode())),64)
            sample=selected[0]
            quote=sample["source_text"].splitlines()[0]
            if len(quote)<8:
                quote="The Compaction Cliff"
                source="manuscript"
            else:
                source=sample["source_id"]
            v={
                "recommendation":"major_revision",
                "major_objections":[{"finding":"Scientific qualification is not established",
                    "source_id":source,"quoted_evidence":quote,
                    "required_change":"Report validity limits before making stronger claims"}],
                "minor_objections":[],
                "verified_points":["Audited source contains documentary text"],
                "unverified_points":["Independent human assessment remains absent"],
                "scope":"Methodological AI advisory only, not human peer review",
                "is_human_reviewer":False
            }
            self.assertEqual(interpret(json.dumps(v),selected,paper),v)
            broken=json.loads(json.dumps(v))
            broken["is_human_reviewer"]=True
            with self.assertRaisesRegex(ValueError,"FALSE_HUMAN"):
                interpret(json.dumps(broken),selected,paper)

    def test_chair_never_receives_gold_and_cannot_sign_for_author(self):
        c=chair_prompt("0"*64,[{
            "reviewer_id":"sample","requested_model":"provider/model",
            "response_id":"test","review":{"recommendation":"major_revision"},
            "original_response_text":"test raw","error":None
        }])
        self.assertIn("author_final_decision (null)",c)
        self.assertIn("human_independent_review_completed (false)",c)
        self.assertIn("Four AI reviewers",c)


if __name__=="__main__":
    unittest.main()
