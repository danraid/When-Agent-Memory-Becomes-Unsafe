"""Scientific boundary tests for genuine P07b documents and AI-only role review."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.p07b_build_verified_cases import source_span, target_header, SourceGateError
from scripts.p07b_ai_panel import parse_vote, prompt, ROLE_MODELS
from scripts.validate_independent_case_intake import validate


class P07BSourceAIPanelTests(unittest.TestCase):
    def test_extracts_real_exact_line_without_paraphrase(self):
        sample = "Title: Example\nSuperseded-By: 387\nOther: data\n"
        span=source_span(sample,"python/peps","387")
        self.assertEqual(span["quoted_line"],"Superseded-By: 387")
        self.assertEqual(span["source_line_number"],2)
        self.assertEqual(target_header("PEP: 387\nTitle: Replacement","python/peps","387"),"PEP: 387")

    def test_source_missing_link_fails_closed(self):
        with self.assertRaisesRegex(SourceGateError,"MISSING_VERIFIED_SUPERSESSION_SPAN"):
            source_span("Some other text","python/peps","387")

    def test_no_answer_or_peers_in_model_visible_review(self):
        sample={
            "question":"Does source explicitly identify replacement?",
            "source_document":{"url":"https://example.org/a"},
            "target_document":{"url":"https://example.org/b"},
            "source_evidence":{"quoted_line":"Superseded-By: 387"},
            "target_identity":{"number":"387"},
            "reference_link_status_from_verified_text":"supported",
            "gold_action":"reject",
        }
        self.assertEqual(len(ROLE_MODELS),3)
        self.assertEqual(len(set(ROLE_MODELS.values())),3)
        for role in ROLE_MODELS:
            p=prompt(role,sample)
            self.assertIn("Superseded-By: 387",p)
            self.assertNotIn("gold_action",p)
            self.assertNotIn("reference_link_status_from_verified_text",p)
            self.assertNotIn('"decision": "supported"',p)
            self.assertNotIn("peer_vote",p)

    def test_valid_votes_require_exact_source_quote(self):
        good=json.dumps({
            "decision":"supported","quoted_evidence":"Superseded-By: 387",
            "reason":"The pinned source explicitly states the target in its metadata.",
            "confidence":0.9,"authority_semantics_resolved":False
        })
        self.assertEqual(parse_vote(good,"Superseded-By: 387")["decision"],"supported")
        bad=json.loads(good)
        bad["quoted_evidence"]="Source author says yes, definitely"
        with self.assertRaisesRegex(ValueError,"EVIDENCE_QUOTE_NOT_IN_SOURCE_EXCERPT"):
            parse_vote(json.dumps(bad),"Superseded-By: 387")
        bad=json.loads(good)
        bad["authority_semantics_resolved"]=True
        with self.assertRaisesRegex(ValueError,"FABRICATED_OPERATIONAL_AUTHORITY_RESOLUTION"):
            parse_vote(json.dumps(bad),"Superseded-By: 387")

    def test_ai_simulation_cannot_pass_real_human_gate(self):
        fixture={"cases":[{
            "case_id":"fixture","split":"development",
            "simulation_only":True,"writer_id":"model-A",
            "writer_declaration":{"independent_of_target_model_outputs":True},
            "source_documents":[{"source_id":"s","url":"https://example.org","revision":"hash","sha256":"hash","licence":"unknown"}],
            "events":[{"event_id":"e","source_id":"s","issuer":"source","issued_at":"2026-01-01","effective_at":"2026-01-01","scope":"x","rule":"x","supersedes":"x"}],
            "request":{"actor":"x"},"decision_time":"2026-01-02"
        }],"simulation_only":True}
        reviews={"simulation_only":True,"adjudications":[{
            "case_id":"fixture","adjudicator_id":"model-B",
            "independence_declaration":{"not_case_writer":True,"blind_to_model_outputs":True,"conflict_checked":True},
            "action":"abstain","reason":"No independent expert data",
            "evidence_event_ids":["e"],"reviewed_at":"2026-01-03",
            "ambiguity_basis":"model opinion"
        }]}
        self.assertTrue(any("fictional simulation" in e for e in validate(fixture,reviews)))


if __name__=="__main__":
    unittest.main()
