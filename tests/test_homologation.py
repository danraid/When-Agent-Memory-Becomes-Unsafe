"""Hub real-provider homologation gates: offline tests must never fake a PASS."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

from article_hub.budget import permit
from article_hub.benchmark import CONDITIONS, generate_episode, make_prompt
from article_hub.homologation import (live_config, blind_review, qualify_evidence,
                                      publish_homologation, HomologationError)
from article_hub.llm import request_advisory
from article_hub.empirical import run_benchmark
from article_hub.evidence import write_json
from scripts.hub import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
PAPER = json.loads((ROOT/'paper.json' if (ROOT/'paper.json').exists() else ROOT/'templates/article/paper.json').read_text())
PROTOCOL = json.loads((ROOT/'experiment_protocol.json' if (ROOT/'experiment_protocol.json').exists() else ROOT/'templates/article/experiment_protocol.json').read_text())


def synthetic_records():
    records=[]
    episode=generate_episode('homologation-test', 'development', 0, 4)
    for step in range(4):
        for condition in CONDITIONS:
            records.append({'case_id':episode['episode_id']+f'-{step:02d}',
                'condition':condition,'input_prompt':make_prompt(episode,step,condition),
                'raw_response':'{"action":"reject"}', 'model':'MOCK_NOT_PROVIDER',
                'provider_response_id': None,'usage':{'input_tokens':0,'output_tokens':0}})
    return records


class HomologationTests(unittest.TestCase):
    def test_unlimited_dollar_ceiling_only_and_finite_call_guard(self):
        limits={'max_usd':None,'max_calls':2,'max_input_tokens':10000,'max_output_tokens':10000}
        valid, reason=permit(limits,{'calls':0,'input_tokens':0,'output_tokens':0,'usd':'0'},
                             calls=1,input_tokens=300,output_tokens=100,usd='999999')
        self.assertTrue(valid)
        self.assertIn('USD_UNCAPPED',reason)
        invalid, reason=permit(limits,{'calls':2,'input_tokens':0,'output_tokens':0,'usd':'0'},
                               calls=1,input_tokens=1,output_tokens=1,usd='0')
        self.assertFalse(invalid)
        self.assertEqual(reason,'CALLS_CAP')

    def test_live_config_has_no_monetary_ceiling_but_finite_calls(self):
        cfg=live_config(PAPER,max_calls=52)
        self.assertTrue(cfg['api']['enabled'])
        self.assertIsNone(cfg['api']['budget']['max_usd'])
        self.assertEqual(cfg['api']['budget']['max_calls'],52)
        self.assertEqual(PAPER['api']['enabled'],False)

    def test_model_advisory_with_uncapped_dollars_is_still_tallied(self):
        with tempfile.TemporaryDirectory() as folder:
            def transport(key, body, timeout):
                return {'id':'resp_healthy', 'output':[{'type':'message','content':[{'type':'output_text','text':'Review advisory only'}]}],
                        'usage':{'input_tokens':9,'output_tokens':5}}
            cfg=live_config(PAPER,max_calls=2)['api']
            r=request_advisory('Test prompt',cfg,Path(folder)/'ledger.json',key='test-not-real',transport=transport)
            self.assertEqual(r['provider_response_id'],'resp_healthy')
            ledger=json.loads((Path(folder)/'ledger.json').read_text())
            self.assertGreater(float(ledger['usd']),0)
            self.assertEqual(ledger['calls'],1)

    def test_mock_never_homologates_and_empty_provenance_rejected(self):
        rows=synthetic_records()
        summary={'classification':'SYNTHETIC_TEST_FIXTURE_NOT_EMPIRICAL','mode':'mock','split':'development'}
        reviews={'classification':'BLIND_LLM_ADVISORY_NOT_PEER_REVIEW','gold_labels_supplied_to_reviewers':False,
                 'reports':[{'model':'gpt-6-luna','provider_response_id':'x','review_text':'ok','scientific_approval':False}]*2}
        valid,reason=qualify_evidence(rows,summary,reviews,expected_cases=4)
        self.assertFalse(valid)
        self.assertEqual(reason,'NO_REAL_GPT_EXECUTION')
        summary['mode']='live';summary['classification']='EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED'
        valid,reason=qualify_evidence(rows,summary,reviews,expected_cases=4)
        self.assertFalse(valid)
        self.assertEqual(reason,'MISSING_DUPLICATE_OR_INVALID_PROVIDER_RESPONSE_IDS')

    def test_blind_reviews_receive_no_gold_labels(self):
        seen=[]
        def fake(prompt,config,ledger):
            seen.append((prompt,config['model']))
            return {'classification':'AI_ADVISORY_NOT_INDEPENDENT_REVIEW','model':'gpt-6-luna',
                    'provider_response_id':'resp_review'+str(len(seen)), 'advisory_text':'A caveat',
                    'observed_usage':{'input_tokens':12,'output_tokens':8},
                    'prompt_sha256':'abc'}
        rows=synthetic_records()
        result=blind_review(rows,live_config(PAPER,max_calls=100)['api'],'/nonexistent/ledger.json',request_fn=fake)
        self.assertEqual(len(result['reports']),2)
        self.assertEqual(result['sample_count'],10)
        self.assertEqual({r[1] for r in seen},{'gpt-6-luna'})
        self.assertTrue(result['gold_labels_supplied_to_reviewers'] is False)
        self.assertTrue(all('"expected"' not in x[0] and 'expected_action' not in x[0] for x in seen))

    def test_complete_mock_engineering_artifacts_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'run'
            run_benchmark(paper=PAPER,protocol=PROTOCOL,output=path,episodes=1,steps=4)
            summary=json.loads((path/'summary.json').read_text())
            rows=json.loads((path/'observations.json').read_text())
            r={'classification':'BLIND_LLM_ADVISORY_NOT_PEER_REVIEW','gold_labels_supplied_to_reviewers':False,'reports':[]}
            valid,_=qualify_evidence(rows,summary,r,expected_cases=4)
            self.assertFalse(valid)

    def test_observed_artifact_manifest_matches_actual_files(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            empirical=out/'empirical';empirical.mkdir()
            rows=synthetic_records()
            for row_index, r in enumerate(rows):
                r['provider_response_id']='resp_observed_'+str(row_index)
                r['model']='gpt-6.1-terra'
                r['usage']={'input_tokens':30,'output_tokens':6}
            write_json(empirical/'observations.json',rows)
            write_json(empirical/'summary.json',{'classification':'EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED',
                                                 'mode':'live','split':'development'})
            write_json(empirical/'manifest.json',{'classification':'test','scientifically_approved':False,'submission_authorized':False,'files':[]})
            reviews={'classification':'BLIND_LLM_ADVISORY_NOT_PEER_REVIEW','gold_labels_supplied_to_reviewers':False,
                     'reports':[{'model':'gpt-6-luna','provider_response_id':'resp_review_a','review_text':'note','scientific_approval':False},{'model':'gpt-6-luna','provider_response_id':'resp_review_b','review_text':'note','scientific_approval':False}]}
            write_json(out/'reviewers.json',reviews)
            cfg=live_config(PAPER,max_calls=22)
            result=publish_homologation(out/'validation',source=ROOT/'scripts/homologate.py',
                                        reviewer=out/'reviewers.json',config=cfg,empirical_dir=empirical,expected_cases=4)
            self.assertEqual(result['status'],'ENGINEERING_HOMOLOGATED')
            self.assertEqual(verify_manifest(out)['verified_files'],5)
            (out/'reviewers.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'mismatch'):
                verify_manifest(out)


if __name__ == '__main__':
    unittest.main()
