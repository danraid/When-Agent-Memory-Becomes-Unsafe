import unittest,json
from scripts.r01_memory_policy_cycle16 import cases,assignments,compaction,decision_prompt,payload,memory_value,MAX_CALLS
from scripts.r01_cycle16_extension import NEW
from scripts.r01_governance_source_replay import load
from scripts.r01_operational_environment import run_episode
from scripts.r01_operational_oracle import score
class Extension(unittest.TestCase):
    def test_frame_and_source_scope(self):
        rows=assignments();self.assertEqual(len(rows),24)
        self.assertEqual(sum(1 if r["arm"]=="source_only" else 2 for r in rows),MAX_CALLS)
        self.assertEqual(len({c["task_id"] for c,h in cases()}),8)
        for c,h in cases():
            self.assertTrue(all(x["published_at"]<=c["cutoff"] for x in h))
            self.assertTrue(all(x["source_id"] in {y["source_id"] for y in h if y["issue"]==c["target_issue"]} for x in c["records"]))
            self.assertNotIn('"records":',decision_prompt(c,h))
            for arm in ("summary","ledger"):payload(compaction(arm,h))
            payload(decision_prompt(c,h))
    def test_scripted_oracle(self):
        ref={x["id"]:x["label"] for x in load(NEW+"LABELS.json")["labels"]}
        for c,h in cases():
            for decision in ("APPROVE","REJECT","ABSTAIN"):
                p={"decision":decision,"action":c["requested_mock_action"] if decision=="APPROVE" else None,"source_ids":[x["source_id"] for x in c["records"]]}
                self.assertEqual(score(c,run_episode(c,p),ref[c["task_id"]])["terminal_success"],decision==ref[c["task_id"]])
    def test_ledger_issue_drift(self):
        c,h=next((c,h) for c,h in cases() if h)
        e=h[0]
        with self.assertRaises(ValueError):memory_value(json.dumps({"memory":[{"source_id":e["source_id"],"published_at":e["published_at"],"issue":-1,"statement":"fixture"}]}),"ledger",h)
