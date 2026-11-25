import unittest
from scripts.r01_cycle23_mapping import frame,payload,MODELS,validate
class MappingTests(unittest.TestCase):
    def test_frame(self):
        c=frame(None);self.assertEqual(len(c),11)
        self.assertEqual(len({x["task_id"] for x in c}),11)
        for x in c:
            self.assertEqual(set(x),{"task_id","question","requested_mock_action"})
            payload(MODELS[0],x)
    def test_schema(self):
        with self.assertRaises(ValueError):validate('{"decision":"APPROVE"}',{})
