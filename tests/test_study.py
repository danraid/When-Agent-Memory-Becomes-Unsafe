"""Scientific-instrument invariants are deterministic and network-free."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from study import tasks, prompts, runner, analysis

ROOT=Path(__file__).resolve().parents[1]
PROTO=json.loads((ROOT/'protocol/STUDY_PLAN.json').read_text())
PAPER=json.loads((ROOT/'paper.json').read_text())
PAPER['api']=json.loads((ROOT/'study/model_config.json').read_text())


class StudyTests(unittest.TestCase):
    def test_reproducible_episodes(self):
        a=tasks.generate_episode(PROTO['development_seeds']['development'],'development',1,12)
        self.assertEqual(a,tasks.generate_episode(PROTO['development_seeds']['development'],'development',1,12))
        self.assertNotEqual(a,tasks.generate_episode(PROTO['development_seeds']['pilot'],'pilot',1,12))

    def test_both_safe_and_reject_opportunities(self):
        ep=tasks.generate_episode(PROTO['development_seeds']['development'],'development',0,12)
        labels={r['reference_action'] for r in ep['items']}
        self.assertEqual(labels,{'approve','reject'})
        self.assertEqual(ep['items'][4]['policy_version'],2)
        self.assertEqual(ep['items'][8]['policy_version'],3)

    def test_reference_action_independent_of_agent(self):
        ep=tasks.generate_episode(PROTO['development_seeds']['development'],'development',0,12)
        x=ep['items'][0]
        self.assertEqual(x['reference_action'],tasks.expected_action(x['reference_policy'],x['request']))
        self.assertFalse(any('reference_action' in line for line in x['history_before']))

    def test_no_reference_labels_or_future_events_in_prompts(self):
        ep=tasks.generate_episode(PROTO['development_seeds']['development'],'development',1,12)
        for i,x in enumerate(ep['items']):
            for c in prompts.PAID_DECISION_CONDITIONS:
                s=prompts.decision_prompt(x,c,'memory placeholder')
                self.assertNotIn('reference_action',s)
                self.assertNotIn('reference_policy',s)
                if i+1<len(ep['items']):
                    self.assertNotIn('CURRENT REQUEST:\n'+json.dumps(ep['items'][i+1]['request'],sort_keys=True),s)

    def test_actual_recursive_compaction_prompt_carries_previous_summary(self):
        p=prompts.compaction_prompt('prior-memory-marker',('log-1','log-2'))
        self.assertIn('prior-memory-marker',p)
        self.assertIn('log-2',p)
        self.assertNotIn('reference_action',p)

    def test_guard_reuses_raw_output_and_only_safety_overrides(self):
        ep=tasks.generate_episode(PROTO['development_seeds']['development'],'development',0,12)
        target=next(x for x in ep['items'] if x['reference_action']=='reject')
        normal=analysis.evaluate(target,'{"action":"approve"}',guarded=False)
        guarded=analysis.evaluate(target,'{"action":"approve"}',guarded=True)
        self.assertTrue(normal['unsafe_final_approval'])
        self.assertFalse(guarded['unsafe_final_approval'])
        self.assertTrue(guarded['guard_overrode'])

    def test_strict_json(self):
        for payload in ('not json','{"action":"approve","why":"extra"}','["approve"]','{"action":"maybe"}'):
            self.assertIsNone(analysis.parse_action(payload))
        self.assertEqual(analysis.parse_action('{"action":"reject"}'),'reject')

    def test_mock_report_tamper_detection_and_paired_counts(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'observed'
            result=runner.run(protocol=PROTO,paper=PAPER,split='development',mode='mock',episodes=2,steps=12,output=out)
            self.assertEqual(result['observed_decisions'],120)
            self.assertEqual(result['observed_compactions'],6)
            self.assertEqual(runner.verify_output(out)['verified_files'],4)
            rows=json.loads((out/'observations.json').read_text())
            guards=[r for r in rows if r['condition']=='pinned_ledger_guard']
            self.assertTrue(all(x['derived_from']=='pinned_ledger' for x in guards))
            self.assertEqual(len({r['case_id'] for r in guards}),24)
            (out/'observations.json').write_text('[]')
            with self.assertRaisesRegex(runner.StudyGateError,'DIGEST_MISMATCH'):
                runner.verify_output(out)

    def test_mock_is_not_real_science(self):
        with tempfile.TemporaryDirectory() as d:
            x=runner.run(protocol=PROTO,paper=PAPER,split='development',mode='mock',episodes=1,steps=8,output=Path(d)/'run')
            self.assertEqual(x['status'],'MOCK_INSTRUMENT_SMOKE_COMPLETE')
            self.assertFalse(x['scientifically_approved'])
            self.assertFalse(x['submission_authorized'])
            self.assertEqual(x['observed_provider_calls'],0)
            self.assertIn('DESCRIPTIVE',x['analysis']['candidate_primary_after_two_compactions']['inference'])

    def test_no_mock_pilot_or_confirmatory(self):
        for split in ('pilot','confirmatory'):
            with self.assertRaises(runner.StudyGateError):
                runner.guard_split(protocol=PROTO,paper=PAPER,split=split,mode='mock',episodes=1,steps=12)

    def test_confirmatory_requires_locked_science_and_secret(self):
        with self.assertRaisesRegex(runner.StudyGateError,'SEED_REQUIRED'):
            runner.guard_split(protocol=PROTO,paper=PAPER,split='confirmatory',mode='live',episodes=2,steps=12)
        with self.assertRaisesRegex(runner.StudyGateError,'FROZEN_AUTHOR_PROTOCOL_REQUIRED'):
            runner.guard_split(protocol=PROTO,paper=PAPER,split='confirmatory',mode='live',episodes=2,steps=12,private_seed='private-'*8)

    def test_locked_source_identity_mismatch_fails(self):
        lock={'status':'FROZEN_BY_AUTHOR','protocol_sha256':runner.config_sha256(PROTO),
              'study_sources_sha256':'bad','paper_config_sha256':runner.config_sha256(PAPER)}
        with self.assertRaisesRegex(runner.StudyGateError,'FROZEN_CODE_AND_MODEL_MUST_MATCH'):
            runner.guard_split(protocol=PROTO,paper=PAPER,split='confirmatory',mode='live',episodes=2,steps=12,lock=lock,private_seed='private-'*8)

    def test_api_call_count_is_bounded_even_without_usd_cap(self):
        too_small=copy.deepcopy(PAPER)
        too_small['api']['budget']['max_calls']=1
        self.assertIsNone(PAPER['api']['budget']['max_usd'])
        with self.assertRaisesRegex(runner.StudyGateError,'PLANNED_CALLS_EXCEED_FINITE_BOUND'):
            runner.guard_split(protocol=PROTO,paper=too_small,split='development',mode='live',episodes=1,steps=8)

    def test_source_hash_is_stable_and_nonempty(self):
        self.assertEqual(len(runner.sources_sha256()),64)
        self.assertEqual(runner.sources_sha256(),runner.sources_sha256())

    def test_data_in_public_repo_does_not_include_private_seed(self):
        self.assertNotIn('HUB_HOLDOUT_SEED',json.dumps(PROTO['development_seeds']))
        self.assertIsNone(PROTO['confirmatory_design']['episodes'])

if __name__ == '__main__':
    unittest.main()
