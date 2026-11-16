"""Offline unit coverage for exploratory OpenRouter LongMemEval instrument."""
import unittest
from study.openrouter_comparison import (
    BenchmarkError, OpenRouter, answer_prompt, compaction_prompt, judge_prompt,
    metrics, parse_judge, planned_calls, public_sessions, select_questions,
)
from pathlib import Path
from tempfile import TemporaryDirectory


class ComparisonTests(unittest.TestCase):
    def sample(self, n=12):
        types = ("knowledge-update", "temporal-reasoning", "multi-session",
                 "single-session-user", "single-session-assistant", "single-session-preference")
        return [{"question_id": f"sample-{i}", "question_type": types[i % 6],
                 "haystack_sessions": [[{"role": "user", "content": "user statement"}]],
                 "haystack_dates": ["2025-01-01"], "haystack_session_ids": ["s1"]}
                for i in range(n)]

    def test_deterministic_balanced_selection(self):
        entries = self.sample()
        a = select_questions(entries, 6, "fixed-seed")
        b = select_questions(entries, 6, "fixed-seed")
        self.assertEqual(a, b)
        self.assertEqual({x["question_type"] for x in a}, {x["question_type"] for x in entries})

    def test_public_context_excludes_answers_and_gold(self):
        item = {"haystack_dates": ["2025-01-01"], "haystack_sessions": [[{
            "role": "user", "content": "my preference",
            "has_answer": True, "answer": "SECRET", "evidence": "SECRET"
        }]]}
        visible = public_sessions(item)
        self.assertEqual(visible, [{"session_date": "2025-01-01", "turns": [{
            "role": "user", "content": "my preference"}]}])
        self.assertNotIn("SECRET", str(visible))
        prompt = compaction_prompt("", visible)
        self.assertNotIn("SECRET", prompt)

    def test_judge_data_stays_in_evaluator_only(self):
        item = {"question_id": "case", "question_type": "knowledge-update",
                "question": "Which city?", "answer": "GOLD_LABEL"}
        decision = answer_prompt(item["question"], "2025-05-01", "history", "recent_window")
        self.assertNotIn("GOLD_LABEL", decision)
        self.assertIn("GOLD_LABEL", judge_prompt(item, "wrong answer"))
        self.assertIs(parse_judge("Yes"), True)
        self.assertIs(parse_judge("no."), False)
        self.assertIsNone(parse_judge("maybe yes"))

    def test_preflight_counts_compaction_and_judge(self):
        entries = self.sample(2)
        self.assertEqual(planned_calls(entries, 4, 8), 4 * 2 * 7)

    def test_provider_reservations_and_provenance(self):
        seen = []
        def provider(key, payload):
            seen.append(payload)
            return {"id": "gen-123", "model": "model/version",
                    "choices": [{"message": {"content": "Yes"}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 2}}
        with TemporaryDirectory() as tmp:
            client = OpenRouter("placeholder", Path(tmp)/"ledger.json", 1, transport=provider)
            observed = client.call("provider/model", "question", 32)
            self.assertEqual(observed["text"], "Yes")
            self.assertEqual(observed["observed_model"], "model/version")
            self.assertEqual(len(seen), 1)
            with self.assertRaisesRegex(BenchmarkError, "FINITE_CALL_LIMIT"):
                client.call("provider/model", "question", 32)

    def test_missing_judgement_never_becomes_success(self):
        rows = [{"model": "a", "arm": "full_history", "question_type": "multi-session",
                 "judge_correct": True}]
        result = metrics(rows, self.sample(2), ["a"])
        self.assertEqual(result["a"]["full_history"]["accuracy_lower_bound_failures_wrong"], 0.5)
        self.assertEqual(result["a"]["full_history"]["coverage"], 0.5)
        self.assertEqual(result["a"]["recent_window"]["coverage"], 0)


if __name__ == "__main__":
    unittest.main()
