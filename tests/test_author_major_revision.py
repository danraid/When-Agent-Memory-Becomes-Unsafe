"""Author-major-revision gates are local, deterministic, and never authorise experiments."""
import json
import pathlib
import tempfile
import unittest

from scripts.check_author_major_revision import ROOT, MANIFEST, verify


class AuthorMajorRevisionTests(unittest.TestCase):
    def test_repository_contract(self):
        report = verify()
        self.assertTrue(report["passed"], report)
        self.assertFalse(report["scientific_approval"])
        self.assertFalse(report["external_submission"])
        self.assertFalse(report["holdout_access"])

    def test_fail_closed_on_promotion_and_missing_provenance(self):
        original = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for item in original["revisions"].values():
                p = root / item["evidence"]
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("fixture", encoding="utf-8")
            target = root / MANIFEST.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            original["external_submission_authorised"] = True
            target.write_text(json.dumps(original), encoding="utf-8")
            report = verify(root)
            self.assertFalse(report["passed"])
            self.assertFalse(report["checks"]["approval_locks"])
            original["external_submission_authorised"] = False
            original["revisions"]["R01"]["evidence"] = "no-such-source.md"
            target.write_text(json.dumps(original), encoding="utf-8")
            report = verify(root)
            self.assertFalse(report["passed"])
            self.assertFalse(report["checks"]["evidence_resolves"])


if __name__ == "__main__":
    unittest.main()
