import json
from pathlib import Path
import unittest

from article_hub.discovery import (normalize_doi, openalex_work, verify_crossref,
    discover, fixture_discovery, DiscoveryError)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(__file__).resolve().parent
        self.fixtures = json.loads((self.base/'fixtures/openalex_mock.json').read_text())['results']

    def test_doi_normalization(self):
        self.assertEqual(normalize_doi('https://doi.org/10.9999/FICTIONAL.'), '10.9999/fictional')
        self.assertIsNone(normalize_doi('invalid'))

    def test_fixture_never_metadata_verified(self):
        result = fixture_discovery(self.fixtures)
        self.assertEqual(result['record_count'], 2)
        self.assertTrue(all(r['status'] == 'SYNTHETIC_TEST_FIXTURE' for r in result['records']))
        self.assertFalse(result['scientifically_approved'])

    def test_crossref_never_scientific_approval(self):
        record = openalex_work(self.fixtures[1])
        verified = verify_crossref(record, {'DOI': '10.9999/fictional-identifier',
               'title': ['Synthetic record about multi-agent evaluation']})
        self.assertEqual(verified['status'], 'METADATA_VERIFIED')
        self.assertEqual(verified['metadata_check'], 'CROSSREF_IDENTITY_MATCH')
        self.assertFalse(verified['scientifically_approved'])
        self.assertFalse(verified['full_text_verified'])

    def test_crossref_mismatched_title_not_verified(self):
        record = openalex_work(self.fixtures[1])
        verify_crossref(record, {'DOI':'10.9999/fictional-identifier', 'title':['Different study']})
        self.assertEqual(record['status'], 'CANDIDATE')

    def test_bounded_deduplicated_live_adapter_mock(self):
        calls=[]
        def fake(url):
            calls.append(url)
            if 'api.openalex' in url:
                return {'results': [self.fixtures[1], self.fixtures[1]]}
            if 'api.crossref.org' in url:
                return {'message':{'DOI':'10.9999/fictional-identifier','title':['Synthetic record about multi-agent evaluation']}}
            raise AssertionError('Unexpected endpoint')
        result = discover(['agent reliability','multiagent failures'], per_query=2,
                           crossref_limit=1, fetcher=fake)
        self.assertEqual(result['record_count'], 1)
        self.assertEqual(result['metadata_verified_count'], 1)
        self.assertEqual(result['records'][0]['discovery_queries'], ['agent reliability','multiagent failures'])
        self.assertEqual(len(calls), 3)
        self.assertEqual(result['full_text_checked'], 0)
        self.assertFalse(result['scientifically_approved'])

    def test_network_failure_is_not_claimed_as_zero_results(self):
        result = discover(['agent reliability'], fetcher=lambda _: (_ for _ in ()).throw(DiscoveryError('HTTP_429')))
        self.assertEqual(result['record_count'], 0)
        self.assertEqual(len(result['errors']), 1)
        self.assertFalse(result['scientifically_approved'])

    def test_query_caps(self):
        with self.assertRaises(ValueError):
            discover(['agent reliability'], per_query=100)
        with self.assertRaises(ValueError):
            discover(['hi'])
