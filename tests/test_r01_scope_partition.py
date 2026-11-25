import unittest
from scripts.r01_scope_partition import partition
class TestScopePartition(unittest.TestCase):
    def test_exclusion(self):
        a,b=partition([{"id":"Q03"},{"id":"Q04"}],{"exclude_from_scored_comparison":["Q04"]})
        self.assertEqual([x["id"] for x in a],["Q03"])
        self.assertEqual([x["id"] for x in b],["Q04"])
    def test_unknown_and_duplicate(self):
        for rows in ([{"id":"Q03"}],[{"id":"Q04"},{"id":"Q04"}]):
            with self.assertRaises(ValueError):partition(rows,{"exclude_from_scored_comparison":["Q04"]})
