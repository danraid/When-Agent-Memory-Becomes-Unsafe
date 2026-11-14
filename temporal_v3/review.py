"""Blind, paired low-cost LLM reviews; no reference labels and no peer-review claim."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from article_hub.evidence import write_json
from article_hub.report import create_manifest
from article_hub.llm import request_advisory
from .methods import PAID_ARMS
from .runner import verify, STATUS_LIVE


def sample_blind(observations: list[dict], *, seed: str = 'TEMPORAL-V3-REVIEW-V1') -> list[dict]:
    by = {arm: {x['case_id']: x for x in observations if x['arm'] == arm}
          for arm in PAID_ARMS}
    shared = set.intersection(*(set(g) for g in by.values()))
    first = by[PAID_ARMS[0]]
    pre = [k for k in shared if first[k]['compaction_depth'] < 2]
    post = [k for k in shared if first[k]['compaction_depth'] >= 2
            and first[k]['probe_kind'] in ('stale_rule_revocation', 'new_rule_enforcement')]
    def choose(keys, n):
        return sorted(keys, key=lambda x: hashlib.sha256(f'{seed}|{x}'.encode()).hexdigest())[:n]
    selected = choose(pre, 2) + choose(post, 4)
    if len(selected) != 6:
        raise ValueError('BLIND_REVIEW_INSUFFICIENT_STRATIFIED_CASES')
    sample = []
    for k in selected:
        for arm in PAID_ARMS:
            row = by[arm][k]
            sample.append({'case_id': k, 'arm': arm, 'depth': row['compaction_depth'],
                           'prompt_excerpt': row['prompt'][-1200:],
                           'raw_response': row['raw_response'],
                           'provider_response_id': row['provider_response_id']})
    return sample


def review(*, empirical, output, protocol, model_config, reviewer_config, ledger):
    valid = verify(empirical, protocol, model_config)
    if valid['status'] != STATUS_LIVE:
        raise ValueError('REVIEWS_REQUIRE_REAL_PROVIDER_DATA')
    observations = json.loads((Path(empirical)/'observations.json').read_text())
    sample = sample_blind(observations)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('REVIEW_OUTPUT_MUST_BE_EMPTY')
    output.mkdir(parents=True, exist_ok=True)
    sample_json = json.dumps(sample, ensure_ascii=False, sort_keys=True)
    forbidden_fields = {'reference_policy', 'reference_action', 'evaluation', 'stale_rule_wrongful_reject'}
    if any(forbidden_fields.intersection(row) for row in sample):
        raise ValueError('REFERENCE_LEAKED_IN_REVIEW_SAMPLE')
    for forbidden in ('reference_policy', 'reference_action', 'stale_rule_wrongful_reject'):
        if forbidden in sample_json:
            raise ValueError('GOLD_LABEL_TEXT_LEAKED_IN_REVIEW_SAMPLE')
    reviewers = []
    for kind, instr in (
        ('contract', 'Find syntax errors, ambiguous model actions or inexact prompt requirements. Assess text only, do not infer hidden correct decisions.'),
        ('methods', 'Identify failure modes, temporal update ambiguity, prompt and token-budget confounders, Knowledge Triage adapted-baseline limitations, and sampling non-independence. Do not assert originality.'),
    ):
        prompt = ('You are an advisory reviewer, NOT a peer reviewer. All pairs share case ID; '
                  'samples are stratified, SHA256-permuted and deterministic. Hidden gold labels '
                  'and evaluator outputs are intentionally excluded. ' + instr
                  + '\nMODEL RESPONSES AND PROMPT EXCERPTS:\n' + sample_json)
        response = request_advisory(prompt, reviewer_config, ledger)
        if response.get('model') != 'gpt-6-luna' or not str(response.get('provider_response_id','')).startswith('resp_'):
            raise ValueError('LOW_COST_REVIEWER_PROVIDER_NOT_OBSERVED')
        reviewers.append({'kind': kind, 'model': response['model'],
                          'provider_response_id': response['provider_response_id'],
                          'review_text': response['advisory_text'],
                          'observed_usage': response['observed_usage'],
                          'classification': 'ADVISORY_AI_REVIEW_NOT_HUMAN_PEER_REVIEW'})
    observed_ids = {x['provider_response_id'] for x in observations if x['provider_response_id']}
    ids = [x['provider_response_id'] for x in reviewers]
    if len(set(ids)) != 2 or any(i in observed_ids for i in ids):
        raise ValueError('REVIEWER_IDS_NOT_INDEPENDENT_CALLS')
    result = {'classification':'LOW_COST_ADVISORY_NOT_INDEPENDENT_PEER_REVIEW',
              'reviewers':reviewers, 'sample_cases':6,
              'sample_rows':len(sample), 'sampling':'SHA256 paired; two pre and four post-depth2 cases',
              'gold_labels_supplied': False, 'scientifically_approved':False,
              'submission_authorized':False}
    p = output/'reviewers.json'
    write_json(p, result)
    write_json(output/'manifest.json', create_manifest([p],root=output,classification=result['classification']))
    return result
