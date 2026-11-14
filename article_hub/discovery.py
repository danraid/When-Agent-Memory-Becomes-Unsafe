"""Bounded scholarly metadata discovery. Metadata is never scientific approval.

Live mode uses OpenAlex and optionally Crossref. All network calls are explicit and
keep API secrets outside logs and saved evidence. Fixtures have separate status.
"""
from __future__ import annotations

from difflib import SequenceMatcher
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .evidence import canonical, sha256

DOI_PATTERN = re.compile(r'^10\.\d{4,9}/\S+$', re.I)


class DiscoveryError(RuntimeError):
    """A remote request or bibliographic record could not be validated."""


def normalize_doi(value):
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    for prefix in ('https://doi.org/', 'http://doi.org/', 'https://dx.doi.org/', 'doi:'):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    value = value.rstrip('.,; ')
    return value if DOI_PATTERN.fullmatch(value) else None


def clean_title(text):
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text.casefold())).strip()


def title_matches(left, right, threshold=0.86):
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    a, b = clean_title(left), clean_title(right)
    return bool(a and b) and SequenceMatcher(None, a, b).ratio() >= threshold


def fetch_json(url, *, headers=None, timeout=15, retries=2, transport=None, sleeper=time.sleep):
    """Small HTTP adapter, injectable for network-free reproducibility tests."""
    if not url.startswith('https://'):
        raise ValueError('HTTPS is required for scholarly services')
    transport = transport or _urlopen
    head = {'User-Agent': 'AgenticResearchHub/0.4 (academic metadata client)', 'Accept': 'application/json'}
    head.update(headers or {})
    for attempt in range(retries + 1):
        try:
            doc = transport(url, head, timeout)
            if not isinstance(doc, dict):
                raise DiscoveryError('Non-object JSON response')
            return doc
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                raise DiscoveryError(f'HTTP_{exc.code}') from None
            try:
                wait = min(8.0, max(0.0, float(exc.headers.get('Retry-After', 0))))
            except (ValueError, TypeError):
                wait = 0
            sleeper(max(wait, min(2 ** attempt, 4)))
        except (URLError, TimeoutError, OSError) as exc:
            if attempt == retries:
                raise DiscoveryError('NETWORK_UNAVAILABLE') from None
            sleeper(min(2 ** attempt, 4))
    raise AssertionError('unreachable')


def _urlopen(url, headers, timeout):
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def openalex_work(work, *, fixture=False):
    if not isinstance(work, dict):
        raise ValueError('OpenAlex work must be an object')
    title = work.get('display_name') or work.get('title')
    work_id = work.get('id')
    if not title or not isinstance(title, str) or not isinstance(work_id, str):
        raise ValueError('OpenAlex work missing title or identifier')
    doi = normalize_doi(work.get('doi'))
    author_list = work.get('authorships') or []
    authors = [(a.get('author') or {}).get('display_name') for a in author_list if isinstance(a, dict) and isinstance(a.get('author') or {}, dict)]
    authors = [a for a in authors if isinstance(a, str)][:20]
    location = work.get('primary_location') or {}
    source = location.get('source') or {}
    year = work.get('publication_year')
    if type(year) is not int or not 1800 <= year <= 2200:
        year = None
    record = {
        'identifier': doi or work_id,
        'doi': doi,
        'openalex_id': work_id,
        'title': title.strip(),
        'publication_year': year,
        'authors': authors,
        'venue': source.get('display_name'),
        'work_type': work.get('type'),
        'is_retracted_flag': bool(work.get('is_retracted')),
        'status': 'SYNTHETIC_TEST_FIXTURE' if fixture else 'CANDIDATE',
        'metadata_check': 'NOT_ATTEMPTED',
        'full_text_verified': False,
        'scientifically_approved': False,
        'license_verified': False,
        'source_record_sha256': sha256(canonical(work)),
        'source': {'provider': 'FIXTURE' if fixture else 'OpenAlex', 'url': work_id},
    }
    return record


def verify_crossref(record, item):
    """Verify only identity, NOT method, results, access rights or validity."""
    expected = record.get('doi')
    title_data = item.get('title') or []
    title = title_data[0] if isinstance(title_data, list) and title_data else title_data
    actual = normalize_doi(item.get('DOI'))
    if not expected or actual != expected:
        record['metadata_check'] = 'DOI_MISMATCH'
        return record
    if not title_matches(record['title'], title):
        record['metadata_check'] = 'TITLE_MISMATCH'
        return record
    record['metadata_check'] = 'CROSSREF_IDENTITY_MATCH'
    if record['status'] != 'SYNTHETIC_TEST_FIXTURE' and not record['is_retracted_flag']:
        record['status'] = 'METADATA_VERIFIED'
    record['crossref_source_sha256'] = sha256(canonical(item))
    return record


def discover(queries, *, per_query=8, crossref_limit=15, fetcher=fetch_json, api_key=None, mailto=None):
    """Query a bounded first OpenAlex page per term and optional DOI identity checks."""
    if not isinstance(queries, list) or not 1 <= len(queries) <= 8 or any(not isinstance(q, str) or len(q.strip()) < 3 for q in queries):
        raise ValueError('Provide 1..8 nonempty research queries')
    if type(per_query) is not int or not 1 <= per_query <= 25:
        raise ValueError('per_query must be between 1 and 25')
    if type(crossref_limit) is not int or not 0 <= crossref_limit <= 25:
        raise ValueError('crossref_limit must be between 0 and 25')
    results = {}
    errors = []
    for query in queries:
        params = {'search': query, 'per-page': per_query, 'page': 1}
        if api_key:
            params['api_key'] = api_key
        url = 'https://api.openalex.org/works?' + urlencode(params)
        try:
            payload = fetcher(url)
        except DiscoveryError as exc:
            errors.append({'query': query, 'provider': 'OpenAlex', 'code': str(exc)})
            continue
        for item in payload.get('results', [])[:per_query]:
            try:
                record = openalex_work(item)
            except ValueError:
                errors.append({'query': query, 'provider': 'OpenAlex', 'code': 'INVALID_RECORD'})
                continue
            key = record['identifier']
            if key not in results:
                record['discovery_queries'] = []
                results[key] = record
            if query not in results[key]['discovery_queries']:
                results[key]['discovery_queries'].append(query)
    checked = 0
    crossref_snapshots = {}
    for record in sorted(results.values(), key=lambda r: r['identifier']):
        if checked >= crossref_limit:
            break
        doi = record.get('doi')
        if not doi or record['is_retracted_flag']:
            continue
        checked += 1
        params = ('?'+urlencode({'mailto': mailto}) if mailto else '')
        url = 'https://api.crossref.org/works/' + quote(doi, safe='/') + params
        try:
            item = fetcher(url).get('message')
            if not isinstance(item, dict):
                raise DiscoveryError('CROSSREF_INVALID_RESPONSE')
            verify_crossref(record, item)
            if record.get('status') == 'METADATA_VERIFIED':
                crossref_snapshots[doi] = item
        except DiscoveryError as exc:
            record['metadata_check'] = 'CROSSREF_UNAVAILABLE'
            errors.append({'identifier': record['identifier'], 'provider': 'Crossref', 'code': str(exc)})
    ordered = sorted(results.values(), key=lambda r: (r['identifier'], r['title']))
    return {
        'classification': 'BIBLIOGRAPHIC_METADATA_ONLY',
        'scientifically_approved': False,
        'full_text_checked': 0,
        'queries': list(queries),
        'per_query_limit': per_query,
        'crossref_checked_count': checked,
        'records': ordered,
        'errors': errors,
        'record_count': len(ordered),
        'metadata_verified_count': sum(r['status'] == 'METADATA_VERIFIED' for r in ordered),
        'crossref_snapshots': crossref_snapshots,
        'record_set_sha256': sha256(canonical(ordered)),
    }


def fixture_discovery(works):
    """Only for testing the parsing pipeline; never a scientific reference."""
    records = [openalex_work(work, fixture=True) for work in works]
    return {
        'classification': 'SYNTHETIC_BIBLIOGRAPHIC_FIXTURE',
        'scientifically_approved': False,
        'full_text_checked': 0,
        'records': records,
        'record_count': len(records),
        'record_set_sha256': sha256(canonical(records)),
    }
