"""Offline regression tests for R01/R02 preparatory evidence, not scientific validation."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.check_r01_r02_subsidies import ROOT,R01,R02,audit


class SubsidyContractTests(unittest.TestCase):
    def test_original_repository_subsidies(self):
        r=audit()
        self.assertTrue(r["passed"],r["checks"])
        self.assertEqual(r["r01_qualified_gold"],0)
        self.assertFalse(r["r02_full_original_reproduction"])
        self.assertFalse(r["external_submission"])

    def test_fabricated_scientific_promotion_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for file in (R01,R02):
                p=root/file.relative_to(ROOT)
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(file.read_bytes())
            p=root/R01.relative_to(ROOT)
            data=json.loads(p.read_text(encoding="utf-8"))
            data["cases"][0]["qualified_action"]="approve"
            p.write_text(json.dumps(data),encoding="utf-8")
            self.assertFalse(audit(root)["passed"])
            self.assertFalse(audit(root)["checks"]["case_status_not_promoted"])
            data["cases"][0]["qualified_action"]=None
            p.write_text(json.dumps(data),encoding="utf-8")
            p=root/R02.relative_to(ROOT)
            data=json.loads(p.read_text(encoding="utf-8"))
            data["original_full_framework_reproduced"]=True
            data["authorisation"]["external_submission"]=True
            p.write_text(json.dumps(data),encoding="utf-8")
            report=audit(root)
            self.assertFalse(report["passed"])
            self.assertFalse(report["checks"]["method_claims_remain_bounded"])
            self.assertFalse(report["checks"]["no_approval_or_external_submit"])

    def test_missing_specific_evidence_field_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for file in (R01,R02):
                p=root/file.relative_to(ROOT)
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(file.read_bytes())
            p=root/R01.relative_to(ROOT)
            data=json.loads(p.read_text())
            del data["cases"][2]["source_capture"]["exception_evidence_url"]
            p.write_text(json.dumps(data))
            self.assertFalse(audit(root)["checks"]["case_proof_complete_as_template"])


if __name__=="__main__":
    unittest.main()
