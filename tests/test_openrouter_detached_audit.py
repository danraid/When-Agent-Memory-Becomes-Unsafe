"""Detached audit must reject tampering and unequal paired evidence."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_openrouter_longmemeval import audit


class DetachedAuditTests(unittest.TestCase):
    def fixture(self, path):
        rows = []
        questions = ["q1", "q2"]
        models = ["a", "b"]
        arms = ["full_history", "recent_window", "recursive_summary"]
        for q in questions:
            for model in models:
                for arm in arms:
                    rows.append({
                        "question_id": q, "model": model, "arm": arm,
                        "judge_correct": True if arm == "full_history" else False,
                        "error": None,
                    })
        data = {
            "observations.json": rows,
            "summary.json": {
                "status": "EXPLORATORY_COMPLETE_NOT_SCIENTIFICALLY_APPROVED",
                "expected_answers": len(rows), "scored_answers": len(rows),
                "submission_authorized": False,
            },
            "run_metadata.json": {
                "benchmark": "LongMemEval",
                "selected_question_ids": questions,
                "models": models, "arms": arms,
                "dataset_sha256": "dataset", "config_sha256": "config",
                "source_sha256": "source",
                "scientifically_approved": False, "holdout_touched": False,
            },
        }
        for name, value in data.items():
            (path / name).write_text(json.dumps(value), encoding="utf-8")
        manifest = {
            "scientifically_approved": False,
            "files_sha256": {
                name: hashlib.sha256((path / name).read_bytes()).hexdigest()
                for name in data
            },
        }
        (path / "manifest.json").write_text(json.dumps(manifest))
        return data

    def test_balanced_paired_descriptive_audit(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            result = audit(root)
            self.assertEqual(result["total_scored"], 12)
            self.assertEqual(result["evidence_files_verified"], 3)
            contrast = result["models"]["a"]["paired_contrasts"]["recursive_summary_minus_full_history"]
            self.assertEqual(contrast["paired_questions_with_both_judged"], 2)
            self.assertEqual(contrast["difference_descriptive_only"], -1)
            self.assertFalse(result["scientifically_approved"])

    def test_hash_change_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            with (root / "observations.json").open("a") as f:
                f.write("tampered")
            with self.assertRaisesRegex(ValueError, "DIGEST_MISMATCH"):
                audit(root)

    def test_unscored_is_missing_not_incorrect(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.fixture(root)
            data["observations.json"][0]["judge_correct"] = None
            data["summary.json"]["scored_answers"] -= 1
            for name in ("observations.json", "summary.json"):
                (root / name).write_text(json.dumps(data[name]))
            m = json.loads((root / "manifest.json").read_text())
            for name in ("observations.json", "summary.json"):
                m["files_sha256"][name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
            (root / "manifest.json").write_text(json.dumps(m))
            result = audit(root)
            self.assertEqual(result["total_scored"], 11)
            self.assertEqual(result["models"]["a"]["full_history"]["coverage"], .5)


if __name__ == "__main__":
    unittest.main()
