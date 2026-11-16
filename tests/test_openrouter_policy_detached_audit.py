"""Independent policy-v2 audit invariants; no API calls or held-out data."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_openrouter_policy_safety import (
    DetachedAuditError, verified_json, require, markdown,
)


class PolicyV2DetachedTests(unittest.TestCase):
    def test_verified_file_rejects_tampering_before_json_parse(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "case.json"
            path.write_text('{"valid":true}')
            valid_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(verified_json(root, "case.json", valid_digest),
                             {"valid": True})
            path.write_text("this is invalid JSON and malicious tampering")
            with self.assertRaisesRegex(DetachedAuditError, "EVIDENCE_DIGEST_MISMATCH"):
                verified_json(root, "case.json", valid_digest)

    def test_traversal_and_missing_evidence_blocked(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            with self.assertRaisesRegex(DetachedAuditError, "MISSING_OR_TRAVERSING"):
                verified_json(root, "../other.json", "deadbeef")
            with self.assertRaisesRegex(DetachedAuditError, "MISSING_OR_TRAVERSING"):
                verified_json(root, "none.json", "deadbeef")

    def test_invalid_status_is_not_a_scientific_success(self):
        with self.assertRaisesRegex(DetachedAuditError, "SCIENCE_BLOCKED"):
            require(False, "SCIENCE_BLOCKED")

    def test_descriptive_report_explicitly_marks_missing_inference(self):
        record = {
            "original_status": "EXPLORATORY_PARTIAL_PROVIDER_OR_COMPACTION_FAILURE",
            "scored_rows": 0, "expected_rows": 1, "coverage": 0.0,
            "compactions": 0, "original_evidence_files_verified": 5,
            "models": {"google/gemini-2.5-flash": {
                "arms": {
                    arm: {"unsafe_raw": 0, "unsafe_final": 0,
                          "reject_opportunities_scored": 0,
                          "scored": 0, "expected": 1}
                    for arm in ("full_history","recent_window",
                                "recursive_summary","pinned_ledger","pinned_ledger_guard")
                },
                "mean_episode_risk_difference_if_complete": None,
                "primary_episode_contrasts": [{"risk_difference_if_complete": None}]
            }},
            "errors": [{"model": "google/gemini-2.5-flash",
                        "arm": "pinned_ledger", "count": 1,
                        "error": "OPENROUTER_HTTP_429"}],
            "limitations": ["No independent human judgement."],
        }
        report = markdown(record)
        self.assertIn("unavailable: incomplete matched cases", report)
        self.assertIn("OPENROUTER_HTTP_429", report)
        self.assertIn("exploratory development", report)
        self.assertNotIn("statistically significant", report)


if __name__ == "__main__":
    unittest.main()
