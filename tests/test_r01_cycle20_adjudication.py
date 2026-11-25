import json,unittest
from scripts.r01_cycle20_adjudication import payload,validate,MODELS
from scripts.r01_cycle16_extension import prepare
class Cycle20Tests(unittest.TestCase):
    def test_frame_and_blinding(self):
        cases=prepare();self.assertEqual(len(cases),8)
        for c in cases:
            for m in MODELS:
                x=payload(m,c)
                self.assertFalse(x["provider"]["allow_fallbacks"])
                self.assertNotIn('"label":',x["messages"][0]["content"])
                self.assertNotIn('"response_contract":',x["messages"][0]["content"])
    def test_mapping_schema_and_unknown_source(self):
        c=next(c for c in prepare() if not c["records"])
        good={"decision":"ABSTAIN","source_ids":[],"reason":"No visible decision.","mapping_status":"MATCHES_REQUEST","mapping_reason":"Mock operation matches the request."}
        self.assertEqual(validate(json.dumps(good),c),(good,False))
        for bad in (dict(good,source_ids=["future"]),dict(good,mapping_status="PASS"),dict(good,decision="APPROVE")):
            with self.assertRaises(ValueError):validate(json.dumps(bad),c)
