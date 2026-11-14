"""V3 scientific instrument correctness, leakage and fail-closed regression tests."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from temporal_v3.generator import generate_episode
from temporal_v3.methods import (decision_prompt, typed_retention, PAID_ARMS,
                                  UPSTREAM_CLASSIFICATION, guard_decision)
from temporal_v3.runner import run, verify, describe, STATUS_MOCK, _score
from temporal_v3.review import sample_blind
from study.tasks import expected_action, ledger_from_authorised_events

ROOT=Path(__file__).resolve().parents[1]
PROTO=json.loads((ROOT/'protocol/TEMPORAL_V3.json').read_text())
CONFIG=json.loads((ROOT/'study/model_config.json').read_text())

class TemporalV3Tests(unittest.TestCase):
 def setUp(self):
  self.episode=generate_episode(PROTO['seeds']['development'],'development',3,18)

 def test_split_and_episode_are_independent(self):
  x=generate_episode(PROTO['seeds']['pilot'],'pilot',3,18)
  self.assertNotEqual(x['public_stream_sha256'],self.episode['public_stream_sha256'])
  with self.assertRaisesRegex(ValueError,'CONFIRMATORY_SPLIT_NOT_OPEN'):
   generate_episode('SECRET_DO_NOT_USE','confirmatory',3,18)

 def test_revocations_are_real_counterfactuals(self):
  for x in self.episode['items']:
   if x['probe_kind']=='stale_rule_revocation':
    self.assertEqual(x['reference_action'],'approve')
   if x['probe_kind']=='new_rule_enforcement':
    self.assertEqual(x['reference_action'],'reject')
  self.assertEqual(sum(x['probe_kind']=='stale_rule_revocation' for x in self.episode['items']),4)
  self.assertEqual(sum(x['probe_kind']=='new_rule_enforcement' for x in self.episode['items']),4)

 def test_public_stream_reconstructs_ledger_not_gold(self):
  for x in self.episode['items']:
   self.assertEqual(ledger_from_authorised_events(x['history_before']),x['public_policy_ledger'])
   y=copy.deepcopy(x); y['reference_policy']['blocked_actor']='FAKE'
   for arm in PAID_ARMS:
    self.assertEqual(decision_prompt(x,arm,'TEST SUMMARY'),decision_prompt(y,arm,'TEST SUMMARY'))

 def test_no_gold_in_prompt_any_arm(self):
  for x in self.episode['items']:
   for arm in PAID_ARMS:
    p=decision_prompt(x,arm,'TEST SUMMARY')
    self.assertNotIn('reference_action',p)
    self.assertNotIn('reference_policy',p)
    self.assertNotIn('probe_kind',p)
    self.assertNotIn('stale_rule_revocation',p)

 def test_stale_rule_probes_start_after_authorised_change(self):
  for x in self.episode['items']:
   if x['probe_kind']=='stale_rule_revocation':
    self.assertEqual(x['step'] % 4,0)
    self.assertGreater(x['policy_version'],1)

 def test_oracle_not_used_by_guard(self):
  row=self.episode['items'][4]
  self.assertEqual(row['probe_kind'],'stale_rule_revocation')
  value=guard_decision(row,'{"action":"approve"}')
  corrupted=copy.deepcopy(row)
  corrupted['reference_policy']['blocked_actor']='FAKE_REFERENCE_ONLY'
  corrupted['reference_action']='reject'
  self.assertEqual(value,guard_decision(corrupted,'{"action":"approve"}'))
  self.assertEqual(value,'approve')

 def test_guard_blocks_genuinely_new_restriction(self):
  row=self.episode['items'][5]
  self.assertEqual(row['probe_kind'],'new_rule_enforcement')
  self.assertEqual(guard_decision(row,'{"action":"approve"}'),'reject')
  self.assertTrue(_score(row,'{"action":"approve"}')['missed_new_enforcement'])
  self.assertFalse(_score(row,'{"action":"approve"}',final='reject')['unsafe_final_approval'])

 def test_adapted_typed_retention_is_not_claimed_upstream_replication(self):
  self.assertIn('NOT_OFFICIAL_REPRODUCTION',UPSTREAM_CLASSIFICATION)
  row=self.episode['items'][16]
  retained=typed_retention(row)
  events=[line for line in row['history_before'] if line.startswith(('INITIAL AUTHORISED POLICY:', 'AUTHORISED POLICY AMENDMENT #'))]
  self.assertTrue(all(x in retained for x in events))
  self.assertIn('superseded',retained)
  with self.assertRaisesRegex(ValueError,'COMPACTION_UNSAFE'):
   typed_retention(row,max_policy_tokens=2)

 def test_mock_never_masquerades_as_empirical(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'results'
   r=run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
         mode='mock',split='development',episodes=2,steps=18)
   self.assertEqual(r['status'],STATUS_MOCK)
   self.assertEqual(r['observed_real_provider_calls'],0)
   self.assertEqual(len(json.loads((root/'observations.json').read_text())),2*18*6)
   self.assertEqual(verify(root,PROTO,CONFIG)['verified_files'],4)
   with self.assertRaisesRegex(ValueError,'OUTPUT_DIRECTORY_MUST_BE_EMPTY'):
    run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
        mode='mock',split='development',episodes=2,steps=18)

 def test_tamper_manifest_detected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'out'
   run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
       mode='mock',split='development',episodes=1,steps=18)
   with (root/'observations.json').open('a') as f:f.write('tamper')
   with self.assertRaisesRegex(ValueError,'EVIDENCE_HASH'):
    verify(root,PROTO,CONFIG)

 def test_blind_sampling_is_paired_and_excludes_labels(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'out'
   run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
       mode='mock',split='development',episodes=2,steps=18)
   rows=json.loads((root/'observations.json').read_text())
   a=sample_blind(rows)
   self.assertEqual(a,sample_blind(rows))
   self.assertEqual(len(a),6*5)
   per={arm:{x['case_id'] for x in a if x['arm']==arm} for arm in PAID_ARMS}
   self.assertTrue(all(v==next(iter(per.values())) for v in per.values()))
   serial=json.dumps(a)
   for forbid in ['reference_action','reference_policy','stale_rule_wrongful_reject']:
    self.assertNotIn(forbid,serial)
   self.assertTrue(all('evaluation' not in row for row in a))

 def test_unknown_scientific_promotion_fails_closed(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'out'
   run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
       mode='mock',split='development',episodes=1,steps=18)
   manifest=json.loads((root/'manifest.json').read_text())
   manifest['scientifically_approved']=True
   (root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'ILLEGAL_SCIENTIFIC_GATE_PROMOTION'):
    verify(root,PROTO,CONFIG)

 def test_protocol_and_source_mismatch_prevent_reinterpreting_old_run(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'out'
   run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
       mode='mock',split='development',episodes=1,steps=18)
   altered=dict(PROTO);altered['question']='ALTERED AFTER OBSERVATION'
   with self.assertRaisesRegex(ValueError,'FROZEN_EVIDENCE_SOURCE_MISMATCH'):
    verify(root,altered,CONFIG)

 def test_balanced_episodes_restrict_inference(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'out'
   run(protocol=PROTO,config=CONFIG,output=root,ledger=Path(tmp)/'ledger.json',
       mode='mock',split='development',episodes=2,steps=18)
   obs=json.loads((root/'observations.json').read_text())
   report=describe(obs,episodes=2,steps=18)
   self.assertTrue(report['no_p_values_or_confirmatory_CI'])
   self.assertEqual(len(report['paired_post_compaction_episodes']),2)

if __name__=='__main__':unittest.main()
