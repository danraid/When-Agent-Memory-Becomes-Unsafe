from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from study.review import blind_sample, review
from study.runner import run, StudyGateError
ROOT=Path(__file__).resolve().parents[1]
PROTO=json.loads((ROOT/'protocol/STUDY_PLAN.json').read_text())
PAPER=json.loads((ROOT/'paper.json').read_text())
PAPER['api']=json.loads((ROOT/'study/model_config.json').read_text())

class BlindReviewTests(unittest.TestCase):
    def test_gold_labels_never_enter_review_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'mock'
            run(protocol=PROTO,paper=PAPER,split='development',mode='mock',episodes=2,steps=8,output=out)
            rows=json.loads((out/'observations.json').read_text())
            sample=blind_sample(rows)
            self.assertEqual(len(sample),8)
            as_text=json.dumps(sample)
            self.assertFalse(any('evaluation' in item for item in sample))
            self.assertNotIn('reference_action',as_text)
            self.assertNotIn('reference_policy',as_text)
            self.assertNotIn('final_correct',as_text)

    def test_mock_never_gets_low_cost_review_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'mock'
            run(protocol=PROTO,paper=PAPER,split='development',mode='mock',episodes=1,steps=8,output=out)
            with self.assertRaisesRegex(StudyGateError,'REAL_OBSERVED_PILOT'):
                review(data_dir=out,output=Path(d)/'review',
                       config=json.loads((ROOT/'study/reviewer_config.json').read_text()),ledger=Path(d)/'ledger')
if __name__=='__main__':
    unittest.main()
