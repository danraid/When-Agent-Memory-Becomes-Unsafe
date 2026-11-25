import unittest
from scripts.r01_operational_environment import prepare,run_episode,Sandbox
from scripts.r01_operational_oracle import controls
class OperationalTests(unittest.TestCase):
    def test_controls(self):
        r=controls()
        self.assertEqual(r["positive_oracle_controls"],7)
        self.assertEqual(r["incorrect_decision_controls_rejected"],14)
        self.assertEqual(r["wrong_scope_controls_blocked"],7)
    def test_partition_and_time(self):
        cases=prepare()
        self.assertEqual(len(cases),7)
        self.assertNotIn("Q04",[x["task_id"] for x in cases])
        self.assertNotIn("Q04-R1",[x["task_id"] for x in cases])
        self.assertTrue(all(r["published_at"]<=c["cutoff"] for c in cases for r in c["records"]))
    def test_bad_source_and_nonapproval_effect(self):
        c=prepare()[0]
        for p in ({"decision":"APPROVE","action":c["requested_mock_action"],"source_ids":["future"]},
                  {"decision":"ABSTAIN","action":c["requested_mock_action"],"source_ids":[]}):
            self.assertEqual(run_episode(c,p)["final_state"],[])
    def test_single_terminal_proposal_and_reset(self):
        c=prepare()[0]
        p={"decision":"APPROVE","action":c["requested_mock_action"],"source_ids":[]}
        s=Sandbox(c)
        try:
            self.assertTrue(s.execute(p)["state_changed"])
            with self.assertRaises(ValueError):s.execute(p)
        finally:s.close()
        self.assertEqual(run_episode(c,p)["initial_state_sha256"],run_episode(c,{"decision":"ABSTAIN","action":None,"source_ids":[]})["initial_state_sha256"])
