import copy
import json
import tempfile
from pathlib import Path
import unittest

from article_hub.benchmark import CONDITIONS, generate_episode, make_prompt, expected_action
from article_hub.empirical import (ExperimentGateError, run_benchmark, validate_execution_gate,
                                   frozen_hash, judge_source_sha256, engine_source_sha256, paper_config_sha256)
from article_hub.judge import adjudicate, summarize
from scripts.hub import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
PAPER = json.loads((ROOT/'paper.json' if (ROOT/'paper.json').exists() else ROOT/'templates/article/paper.json').read_text())
PROTOCOL = json.loads((ROOT/'experiment_protocol.json' if (ROOT/'experiment_protocol.json').exists() else ROOT/'templates/article/experiment_protocol.json').read_text())


class BenchmarkTests(unittest.TestCase):
    def test_deterministic_episodes_and_split_isolation(self):
        a = generate_episode('test-only-secret', 'development', 0, 8)
        self.assertEqual(a, generate_episode('test-only-secret', 'development', 0, 8))
        self.assertNotEqual(a['content_sha256'], generate_episode('test-only-secret', 'pilot', 0, 8)['content_sha256'])
        self.assertEqual(a['events'][0]['actor'], a['policy']['blocked_actor'])

    def test_prompt_contains_no_expected_labels_or_future_events(self):
        a = generate_episode('test-seed', 'development', 0, 8)
        t = 4
        for name in CONDITIONS:
            prompt = make_prompt(a, t, name)
            self.assertNotIn('expected_action', prompt)
            self.assertNotIn('unsafe_final_approval', prompt)
            self.assertNotIn(json.dumps(a['events'][t+1]), prompt)
        self.assertIn('Original policy', make_prompt(a, 0, 'window_only'))
        self.assertNotIn('Constraint A', make_prompt(a, 3, 'window_only'))
        self.assertIn('Constraint A', make_prompt(a, 3, 'structured_memory'))
        self.assertNotIn('Constraint A', make_prompt(a, 3, 'structured_memory_ablated'))

    def test_independent_judge_and_guard_ablation(self):
        a = generate_episode('x', 'development', 0)
        ev = a['events'][0]  # blocked actor
        self.assertEqual(expected_action(a['policy'], ev), 'reject')
        bare = adjudicate(a['policy'], ev, '{"action":"approve"}', guard=False)
        guarded = adjudicate(a['policy'], ev, '{"action":"approve"}', guard=True)
        self.assertTrue(bare['unsafe_final_approval'])
        self.assertFalse(guarded['unsafe_final_approval'])
        self.assertFalse(guarded['raw_correct'])
        self.assertTrue(guarded['guard_overrode'])
        self.assertIsNone(adjudicate(a['policy'], ev, 'approve')['raw_action'])

    def test_mock_is_not_empirical_and_manifest_bound(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test'
            summary=run_benchmark(paper=PAPER, protocol=PROTOCOL, output=path, episodes=2, steps=8)
            self.assertEqual(summary['observations'], 2*8*len(CONDITIONS))
            self.assertEqual(summary['classification'], 'SYNTHETIC_TEST_FIXTURE_NOT_EMPIRICAL')
            self.assertEqual(verify_manifest(path)['verified_files'], 2)
            row=json.loads((path/'observations.json').read_text())[0]
            self.assertTrue(row['model'].startswith('MOCK'))
            (path/'observations.json').write_text('[]')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                verify_manifest(path)

    def test_live_requires_budget_and_config(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ExperimentGateError, 'DISABLED'):
                run_benchmark(paper=PAPER, protocol=PROTOCOL, output=Path(d)/'run', mode='live', ledger=Path(d)/'ledger')

    def test_holdout_requires_freeze_approval_and_private_seed(self):
        with self.assertRaisesRegex(ExperimentGateError, 'REAL_EMPIRICAL'):
            validate_execution_gate(split='confirmatory',mode='mock',protocol=PROTOCOL)
        with self.assertRaisesRegex(ExperimentGateError, 'FROZEN_PROTOCOL'):
            validate_execution_gate(split='confirmatory',mode='live',protocol=PROTOCOL)
        frozen = copy.deepcopy(PROTOCOL)
        frozen['confirmatory_design']={'episodes':2,'steps':7}
        lock={'status':'FROZEN_BY_AUTHOR','protocol_sha256':frozen_hash(frozen),
              'evaluator_sha256':judge_source_sha256(),
              'engine_sha256':engine_source_sha256(),
              'paper_config_sha256':paper_config_sha256(PAPER)}
        with self.assertRaisesRegex(ExperimentGateError, 'HUMAN_APPROVAL'):
            validate_execution_gate(split='confirmatory',mode='live',protocol=frozen,paper=PAPER,episodes=2,steps=7,lock=lock)
        approval={'approved':True,'author':'Human Author','protocol_sha256':frozen_hash(frozen)}
        with self.assertRaisesRegex(ExperimentGateError, 'PRIVATE_HOLDOUT_SEED'):
            validate_execution_gate(split='confirmatory',mode='live',protocol=frozen,paper=PAPER,episodes=2,steps=7,lock=lock,approval=approval,holdout_secret='short')
        self.assertTrue(validate_execution_gate(split='confirmatory',mode='live',protocol=frozen,paper=PAPER,episodes=2,steps=7,
            lock=lock,approval=approval,holdout_secret='long-private-seed-with-32-characters'))
        changed=copy.deepcopy(frozen)
        changed['hypothesis']='changed after freeze'
        with self.assertRaisesRegex(ExperimentGateError, 'FROZEN_PROTOCOL'):
            validate_execution_gate(split='confirmatory',mode='live',protocol=changed,paper=PAPER,episodes=2,steps=7,
                lock=lock,approval=approval,holdout_secret='long-private-seed-with-32-characters')

    def test_evaluations_are_paired(self):
        records=[{'condition':'window_only', 'case_id':'A', 'evaluation':{'raw_correct':True,'final_correct':True,
            'unsafe_raw_approval':False,'unsafe_final_approval':False,'false_final_reject':False,'invalid_json':False,'guard_overrode':False}},
             {'condition':'structured_memory','case_id':'B','evaluation':{'raw_correct':True,'final_correct':True,
            'unsafe_raw_approval':False,'unsafe_final_approval':False,'false_final_reject':False,'invalid_json':False,'guard_overrode':False}}]
        with self.assertRaisesRegex(ValueError,'Unpaired'):
            summarize(records)


if __name__ == '__main__':
    unittest.main()
