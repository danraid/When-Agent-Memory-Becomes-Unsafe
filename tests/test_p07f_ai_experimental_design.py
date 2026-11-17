"""P07f: source provenance, blind expert roles, and author-only decision gates."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.p07f_ai_methodology_experts import (
    assemble, role_prompt, parse_role, synth_prompt, parse_synthesis, manifest,
)


class AIExperimentalDesignTests(unittest.TestCase):
    def test_original_p07e_provenance_required_before_any_paid_calls(self):
        with TemporaryDirectory() as tmp:
            a=Path(tmp)/"original"
            b=Path(tmp)/"p07e"
            a.mkdir();b.mkdir()
            with self.assertRaisesRegex(ValueError,"MISSING_ORIGINAL_MANIFEST"):
                assemble(a,b,Path("protocol/P07F_AI_EXPERIMENTAL_PANEL_V1.json"))

    def test_role_is_blind_to_ai_votes_and_historical_disposition(self):
        case={
            "title":"Source code amendment",
            "description_retrospective":"Change C API warning",
            "created_at":"2025-01-01T00:00:00Z",
            "evidence":[{"id":"PATCH_1","text":"-legacy()\n+safe_api()"},
                        {"id":"CREATION_NORM_1","text":"A feature cannot be removed without notice."}],
            "historical_source_available_at_creation":True,
            "historical_source_available_at_closure":True,
            "source_changed_between_events":False,
            "effective_normative_authority_not_verified":True,
            "independent_human_reference_action_available":False,
        }
        cfg=json.loads(Path("protocol/P07F_AI_EXPERIMENTAL_PANEL_V1.json").read_text())
        self.assertEqual(len(set(cfg["blinded_roles"].values())),3)
        for role in cfg["blinded_roles"]:
            p=role_prompt(role,case)
            self.assertIn("NOT A HUMAN EXPERT",p)
            self.assertNotIn("observed_disposition",p)
            self.assertNotIn("prior_ai_vote",p)
            self.assertNotIn("analyst_scope_tag",p)

    def test_literal_source_citation_is_required(self):
        case={"evidence":[{"id":"PATCH_1","text":"-legacy()\n+safe_api()"},
                          {"id":"CREATION_NORM_1","text":"Removal requires a warning."}]}
        vote={
            "decision":"needs_additional_source",
            "evidence_id":"CREATION_NORM_1",
            "quote":"Removal requires a warning.",
            "reason":"Evidence does not establish policy effectiveness in this episode.",
            "risk_flags":["policy_effectivity_unknown"],
            "confidence":0.7,
            "claims_human_expertise":False,
            "human_ground_truth_established":False,
        }
        body=json.dumps(vote)
        self.assertEqual(parse_role(body,case)[0],vote)
        with self.assertRaisesRegex(ValueError,"NONVERBATIM"):
            parse_role(json.dumps(dict(vote,quote="Fabricated phrase")),case)
        with self.assertRaisesRegex(ValueError,"FALSE_HUMAN"):
            parse_role(json.dumps(dict(vote,claims_human_expertise=True)),case)
        with self.assertRaisesRegex(ValueError,"CONTRADICTORY_RISKS"):
            parse_role(json.dumps(dict(vote,risk_flags=["none","scope_mismatch"])),case)

    def test_synthesis_is_not_independent_human_or_author_approval(self):
        case={"evidence":[{"id":"PATCH_1","text":"sample source"}]}
        votes=[
            {"role":role,
             "review":{"decision":"needs_additional_source",
                       "risk_flags":["insufficient_events"],
                       "evidence_id":"PATCH_1",
                       "reason":"Missing authenticated rule event."}}
            for role in ("causal_design","temporal_authority","benchmark_validity")
        ]
        p=synth_prompt(case,votes)
        self.assertIn("not a fourth",p)
        good={
            "recommendation":"needs_additional_source",
            "disagreements":[],
            "blocking_reason":"Insufficiently authenticated policy event.",
            "author_review_required":True,
            "human_validation_claimed":False,
        }
        self.assertEqual(parse_synthesis(json.dumps(good))[0],good)
        with self.assertRaisesRegex(ValueError,"AUTOMATIC_AUTHOR"):
            parse_synthesis(json.dumps(dict(good,author_review_required=False)))

if __name__=="__main__":
    unittest.main()
