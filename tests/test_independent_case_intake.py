"""Offline schema checks only; synthetic fixtures are never human-adjudicated evidence."""
import unittest
from scripts.validate_independent_case_intake import validate

def case():
    return {"case_id":"development-demo-01","split":"development","writer_id":"example-writer",
      "writer_declaration":{"independent_of_target_model_outputs":True},
      "source_documents":[{"source_id":"s1","url":"https://example.org/policy","revision":"example","sha256":"f"*64,"licence":"synthetic"}],
      "events":[{"event_id":"e1","source_id":"s1","issuer":"example-office","issued_at":"2026-01-01","effective_at":"2026-01-02","scope":"example","rule":"example restriction","supersedes":[]}],
      "request":"example action","decision_time":"2026-01-03"}
def review():
    return {"case_id":"development-demo-01","adjudicator_id":"example-adjudicator",
      "independence_declaration":{"not_case_writer":True,"blind_to_model_outputs":True,"conflict_checked":True},
      "action":"reject","reason":"example reason","evidence_event_ids":["e1"],"reviewed_at":"2026-01-04"}
class TestCaseIntake(unittest.TestCase):
    def test_structurally_complete_not_human_verified(self):
        self.assertEqual(validate({"cases":[case()]},{"adjudications":[review()]}),[])
    def test_reject_missing_review(self):
        self.assertTrue(validate({"cases":[case()]},{"adjudications":[]}))
    def test_reject_self_adjudication(self):
        d=review();d["adjudicator_id"]="example-writer"
        self.assertTrue(any("writer cannot" in x for x in validate({"cases":[case()]},{"adjudications":[d]})))
    def test_reject_answer_leak(self):
        c=case();c["gold_action"]="reject"
        self.assertTrue(any("label" in x for x in validate({"cases":[c]},{"adjudications":[review()]})))
    def test_reject_confirmatory(self):
        c=case();c["split"]="confirmatory"
        self.assertTrue(any("development" in x for x in validate({"cases":[c]},{"adjudications":[review()]})))
    def test_reject_invalid_reference(self):
        d=review();d["evidence_event_ids"]=["missing"]
        self.assertTrue(any("missing events" in x for x in validate({"cases":[case()]},{"adjudications":[d]})))
    def test_abstain_needs_reason(self):
        d=review();d["action"]="abstain"
        self.assertTrue(any("ambiguity_basis" in x for x in validate({"cases":[case()]},{"adjudications":[d]})))
if __name__=="__main__":unittest.main()
