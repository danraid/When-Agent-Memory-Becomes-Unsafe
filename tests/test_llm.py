from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest

from article_hub.llm import AdvisoryError, request_advisory


class LLMTests(unittest.TestCase):
    def setUp(self):
        self.config={'enabled':True,'model':'test-response-model', 'max_output_tokens':128,
            'pricing':{'input_usd_per_million':'1.00','output_usd_per_million':'2.00'},
            'budget':{'max_calls':2,'max_input_tokens':8000,'max_output_tokens':256,'max_usd':'0.02'}}
        self.response={'id':'synthetic-id','output':[{'type':'message','content':[{'type':'output_text','text':'Advisory text only'}]}],
            'usage':{'input_tokens':10,'output_tokens':4}}

    def test_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.config['enabled']=False
            with self.assertRaisesRegex(AdvisoryError,'DISABLED'):
                request_advisory('Hello',self.config,Path(tmp)/'ledger.json',key='fake')
            self.assertFalse((Path(tmp)/'ledger.json').exists())

    def test_explicit_budget_and_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger.json'
            calls=[]
            def fake(key,payload,timeout):
                calls.append((key,payload,timeout))
                return self.response
            r=request_advisory('Test prompt',self.config,ledger,key='TEST-KEY',transport=fake)
            self.assertEqual(r['classification'],'AI_ADVISORY_NOT_INDEPENDENT_REVIEW')
            self.assertFalse(r['scientific_approval'])
            self.assertEqual(r['observed_usage']['input_tokens'],10)
            self.assertEqual(calls[0][1]['store'],False)
            self.assertNotIn('TEST-KEY',ledger.read_text())
            self.assertEqual(json.loads(ledger.read_text())['calls'],1)
            request_advisory('Test prompt',self.config,ledger,key='TEST-KEY',transport=fake)
            with self.assertRaisesRegex(AdvisoryError,'CALLS_CAP'):
                request_advisory('Test prompt',self.config,ledger,key='TEST-KEY',transport=fake)
            self.assertEqual(len(calls),2)

    def test_missing_pricing_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            del self.config['pricing']
            with self.assertRaisesRegex(AdvisoryError,'pricing'):
                request_advisory('Test',self.config,Path(tmp)/'ledger',key='fake',transport=lambda *args: self.response)

    def test_unknown_provider_outcome_keeps_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger.json'
            with self.assertRaisesRegex(AdvisoryError,'UNKNOWN_PROVIDER_OUTCOME'):
                request_advisory('Test',self.config,ledger,key='fake',transport=lambda *args: 1/0)
            self.assertEqual(json.loads(ledger.read_text())['calls'],1)

    def test_budget_rejects_bad_price(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.config['pricing']['input_usd_per_million']='NaN'
            with self.assertRaises(AdvisoryError):
                request_advisory('Test',self.config,Path(tmp)/'ledger',key='fake',transport=lambda *args: self.response)
