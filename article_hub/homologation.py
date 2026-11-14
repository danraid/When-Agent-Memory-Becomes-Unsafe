"""Engineering-only real-GPT homologation with blinded, low-cost advisory reviews.

Runs are finite and use no USD spending ceiling. Financial usage is recorded,
not limited. The reviewer cannot see the reference policy labels or approve
scientific conclusions; objective evaluation remains detached and deterministic.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path

from .benchmark import CONDITIONS
from .evidence import sha256, canonical, write_json
from .empirical import run_benchmark
from .llm import request_advisory
from .report import create_manifest
from . import VERSION


class HomologationError(RuntimeError):
    pass


def live_config(paper, *, agent_model='gpt-6.1-terra', max_calls=70):
    if not isinstance(max_calls, int) or max_calls < 1 or max_calls > 12000:
        raise ValueError('Experiment must have a finite number of API requests')
    config = copy.deepcopy(paper)
    config['slug'] = 'hub-engineering-validation'
    config['title'] = 'Hub engineering validation, not a research article'
    api = config['api']
    api.update({'enabled': True, 'model': agent_model,
                'max_output_tokens': 512,
                'pricing': {'input_usd_per_million': '1.00',
                            'output_usd_per_million': '5.00',
                            'note': 'Informational standard token price for gpt-6.1-terra; not a billing statement'},
                'budget': {'max_calls': max_calls,
                           'max_input_tokens': max_calls * 25000,
                           'max_output_tokens': max_calls * 1024,
                           'max_usd': None}})
    return config


def _reviews_input(rows, max_items=10):
    # Select a fixed, deterministic sample across *all* conditions.
    # Never include gold reference labels, policy objects, or judged outcomes.
    selected = []
    for condition in CONDITIONS:
        pool = sorted((r for r in rows if r['condition'] == condition), key=lambda r: r['case_id'])
        selected.extend(pool[:min(2, len(pool))])
    result = []
    for r in selected[:max_items]:
        result.append({'case_id': r['case_id'], 'condition': r['condition'],
                       'prompt_excerpt': r['input_prompt'][-3500:],
                       'raw_response': r['raw_response']})
    return result


def blind_review(rows, api, ledger, *, request_fn=request_advisory):
    examples = _reviews_input(rows)
    if not examples or len(set(row['condition'] for row in examples)) != len(CONDITIONS):
        raise HomologationError('REVIEW_SAMPLE_MISSING_CONDITIONS')
    reviewer = copy.deepcopy(api)
    reviewer['model'] = 'gpt-6-luna'
    reviewer['pricing'] = {'input_usd_per_million': '0.10',
                           'output_usd_per_million': '0.50',
                           'note': 'Informational standard price; no USD ceiling'}
    reviewer['max_output_tokens'] = 800
    tasks = [
        ('format', 'Independently assess whether each raw agent response follows the required JSON contract. Identify concrete format failures, if any.'),
        ('context', 'Independently assess limitations of evidence for these memory-policy decisions and list possible confounders. Do not guess hidden policy labels.'),
    ]
    # The two reviews are advisory, not independent peer review or evidence of
    # correctness. Responses are never used to amend reference labels.
    reports = []
    for focus, instruction in tasks:
        prompt = ('You are a low-cost, blind methodological reviewer. '
                  'No reference answers or hidden future inputs are supplied. '
                  'Do not declare scientific approval. ' + instruction +
                  '\nExamples (synthetic task, but real model responses):\n' +
                  json.dumps(examples, ensure_ascii=False, sort_keys=True) +
                  '\nReturn a concise list of issues and evidence limitations.')
        response = request_fn(prompt, reviewer, ledger)
        if response.get('classification') != 'AI_ADVISORY_NOT_INDEPENDENT_REVIEW':
            raise HomologationError('REVIEWER_NOT_ADVISORY')
        if response.get('model') != 'gpt-6-luna' or not str(response.get('provider_response_id') or '').strip():
            raise HomologationError('REVIEWER_PROVENANCE_MISSING')
        reports.append({'focus': focus, 'model': response['model'],
                        'review_text': response['advisory_text'],
                        'provider_response_id': response['provider_response_id'],
                        'usage': response['observed_usage'],
                        'prompt_sha256': response['prompt_sha256'],
                        'scientific_approval': False})
    return {'classification': 'BLIND_LLM_ADVISORY_NOT_PEER_REVIEW', 'reports': reports,
            'sample_count': len(examples), 'sample_selection': 'two lexically first cases for each condition',
            'gold_labels_supplied_to_reviewers': False,
            'scientific_approval': False}


def qualify_evidence(observations, summary, reviews, *, expected_cases):
    """Determine engineering readiness from observed API records, never prose claims."""
    if summary.get('classification') != 'EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED' or summary.get('mode') != 'live':
        return False, 'NO_REAL_GPT_EXECUTION'
    if summary.get('split') != 'development' or len(observations) != expected_cases * len(CONDITIONS):
        return False, 'UNEXPECTED_OBSERVATION_COUNT_OR_SPLIT'
    by_condition = {name: set() for name in CONDITIONS}
    response_ids = set()
    for row in observations:
        condition = row.get('condition')
        if condition not in by_condition:
            return False, 'UNKNOWN_CONDITION'
        if row.get('case_id') in by_condition[condition]:
            return False, 'DUPLICATE_CASE'
        by_condition[condition].add(row.get('case_id'))
        usage = row.get('usage') or {}
        provider_id = row.get('provider_response_id')
        if not isinstance(provider_id, str) or not provider_id.startswith('resp_') or provider_id in response_ids:
            return False, 'MISSING_DUPLICATE_OR_INVALID_PROVIDER_RESPONSE_IDS'
        response_ids.add(provider_id)
        if not str(row.get('provider_response_id') or '').strip() or \
            not isinstance(usage.get('input_tokens'), int) or usage['input_tokens'] <= 0 or \
            not isinstance(usage.get('output_tokens'), int) or usage['output_tokens'] <= 0 or \
            str(row.get('model', '')).startswith('MOCK'):
            return False, 'MISSING_REAL_PROVIDER_PROVENANCE'
    if len({frozenset(ids) for ids in by_condition.values()}) != 1 or \
        any(len(cases) != expected_cases for cases in by_condition.values()):
        return False, 'MISSING_PAIRED_CASES'
    if reviews.get('classification') != 'BLIND_LLM_ADVISORY_NOT_PEER_REVIEW' or \
        reviews.get('gold_labels_supplied_to_reviewers') is not False or \
        len(reviews.get('reports', [])) != 2:
        return False, 'BLIND_REVIEW_MISSING'
    review_ids = set()
    for review in reviews['reports']:
        if not isinstance(review.get('provider_response_id'), str) or not review['provider_response_id'].startswith('resp_') or \
            review['provider_response_id'] in response_ids or review['provider_response_id'] in review_ids:
            return False, 'REVIEWER_RESPONSE_ID_INVALID_OR_REUSED'
        review_ids.add(review['provider_response_id'])
        if review.get('model') != 'gpt-6-luna' or not review.get('provider_response_id') or \
            not review.get('review_text') or review.get('scientific_approval') is not False:
            return False, 'REVIEW_METADATA_INVALID'
    return True, 'OBSERVED_REAL_GPT_PAIRED_AND_BLINDLY_REVIEWED'


def publish_homologation(output, *, source, reviewer, config, empirical_dir, expected_cases):
    """Create an evidence manifest and machine-checkable non-scientific status."""
    output = Path(output)
    observations = json.loads((Path(empirical_dir)/'observations.json').read_text())
    summary = json.loads((Path(empirical_dir)/'summary.json').read_text())
    reviews = json.loads(Path(reviewer).read_text())
    valid, reason = qualify_evidence(observations, summary, reviews, expected_cases=expected_cases)
    if not valid:
        raise HomologationError('ENGINEERING_HOMOLOGATION_REJECTED: ' + reason)
    out = {'status': 'ENGINEERING_HOMOLOGATED',
           'scope': 'GENERIC_HUB_REAL_GPT_INSTRUMENT_ONLY',
           'hub_version': VERSION,
           'run_source_sha256': sha256(Path(source).read_bytes()),
           'config_sha256': sha256(canonical(config)),
           'observed_real_gpt_decisions': len(observations),
           'observed_gpt_reviewer_calls': len(reviews['reports']),
           'paired_cases_per_condition': expected_cases,
           'review_models': sorted({r['model'] for r in reviews['reports']}),
           'usd_ceiling_enforced': False,
           'finite_calls_and_retry_bounds_enforced': True,
           'confirmatory_holdout_accessed': False,
           'scientifically_approved': False,
           'submission_authorized': False,
           'author_approval_forged': False,
           'reason': reason}
    output.mkdir(parents=True, exist_ok=True)
    status = output/'homologation.json'
    write_json(status, out)
    manifest = create_manifest([status, Path(reviewer), Path(empirical_dir)/'summary.json',
                                Path(empirical_dir)/'observations.json',
                                Path(empirical_dir)/'manifest.json'], root=output.parent,
                               classification='REAL_GPT_HUB_ENGINEERING_EVIDENCE')
    write_json(output.parent/'manifest.json', manifest)
    return out
