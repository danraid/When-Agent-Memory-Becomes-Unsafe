"""P07b source draft and original Knowledge Triage fidelity boundary tests.

This suite intentionally proves that source verification does not generate
human-gold decisions, and upstream source inspection cannot qualify the
full published comparator by itself.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts.p07b_operational_candidate_instrument import (
    SPECS, CLASSIFICATION, build, quote_lines, write_artifacts,
)
from scripts.p08_full_original_knowledge_triage_preflight import (
    assess, OFFICIAL_MODELS,
)


class P07BOperationalDraftTests(TestCase):
    def test_excerpts_are_literal_and_line_pinned(self):
        s = "Heading\nNormative requirement MUST be followed.\nConsequence is an error.\n"
        excerpt = quote_lines(s, "Normative requirement MUST", 2)
        self.assertEqual(excerpt["line_start_1based"], 2)
        self.assertEqual(excerpt["line_end_1based"], 3)
        self.assertEqual(
            excerpt["verbatim_excerpt"],
            "Normative requirement MUST be followed.\nConsequence is an error.")

    def test_cannot_rewrite_missing_normative_anchor(self):
        with self.assertRaisesRegex(ValueError, "NORMATIVE_ANCHOR"):
            quote_lines("Unrelated text", "not found", 2)

    def test_six_distinct_source_backed_scenarios(self):
        self.assertEqual(len(SPECS), 6)
        self.assertEqual(len({x["domain"] for x in SPECS.values()}), 6)
        self.assertIn("NO_GOLD", CLASSIFICATION)
        self.assertTrue(all("request" in spec and "anchor" in spec
                            for spec in SPECS.values()))

    def test_write_artifacts_never_imputes_missing_human_ground_truth(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)/"candidate"
            packet = {"cases":[{"case_id":"test","decision_time":None,
                                "adjudication_status":"UNADJUDICATED"}],
                      "human_qualified_reference_labels":0}
            provenance = {"source_verification_complete":True,
                          "human_semantic_review_complete":False}
            forms = {"adjudications":[{"case_id":"test","action":None}],
                     "genuine_human_adjudications":0}
            write_artifacts(root,(packet,provenance,forms))
            m = json.loads((root/"manifest.json").read_text())
            self.assertFalse(m["operational_gold_qualified"])
            self.assertEqual(m["human_adjudications"],0)
            with self.assertRaisesRegex(ValueError, "CANNOT_OVERWRITE"):
                write_artifacts(root,(packet,provenance,forms))


class P08OriginalMethodPreflightTests(TestCase):
    def test_exact_author_model_dependencies_remain_frozen(self):
        self.assertEqual(OFFICIAL_MODELS["embedding"],"octen-embedding-8b")
        self.assertEqual(OFFICIAL_MODELS["cascade_llm"],"gpt-5.4-mini")

    @patch("scripts.p08_full_original_knowledge_triage_preflight.subprocess.run")
    def test_missing_upstream_source_fails_closed(self, mocked):
        mocked.return_value.stdout = "a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4\n"
        with TemporaryDirectory() as dirname:
            with self.assertRaisesRegex(ValueError, "UPSTREAM_COMPONENT_MISSING"):
                assess(Path(dirname),{"OPENROUTER_API_KEY":"dummy"})


if __name__=="__main__":
    import unittest
    unittest.main()
