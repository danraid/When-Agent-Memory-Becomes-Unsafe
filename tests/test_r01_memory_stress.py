"""R01 memory-stress development preflight: same source, bounded representations."""
import copy
import unittest
from r01_documentary.challenge import validated
from r01_documentary.memory_stress import (
 common_feed,deterministic_ledger,words,bounded_memory,
 decision_prompt,compaction_prompt,manifest,
)

class R01MemoryStress(unittest.TestCase):
    def test_shared_source_stream_and_bounded_ledger(self):
        m=manifest()
        self.assertEqual(len(m["cases"]),12)
        self.assertEqual(m["model_calls"],0)
        self.assertEqual(m["independent_action_gold"],0)
        self.assertTrue(m["retrospective_not_contemporaneous"])
        self.assertGreater(m["source_words"],m["ledger_words"])
        self.assertLessEqual(m["ledger_words"],220)
        self.assertIn("SC_DECISION_288",common_feed())
        self.assertIn("SC_DECISION_288",deterministic_ledger())
    def test_oracle_metadata_not_in_decision_prompt(self):
        d,_=validated()
        ledger=deterministic_ledger()
        for t in d["tasks"]:
            p=decision_prompt(t,ledger)
            copy_t=copy.deepcopy(t)
            copy_t["reference_documentary_state"]="WRONG_ON_PURPOSE"
            copy_t["design_note"]="tampered"
            self.assertEqual(p,decision_prompt(copy_t,ledger))
            self.assertNotIn("reference_documentary_state",p)
            self.assertIn(t["decision_at"],p)
    def test_fail_closed_when_memory_exceeds_budget(self):
        with self.assertRaisesRegex(ValueError,"MEMORY_BUDGET"):
            bounded_memory("over " * 300)
        with self.assertRaisesRegex(ValueError,"MEMORY_BUDGET"):
            bounded_memory("")
    def test_compactor_same_feed_no_gold(self):
        c=compaction_prompt()
        self.assertIn(common_feed(),c)
        self.assertNotIn("reference_documentary_state",c)

if __name__=="__main__":unittest.main()
