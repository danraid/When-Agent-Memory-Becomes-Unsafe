"""P07e historical qualification boundaries: no future norms, no model answers."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.p07e_qualify_historical_policy_cases import (
    history,extract_line,inspect,strict,
)
from study.openrouter_comparison import digest


class QualificationTests(unittest.TestCase):
    def test_future_normative_commit_is_rejected(self):
        def mocked(url):
            if "api.github.com" in url:
                return json.dumps([{
                    "sha":"a"*40,
                    "commit":{"committer":{"date":"2025-01-02T00:00:00Z"}}
                }]).encode()
            return ("a"*150).encode()
        with self.assertRaisesRegex(ValueError,"FUTURE_SOURCE_REVISION_LEAK"):
            history("example/repo","rules.md","2025-01-01T00:00:00Z",fetch=mocked)

    def test_historical_source_not_available_cannot_be_synthesized(self):
        def missing(url):
            return b"[]"
        result,receipt=history("rust-lang/rfcs","text/2972-constrained-naked.md",
                               "2021-08-03T13:23:38Z",fetch=missing)
        self.assertFalse(result["available"])
        self.assertIsNone(result["source_text"])
        self.assertIsNone(receipt["raw_git_text_sha256"])
        self.assertFalse(extract_line(result["source_text"],"must not specify")["anchor_present"])

    def test_literal_source_spans_never_get_inferred(self):
        s="Header\nmust not specify the inline attribute\nOther line"
        got=extract_line(s,"must not specify the")
        self.assertEqual(got["line_number"],2)
        self.assertEqual(got["literal_quote"],"must not specify the inline attribute")
        self.assertFalse(extract_line(s,"must not contain operands")["anchor_present"])
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            extract_line("constraint\nconstraint","constraint")

    def test_original_source_provenance_is_a_hard_precondition(self):
        with TemporaryDirectory() as root:
            r=Path(root)
            (r/"manifest.json").write_text(json.dumps({
                "files_sha256":{
                    "blind_code_cases.json":"0",
                    "observed_dispositions_evaluator_only.json":"0",
                    "raw_original_sources.json":"0",
                }}))
            for name in ("blind_code_cases.json",
                         "observed_dispositions_evaluator_only.json",
                         "raw_original_sources.json"):
                (r/name).write_text("{}")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_P07D_SOURCE_HASH_FAILED"):
                inspect(r,Path("protocol/P07E_HISTORICAL_SCOPE_TRIAGE.json"),
                        Path("protocol/P07D_REAL_CODE_CHANGE_MATRIX.json"))

if __name__=="__main__":
    unittest.main()
