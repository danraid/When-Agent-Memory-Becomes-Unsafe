import json
import unittest
from scripts.r01_memory_policy_cycle13 import cases,assignments,compaction,decision_prompt,payload,memory_value,MAX_CALLS,ARMS
class PilotTests(unittest.TestCase):
    def test_frame(self):
        rows=assignments();self.assertEqual(len(rows),21)
        self.assertEqual(sum(1 if r["arm"]=="source_only" else 2 for r in rows),MAX_CALLS)
        for c,h in cases():
            self.assertEqual({r["arm"] for r in rows if r["task_id"]==c["task_id"]},set(ARMS))
            self.assertTrue(all(x["published_at"]<=c["cutoff"] for x in h))
            self.assertNotIn("requested_mock_action",compaction("summary",h))
            self.assertNotIn("requested_mock_action",compaction("ledger",h))
            self.assertNotIn('"records":',decision_prompt(c,"sentinel memory"))
            self.assertEqual(payload(compaction("summary",h))["max_tokens"],payload(compaction("ledger",h))["max_tokens"])
    def test_bad_ledger(self):
        with self.assertRaises(ValueError):
            memory_value(json.dumps({"memory":[{"source_id":"E99","published_at":"1900","statement":"fake"}]}),"ledger",[])
    def test_memory_caps(self):
        self.assertEqual(memory_value('{"memory":"empty"}',"summary",[]),"empty")
        with self.assertRaises(ValueError):memory_value(json.dumps({"memory":"x"*5000}),"summary",[])
