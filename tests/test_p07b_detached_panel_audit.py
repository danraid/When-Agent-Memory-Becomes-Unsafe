"""Presentation-only envelope recovery is bounded and fail-closed."""
import unittest
from scripts.p07b_detached_panel_audit import remove_exact_envelope, PanelAuditError
from scripts.p07b_ai_panel import parse_vote
import json


class P07BDetachedPanelTests(unittest.TestCase):
    def test_single_complete_fence_removed_without_changing_json(self):
        original = {"decision":"supported",
                    "quoted_evidence":"Superseded-By: 387",
                    "reason":"Document header directly and explicitly identifies the replacement.",
                    "confidence":0.9,"authority_semantics_resolved":False}
        body=json.dumps(original)
        wrapped=chr(96)*3+"json\n"+body+"\n"+chr(96)*3
        recovered,changed=remove_exact_envelope(wrapped)
        self.assertEqual(recovered,body)
        self.assertTrue(changed)
        self.assertEqual(parse_vote(recovered,"Superseded-By: 387"),original)

    def test_refuses_nested_or_partial_fences(self):
        fence=chr(96)*3
        with self.assertRaisesRegex(PanelAuditError,"NESTED_FENCE"):
            remove_exact_envelope(fence+"json\n{\"x\":\""+fence+"\"}\n"+fence)
        candidate,normalized=remove_exact_envelope(fence+"json\n{\"valid\":true}")
        self.assertFalse(normalized)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(candidate)


if __name__=="__main__":
    unittest.main()
