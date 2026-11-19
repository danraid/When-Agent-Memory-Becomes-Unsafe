"""R01 development-only documentary challenges: time/source/scope isolation."""
from __future__ import annotations
import copy,json,unittest
from r01_documentary.challenge import validated,prompt_for,sources_for,grade,build,stamp
class R01RealDocumentaryCaseTests(unittest.TestCase):
    def test_exact_12_case_manifest_and_source_scope(self):
        d,p=validated()
        self.assertEqual(len(build()),12)
        self.assertEqual(sum(t["reference_documentary_state"]=="grant_supported" for t in d["tasks"]),2)
        self.assertEqual(sum(t["reference_documentary_state"]=="not_established" for t in d["tasks"]),10)
        for t in d["tasks"]:
            s,visible=prompt_for(t,d,p)
            self.assertNotIn("reference_documentary_state",s)
            self.assertNotIn("design_note",s)
            self.assertTrue(visible)
            self.assertTrue(all(stamp(x["created"])<=stamp(t["decision_at"]) for x in visible))
            for x in visible:
                self.assertIn(x["id"],s)
    def test_sc_grant_only_after_publication_and_exact_scope(self):
        d,p=validated()
        by={x["id"]:x for x in d["tasks"]}
        self.assertNotIn("SC_DECISION_288",{x["id"] for x in sources_for(by["T01"],d,p)})
        for tid in ("T02","T03"):
            self.assertIn("SC_DECISION_288",{x["id"] for x in sources_for(by[tid],d,p)})
        self.assertEqual(by["T04"]["reference_documentary_state"],"not_established")
        self.assertEqual(by["T05"]["reference_documentary_state"],"not_established")
    def test_post_decision_comment_is_not_initial_context(self):
        d,p=validated()
        by={x["id"]:x for x in d["tasks"]}
        self.assertNotIn("AST_REVIEW_140344",{x["id"] for x in sources_for(by["T06"],d,p)})
        self.assertIn("AST_REVIEW_140344",{x["id"] for x in sources_for(by["T07"],d,p)})
        self.assertNotIn("AST_AUTHOR_140344",{x["id"] for x in sources_for(by["T07"],d,p)})
        self.assertIn("AST_AUTHOR_140344",{x["id"] for x in sources_for(by["T08"],d,p)})
    def test_reference_corruption_cannot_change_prompt(self):
        d,p=validated()
        t=d["tasks"][2]
        modified=copy.deepcopy(t)
        modified["reference_documentary_state"]="not_established"
        modified["design_note"]="malicious injection"
        self.assertEqual(prompt_for(t,d,p)[0],prompt_for(modified,d,p)[0])
    def test_genuine_source_id_required_for_grant(self):
        d,p=validated()
        t=d["tasks"][1]
        visible=sources_for(t,d,p)
        valid=grade(t,json.dumps({"status":"grant_supported",
             "evidence_ids":["SC_REQUEST_288","SC_DECISION_288"],"reason":"Request names API; formal response approves that request"}),visible)
        self.assertTrue(valid["documentary_match"])
        self.assertTrue(valid["grant_cites_original_scope_and_decision"])
        bad=grade(t,json.dumps({"status":"grant_supported","evidence_ids":["PEP387_AT_PREDECISION"],
                                "reason":"General policy gives no specific approval"}),visible)
        self.assertTrue(bad["documentary_match"])
        self.assertTrue(bad["unsupported_grant"])
        self.assertFalse(bad["grant_cites_original_scope_and_decision"])
    def test_unknown_sources_invalid(self):
        d,p=validated()
        t=d["tasks"][0]
        q=grade(t,json.dumps({"status":"not_established","evidence_ids":["FUTURE_COMMENT"],
                              "reason":"No valid proof in time"}),sources_for(t,d,p))
        self.assertFalse(q["valid_source_ids"])
if __name__=="__main__":unittest.main()
