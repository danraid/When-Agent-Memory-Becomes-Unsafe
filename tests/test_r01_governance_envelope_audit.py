import unittest
from scripts.r01_governance_envelope_audit import unwrap
class TestEnvelope(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(unwrap('```json\n{"decision":"ABSTAIN"}\n```'),('{"decision":"ABSTAIN"}',True))
        self.assertEqual(unwrap('{"decision":"ABSTAIN"}'),('{"decision":"ABSTAIN"}',False))
    def test_multiple_rejected(self):
        with self.assertRaises(ValueError): unwrap('```json\n{}\n```\n```json\n{}\n```')
