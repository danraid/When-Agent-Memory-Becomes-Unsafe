import unittest
from scripts.r01_cycle25_mapping import frame,payload,MODELS,typed_action
class TypedTierTests(unittest.TestCase):
    def test_frame(self):
        c=frame(None);self.assertEqual(len(c),6)
        self.assertEqual({x["task_id"] for x in c},{"Q13","Q14","Q15","Q16","T1","T2"})
        for x in c:
            a=x["requested_mock_action"]
            self.assertNotIn("version",a)
            self.assertIn(a["support_tier"],(2,3))
            p=payload(MODELS[0],x)["messages"][0]["content"]
            self.assertNotIn('"task_id"',p)
            self.assertNotIn('"records"',p)
        self.assertEqual(c[0]["requested_mock_action"]["support_tier"],2)
        self.assertEqual(c[2]["requested_mock_action"]["support_tier"],3)
        self.assertEqual(c[4]["requested_mock_action"]["support_tier"],3)
        self.assertEqual(c[5]["requested_mock_action"]["support_tier"],2)
    def test_bad_type(self):
        with self.assertRaises(ValueError):typed_action({"operation":"set_mock_platform_tier","target":"fixture","version":"99"})
