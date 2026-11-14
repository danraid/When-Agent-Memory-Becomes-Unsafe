import json
from pathlib import Path
import unittest
from article_hub.budget import permit
from article_hub.evidence import smoke
from article_hub.state import DEPS, plan, validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        source = root/'research_state.json'
        if not source.exists():
            source = root/'templates/article/research_state.json'
        self.state = json.loads(source.read_text(encoding='utf-8'))

    def test_all_stages_unimplemented_by_default(self):
        results = plan(self.state)
        self.assertEqual(len(results), 11)
        self.assertTrue(all(not d.ready and d.reason == 'RUNNER_NOT_IMPLEMENTED' for d in results))

    def test_confirmatory_success_requires_approval(self):
        for stage in list(DEPS)[:7]:
            self.state['stages'][stage] = 'TECHNICAL_PASS'
        with self.assertRaisesRegex(ValueError, 'preregistration lock'):
            validate(self.state)

    def test_submission_success_requires_approval(self):
        for stage in DEPS:
            self.state['stages'][stage] = 'TECHNICAL_PASS'
        self.state['human_gates']['preregistration_locked'] = True
        self.state['human_gates']['confirmatory_release_approved'] = True
        with self.assertRaisesRegex(ValueError, 'submission state'):
            validate(self.state)

    def test_confirmatory_not_eligible_with_only_upstream_pass(self):
        for stage in list(DEPS)[:6]:
            self.state['stages'][stage] = 'TECHNICAL_PASS'
        result = next(d for d in plan(self.state, {'confirmatory'}) if d.stage == 'confirmatory')
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, 'HUMAN_CONFIRMATORY_GATE_CLOSED')

    def test_budget_caps(self):
        limits = {'max_calls': 100, 'max_input_tokens': 500, 'max_output_tokens': 200, 'max_usd': '1.00'}
        spent = {'calls': 99, 'input_tokens': 30, 'output_tokens': 10, 'usd': '0.90'}
        self.assertEqual(permit(limits, spent, calls=2, input_tokens=1, output_tokens=1, usd='0.01'), (False, 'CALLS_CAP'))
        self.assertEqual(permit(limits, spent, calls=1, input_tokens=1, output_tokens=1, usd='0.11'), (False, 'USD_CAP'))
        self.assertTrue(permit(limits, spent, calls=1, input_tokens=1, output_tokens=1, usd='0.10')[0])

    def test_invalid_prior_budget_usage_rejected(self):
        limits={'max_calls':2,'max_input_tokens':100,'max_output_tokens':50,'max_usd':'1.00'}
        spent={'calls':-1,'input_tokens':0,'output_tokens':0,'usd':'0'}
        with self.assertRaises(ValueError):
            permit(limits,spent,calls=1,input_tokens=10,output_tokens=10,usd='0.01')

    def test_smoke_reproducible_non_science(self):
        a = smoke(2026, 64)
        self.assertEqual(a, smoke(2026, 64))
        self.assertNotEqual(a['data_sha256'], smoke(2027, 64)['data_sha256'])
        self.assertFalse(a['science_claim'])
        self.assertEqual(a['classification'], 'SYNTHETIC_TEST_FIXTURE')
