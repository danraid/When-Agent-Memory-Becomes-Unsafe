"""Claim-level source binding: bibliographic identity != full-text verification.

A claim is citable only with Crossref raw identity snapshot, bound excerpt bytes,
locator and a *recorded* human full-text review. A JSON assertion alone does not
cryptographically establish that the named reviewer is a human.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import re
from .discovery import normalize_doi, title_matches
from .evidence import canonical, sha256


class CitationError(ValueError):
    pass


def _key(doi):
    return 'doi_' + re.sub(r'[^a-z0-9]+', '_', doi.lower()).strip('_')


def _bib_escape(value):
    value = str(value or '').replace('\\', r'\textbackslash{}')
    return value.replace('&', r'\&').replace('%', r'\%').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}')


def validate_catalogue(catalogue):
    if catalogue.get('classification') != 'BIBLIOGRAPHIC_METADATA_ONLY':
        raise CitationError('SYNTHETIC_OR_UNVERIFIED_CATALOGUE_REJECTED')
    records = catalogue.get('records', [])
    snapshots = catalogue.get('crossref_snapshots') or {}
    if not isinstance(records, list) or not isinstance(snapshots, dict):
        raise CitationError('Invalid bibliography catalogue')
    accepted = {}
    for record in records:
        if record.get('status') != 'METADATA_VERIFIED' or record.get('metadata_check') != 'CROSSREF_IDENTITY_MATCH':
            continue
        if record.get('is_retracted_flag') or (record.get('source') or {}).get('provider') != 'OpenAlex':
            continue
        doi = normalize_doi(record.get('doi'))
        snap = snapshots.get(doi)
        if not doi or not isinstance(snap, dict):
            continue
        if normalize_doi(snap.get('DOI')) != doi:
            continue
        crossref_title = snap.get('title', [])
        crossref_title = crossref_title[0] if isinstance(crossref_title, list) and crossref_title else crossref_title
        if not title_matches(record.get('title'), crossref_title):
            continue
        if record.get('crossref_source_sha256') != sha256(canonical(snap)):
            continue
        if doi in accepted:
            raise CitationError('Duplicate verified DOI: ' + doi)
        accepted[doi] = record
    return accepted


def verify_claims(catalogue, claims, *, source_root):
    approved_metadata = validate_catalogue(catalogue)
    source_root = Path(source_root).resolve()
    if claims.get('schema_version') != 1 or not isinstance(claims.get('claims'), list):
        raise CitationError('Invalid claim dossier')
    valid = []
    used = set()
    for claim in claims['claims']:
        cid = claim.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{1,50}', cid) or cid in used:
            raise CitationError('Invalid or repeated claim ID')
        used.add(cid)
        doi = normalize_doi(claim.get('doi'))
        if doi not in approved_metadata:
            raise CitationError('Claim lacks verified primary bibliographic identity: ' + cid)
        text = claim.get('claim_text')
        if not isinstance(text, str) or len(text.strip()) < 12 or len(text) > 1200:
            raise CitationError('Claim text missing or excessive: ' + cid)
        excerpt_path = claim.get('excerpt_path')
        if not isinstance(excerpt_path, str) or not excerpt_path.startswith('evidence/excerpts/'):
            raise CitationError('Source excerpt must be in evidence/excerpts/: ' + cid)
        path = (source_root/excerpt_path).resolve()
        if not path.is_relative_to(source_root) or not path.is_file():
            raise CitationError('Excerpt missing or outside source root: ' + cid)
        excerpt = path.read_text(encoding='utf-8').strip()
        if not excerpt or len(excerpt.split()) > 25 or len(excerpt.encode('utf-8')) > 400:
            raise CitationError('Excerpt must be bounded to 25 source words: ' + cid)
        if sha256(path.read_bytes()) != claim.get('excerpt_sha256'):
            raise CitationError('Excerpt content hash mismatch: ' + cid)
        location = claim.get('locator') or {}
        if not isinstance(location, dict) or not any(isinstance(location.get(k), str) and location.get(k).strip() for k in ('page', 'section')):
            raise CitationError('Page or section locator required: ' + cid)
        human = claim.get('human_review') or {}
        if (human.get('decision') != 'VERIFIED' or human.get('method') != 'MANUAL_FULLTEXT_REVIEW'
            or not isinstance(human.get('reviewer'), str) or len(human['reviewer'].strip()) < 3):
            raise CitationError('Recorded human full-text review required: ' + cid)
        try:
            datetime.fromisoformat(str(human.get('reviewed_at_utc', '')).replace('Z', '+00:00'))
        except ValueError:
            raise CitationError('Review date missing or invalid: ' + cid) from None
        valid.append({
            'id': cid, 'doi': doi, 'key': _key(doi), 'claim_text': text.strip(),
            'excerpt_path': excerpt_path, 'excerpt_sha256': claim['excerpt_sha256'],
            'locator': location, 'reviewer_record': human['reviewer'],
            'source_identity_sha256': approved_metadata[doi]['crossref_source_sha256'],
        })
    return valid, approved_metadata


def render_bibtex(records, claims):
    used = sorted({c['doi'] for c in claims})
    entries = []
    for doi in used:
        r = records[doi]
        author = ' and '.join(_bib_escape(x) for x in r.get('authors') or [])
        fields = [('title', _bib_escape(r['title'])), ('doi', doi), ('url', 'https://doi.org/' + doi)]
        if author:
            fields.append(('author', author))
        if type(r.get('publication_year')) is int:
            fields.append(('year', str(r['publication_year'])))
        if isinstance(r.get('venue'), str) and r['venue']:
            fields.append(('journal', _bib_escape(r['venue'])))
        kind = 'article' if any(f[0]=='journal' for f in fields) else 'misc'
        entries.append('@' + kind + '{' + _key(doi) + ',\n' + '\n'.join('  ' + k + ' = {' + v + '},' for k,v in fields) + '\n}')
    return '\n\n'.join(entries) + ('\n' if entries else '')
