"""Scientific source parity and evaluator isolation for R03."""
import copy
import json
from pathlib import Path
import unittest
from temporal_v3.generator import generate_episode
from scripts.r03_common_authority_live_dev import build_prompt,source_packet,validate_pair,ARMS

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=json.loads((ROOT/"protocol/R03_SHARED_AUTHORITY_SOURCE_DEVELOPMENT_V1.json").read_text())

class CommonAuthorityTests(unittest.TestCase):
    def test_pilot_preconditions_and_call_bound(self):
        self.assertEqual(PROTOCOL["episodes"],2)
        self.assertEqual(PROTOCOL["steps"],18)
        self.assertEqual(PROTOCOL["approved_live_calls_upper_bound"],82)
        self.assertFalse(PROTOCOL["confirmatory_holdout"])
        self.assertFalse(PROTOCOL["external_submission"])
    def test_shared_source_always_sealed(self):
        for i in range(2):
            ep=generate_episode("WAMBU-R03-COMMON-SOURCE-20261119","development",i,18)
            for item in ep["items"]:
                a=build_prompt(item,ARMS[0],"sample summary not authoritative")
                b=build_prompt(item,ARMS[1],"sample summary not authoritative")
                self.assertTrue(validate_pair(item,a,b))
                self.assertIn(source_packet(item),a)
                self.assertIn(source_packet(item),b)
                self.assertEqual(a.count("COMMON AUTHORISED SOURCE PACKET:"),1)
                self.assertEqual(b.count("COMMON AUTHORISED SOURCE PACKET:"),1)
    def test_evaluator_labels_cannot_change_inputs(self):
        item=generate_episode("WAMBU-R03-COMMON-SOURCE-20261119","development",0,18)["items"][5]
        modified=copy.deepcopy(item)
        modified["reference_policy"]["blocked_actor"]="FAKE"
        modified["reference_action"]="approve"
        modified["probe_kind"]="changed_evaluator_label"
        for arm in ARMS:
            self.assertEqual(build_prompt(item,arm,"summary"),build_prompt(modified,arm,"summary"))
    def test_unknown_arm_and_missing_policy_fail(self):
        item=generate_episode("WAMBU-R03-COMMON-SOURCE-20261119","development",0,18)["items"][0]
        with self.assertRaisesRegex(ValueError,"INVALID_EXPERIMENT_ARM"):
            build_prompt(item,"cheating_policy_arm","summary")
        damaged=copy.deepcopy(item)
        damaged["history_before"]=("REQUEST OBSERVED 0",)
        with self.assertRaisesRegex(ValueError,"MISSING_VISIBLE_AUTHORITATIVE_SOURCE"):
            source_packet(damaged)

if __name__=="__main__":unittest.main()
