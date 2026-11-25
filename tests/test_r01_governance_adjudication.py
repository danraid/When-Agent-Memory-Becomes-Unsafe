import json
import unittest
from scripts.r01_governance_adjudication import build,parse,MODELS
class TestR01GovernanceAdjudication(unittest.TestCase):
    def setUp(self):
        self.case={"task_id":"Q","cutoff":"2025-01-01T00:00:00Z","question":"Can this proceed?","contract":"source only","records":[]}
    def test_no_reference_in_prompt(self):
        p=build(MODELS[0],self.case)
        self.assertNotIn("provisional_label",p["messages"][0]["content"])
        self.assertFalse(p["provider"]["allow_fallbacks"])
    def test_unsupported_and_bad_citations(self):
        for x in [{"decision":"APPROVE","source_ids":[],"reason":"No record present."},{"decision":"ABSTAIN","source_ids":["future"],"reason":"No record present."}]:
            with self.assertRaises(ValueError): parse(json.dumps(x),self.case)
    def test_valid_abstention(self):
        x={"decision":"ABSTAIN","source_ids":[],"reason":"No record present."}
        self.assertEqual(parse(json.dumps(x),self.case),x)
