import unittest
from scripts.r01_memory_policy_cycle28 import cases,assignments,compaction,decision_prompt,payload,compaction_cap,ARMS,MAX_CALLS,distractors,OUTPUT
class PressureTests(unittest.TestCase):
    def test_frame(self):
        rows=assignments();self.assertEqual(len(rows),40)
        self.assertEqual(sum(1 if r["arm"]=="source_only" else 2 for r in rows),MAX_CALLS)
        for c,h in cases():
            rr=[r for r in rows if r["task_id"]==c["task_id"]]
            self.assertEqual({r["arm"] for r in rr},set(ARMS))
            self.assertEqual(len({r["source_sha256"] for r in rr}),1)
            self.assertEqual(sum(x["source_id"].startswith("S") for x in h),16)
            self.assertTrue(all(x["published_at"]<=c["cutoff"] for x in h))
            self.assertFalse({x["issue"] for x in distractors()} & {c["target_issue"]})
            for a in ARMS:
                if a!="source_only":
                    self.assertNotIn("requested_mock_action",compaction(a,h))
                    self.assertEqual(payload(compaction(a,h),compaction_cap(a))["max_tokens"],compaction_cap(a))
            self.assertEqual(payload(decision_prompt(c,h))["max_tokens"],OUTPUT)
            self.assertNotIn('"records":',decision_prompt(c,h))
    def test_caps_and_source_ids(self):
        self.assertEqual(compaction_cap("summary_256"),compaction_cap("ledger_256"))
        self.assertEqual(compaction_cap("summary_768"),compaction_cap("ledger_768"))
        self.assertEqual(len({x["source_id"] for x in distractors()}),16)
