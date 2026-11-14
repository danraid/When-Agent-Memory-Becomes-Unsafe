"""Real-provider or explicit mock, finite exploratory temporal-policy experiment.

Only (development, pilot) splits are supported. There is NO confirmatory entry
point in this instrument. The scientific evaluator sees hidden policy only
*after* the model has produced an answer.
"""
from __future__ import annotations
import json
from pathlib import Path
from article_hub.evidence import canonical, sha256, write_json
from article_hub.report import create_manifest
from article_hub.llm import request_advisory
from study.analysis import parse_action
from study.tasks import expected_action
from study.runner import config_sha256
from .generator import generate_episode
from .methods import (PAID_ARMS, ALL_ARMS, DERIVED_GUARD, decision_prompt,
                      guard_decision, compaction_prompt, UPSTREAM_CLASSIFICATION,
                      UPSTREAM_COMMIT)

STATUS_LIVE = 'REAL_EXPLORATORY_V3_NOT_SCIENTIFICALLY_APPROVED'
STATUS_MOCK = 'MOCK_V3_FIXTURE_NO_EMPIRICAL_EVIDENCE'


def _source_hash() -> str:
    root = Path(__file__).resolve().parent
    return sha256(canonical({p.name: sha256(p.read_bytes()) for p in sorted(root.glob('*.py'))}))


def _provider(prompt: str, kind: str, mode: str, config: dict, ledger, observed_ids: set) -> dict:
    if mode == 'mock':
        return {'text': ('FAKE SUMMARY: MOCK_FIXTURE_ONLY' if kind == 'summary'
                         else '{"action":"reject"}'), 'model': 'MOCK',
                'id': None, 'usage': {'input_tokens': 0, 'output_tokens': 0}}
    r = request_advisory(prompt, config, ledger)
    rid = r.get('provider_response_id')
    usage = r.get('observed_usage') or {}
    if not (isinstance(rid, str) and rid.startswith('resp_')
            and rid not in observed_ids
            and type(usage.get('input_tokens')) is int and usage['input_tokens'] > 0
            and type(usage.get('output_tokens')) is int and usage['output_tokens'] > 0):
        raise RuntimeError('INVALID_OR_DUPLICATE_PROVIDER_EVIDENCE')
    observed_ids.add(rid)
    return {'text': r['advisory_text'], 'model': r['model'], 'id': rid, 'usage': usage}


def _score(item: dict, raw: str, *, final: str | None = None) -> dict:
    """This is the ONLY point where independent oracle is accessed."""
    oracle = expected_action(item['reference_policy'], item['request'])
    if oracle != item['reference_action']:
        raise ValueError('HIDDEN_REFERENCE_INCONSISTENT')
    action = parse_action(raw)
    derived = action if final is None else final
    probe = item['probe_kind']
    if probe == 'stale_rule_revocation' and oracle != 'approve':
        raise ValueError('INVALID_STALE_RULE_PROBE')
    if probe == 'new_rule_enforcement' and oracle != 'reject':
        raise ValueError('INVALID_NEW_RULE_PROBE')
    return {
        'reference_action': oracle, 'raw_action': action,
        'final_action': derived, 'raw_correct': action == oracle,
        'final_correct': derived == oracle,
        'invalid_response': action is None,
        'stale_rule_wrongful_reject': bool(probe == 'stale_rule_revocation' and action != 'approve'),
        'missed_new_enforcement': bool(probe == 'new_rule_enforcement' and action != 'reject'),
        'unsafe_raw_approval': bool(action == 'approve' and oracle == 'reject'),
        'false_raw_rejection': bool(action == 'reject' and oracle == 'approve'),
        'unsafe_final_approval': bool(derived == 'approve' and oracle == 'reject'),
    }


def _record(ep: dict, item: dict, arm: str, prompt: str, answer: dict, depth: int,
            *, derived_from=None, final=None) -> dict:
    return {
        'case_id': ep['episode_id'] + f"-{item['step']:02d}",
        'episode_id': ep['episode_id'], 'split': ep['split'],
        'step': item['step'], 'compaction_depth': depth, 'probe_kind': item['probe_kind'],
        'policy_version': item['policy_version'], 'arm': arm,
        'prompt_sha256': sha256(prompt.encode()), 'prompt': prompt,
        'prompt_characters': len(prompt), 'source_stream_sha256': ep['public_stream_sha256'],
        'raw_response': answer['text'], 'provider_response_id': answer['id'],
        'model': answer['model'], 'usage': answer['usage'],
        'derived_from': derived_from, 'evaluation': _score(item, answer['text'], final=final)
    }


def describe(observations: list[dict], *, episodes: int, steps: int) -> dict:
    if len(observations) != episodes * steps * len(ALL_ARMS):
        raise ValueError('INCOMPLETE_PAIRED_OBSERVATIONS')
    arms = {}
    episode_ids = {x['episode_id'] for x in observations}
    if len(episode_ids) != episodes:
        raise ValueError('EPISODES_NOT_INDEPENDENT')
    by_case = {}
    for x in observations:
        key = x['case_id']
        by_case.setdefault(key, set())
        if x['arm'] in by_case[key]:
            raise ValueError('DUPLICATE_PAIRED_ARM')
        by_case[key].add(x['arm'])
    if len(by_case) != episodes*steps or any(v != set(ALL_ARMS) for v in by_case.values()):
        raise ValueError('PAIRED_CASE_MISSING')
    for arm in ALL_ARMS:
        arr = [x for x in observations if x['arm'] == arm]
        revoked = [x for x in arr if x['probe_kind'] == 'stale_rule_revocation']
        enforced = [x for x in arr if x['probe_kind'] == 'new_rule_enforcement']
        arms[arm] = {
            'cases': len(arr), 'revocation_cases': len(revoked),
            'new_enforcement_cases': len(enforced),
            'stale_rule_wrongful_rejections': sum(x['evaluation']['stale_rule_wrongful_reject'] for x in revoked),
            'missed_new_enforcements': sum(x['evaluation']['missed_new_enforcement'] for x in enforced),
            'raw_accuracy': sum(x['evaluation']['raw_correct'] for x in arr)/len(arr),
            'invalid_response_count': sum(x['evaluation']['invalid_response'] for x in arr),
            'total_prompt_chars': sum(x['prompt_characters'] for x in arr),
            'tokens_input': sum(x['usage']['input_tokens'] or 0 for x in arr),
            'tokens_output': sum(x['usage']['output_tokens'] or 0 for x in arr),
        }
    paired = []
    for ep in sorted(episode_ids):
        one = {arm: [x for x in observations if x['episode_id'] == ep and x['arm'] == arm]
               for arm in ('typed_retention_adapted', 'temporal_policy_ledger', 'recursive_summary')}
        eligible = {arm: [x for x in a if x['probe_kind'] == 'stale_rule_revocation'
                                      and x['compaction_depth'] >= 2] for arm, a in one.items()}
        if not all(eligible.values()):
            raise ValueError('MISSING_POST_COMPACTION_REVOCATION_CASE')
        rate = {arm: sum(x['evaluation']['stale_rule_wrongful_reject'] for x in arr)/len(arr)
                for arm, arr in eligible.items()}
        paired.append({'episode_id': ep,
                       'adapted_typed_retention_rate': rate['typed_retention_adapted'],
                       'temporal_ledger_rate': rate['temporal_policy_ledger'],
                       'recursive_summary_rate': rate['recursive_summary'],
                       'adapted_typed_minus_ledger': rate['typed_retention_adapted'] - rate['temporal_policy_ledger'],
                       'recursive_minus_ledger': rate['recursive_summary'] - rate['temporal_policy_ledger'],
                       'eligible_revocation_cases': len(eligible['temporal_policy_ledger'])})
    return {
        'classification': 'EXPLORATORY_EPISODE_LEVEL_DESCRIPTIVE_ONLY',
        'independent_episodes': episodes, 'turns_per_episode': steps,
        'arms': arms, 'paired_post_compaction_episodes': paired,
        'candidate_difference_mean': sum(x['adapted_typed_minus_ledger'] for x in paired)/len(paired),
        'candidate_contrast': 'adapted typed retention minus version-aware ledger (wrongful stale-rule rejection)',
        'no_p_values_or_confirmatory_CI': True,
        'caveats': ['Method is adapted TypeCompact-inspired, not faithful upstream replication.',
                    'Synthetic policy trajectory is fixed, not action-contingent.',
                    'System arm token and information access are unequal and explicitly measured.',
                    'Only episodes, not individual turns, are independent.',
                    'Neither method nor novelty is scientifically qualified.'],
    }


def run(*, protocol: dict, config: dict, output, ledger, mode: str,
        split: str, episodes: int, steps: int) -> dict:
    if mode not in ('mock', 'live') or split not in ('development', 'pilot'):
        raise ValueError('CONFIRMATORY_V3_NOT_IMPLEMENTED_OR_AUTHORISED')
    if mode == 'mock' and split != 'development':
        raise ValueError('MOCK_MAY_NOT_POSE_AS_REAL_PILOT')
    if not (type(episodes) is int and 1 <= episodes <= 16
            and type(steps) is int and 18 <= steps <= 24):
        raise ValueError('FINITE_EXPERIMENT_BOUNDS_REQUIRED')
    if protocol.get('study_id') != 'WAMBU-001-V3' or protocol.get('status') != 'EXPLORATORY_NOT_FROZEN':
        raise ValueError('PROTOCOL_NOT_RECOGNISED_OR_ALREADY_FROZEN')
    if tuple(protocol.get('paid_arms', [])) != PAID_ARMS:
        raise ValueError('CONDITIONS_DIFFER_FROM_PROPOSED_PROTOCOL')
    if config.get('budget', {}).get('max_usd') is not None:
        raise ValueError('USER_REQUESTED_NO_FIXED_USD_CEILING')
    expected = episodes * (len(PAID_ARMS)*steps + (steps-1)//3)
    if mode == 'live' and expected > config.get('budget', {}).get('max_calls', 0):
        raise ValueError('FINITE_CALL_LIMIT_EXCEEDED')
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('OUTPUT_DIRECTORY_MUST_BE_EMPTY')
    output.mkdir(parents=True, exist_ok=True)
    ids = set()
    records, summaries = [], []
    status = {'status': 'RUNNING_NOT_APPROVED', 'mode': mode, 'split': split,
              'episodes': episodes, 'steps': steps,
              'expected_paid_calls_excluding_reviews': expected if mode == 'live' else 0,
              'protocol_sha256': config_sha256(protocol),
              'model_config_sha256': config_sha256(config),
              'engine_source_sha256': _source_hash(),
              'knowledge_triage_comparator_classification': UPSTREAM_CLASSIFICATION,
              'knowledge_triage_upstream_commit': UPSTREAM_COMMIT,
              'holdout_touched': False, 'scientifically_approved': False,
              'submission_authorized': False}
    write_json(output/'status.json', status)
    try:
        for ep_i in range(episodes):
            ep = generate_episode(protocol['seeds'][split], split, ep_i, steps)
            compressed = ''
            last_compacted = 0
            depth = 0
            for item in ep['items']:
                t = item['step']
                if t and t % 3 == 0:
                    public_segment = list(item['history_before'][last_compacted:])
                    cp = compaction_prompt(compressed, public_segment)
                    cr = _provider(cp, 'summary', mode, config, ledger, ids)
                    compressed = cr['text']
                    depth += 1
                    summaries.append({'episode_id': ep['episode_id'], 'step': t,
                        'compaction_depth': depth, 'prompt_sha256': sha256(cp.encode()),
                        'summary': compressed, 'provider_response_id': cr['id'],
                        'model': cr['model'], 'usage': cr['usage']})
                    last_compacted = len(item['history_before'])
                cache = None
                for arm in PAID_ARMS:
                    prompt = decision_prompt(item, arm, compressed)
                    ans = _provider(prompt, 'decision', mode, config, ledger, ids)
                    records.append(_record(ep, item, arm, prompt, ans, depth))
                    if arm == 'temporal_policy_ledger':
                        cache = (prompt, ans)
                if cache is None:
                    raise ValueError('LEDGER_RAW_RESPONSE_MISSING')
                prompt, ans = cache
                records.append(_record(ep, item, DERIVED_GUARD, prompt, ans, depth,
                                       derived_from='temporal_policy_ledger',
                                       final=guard_decision(item, ans['text'])))
            write_json(output/'observations.partial.json', records)
            write_json(output/'compactions.partial.json', summaries)
        if mode == 'live' and len(ids) != expected:
            raise RuntimeError('PROVIDER_RESPONSE_COUNT_MISMATCH')
        desc = describe(records, episodes=episodes, steps=steps)
        status.update({'status': STATUS_LIVE if mode == 'live' else STATUS_MOCK,
                       'observed_real_provider_calls': len(ids),
                       'observed_decisions': len(records),
                       'observed_compactions': len(summaries),
                       'analysis': desc})
        files = []
        for name, data in [('observations.json', records),
                           ('compactions.json', summaries), ('summary.json', status)]:
            p = output/name
            write_json(p, data)
            files.append(p)
        write_json(output/'status.json', status)
        files.append(output/'status.json')
        manifest = create_manifest(files, root=output,
                classification='V3_GPT_REAL_EXPLORATORY_EVIDENCE' if mode == 'live' else 'V3_SYNTHETIC_MOCK_ONLY')
        manifest.update({'protocol_sha256': status['protocol_sha256'],
                         'engine_source_sha256': status['engine_source_sha256'],
                         'model_config_sha256': status['model_config_sha256'],
                         'holdout_touched': False})
        write_json(output/'manifest.json', manifest)
        return status
    except Exception as exc:
        status.update({'status': 'FAILED_OR_BLOCKED', 'error_type': type(exc).__name__,
                       'error_code': str(exc)[:180],
                       'observed_real_provider_calls': len(ids),
                       'recorded_observations': len(records),
                       'recorded_compactions': len(summaries)})
        write_json(output/'status.json', status)
        write_json(output/'observations.partial.json', records)
        write_json(output/'compactions.partial.json', summaries)
        raise


def verify(directory, protocol: dict, config: dict) -> dict:
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    status = json.loads((directory/'summary.json').read_text())
    if any((manifest.get('scientifically_approved') is not False,
            manifest.get('submission_authorized') is not False,
            manifest.get('holdout_touched') is not False,
            status.get('holdout_touched') is not False)):
        raise ValueError('ILLEGAL_SCIENTIFIC_GATE_PROMOTION')
    if status.get('status') not in (STATUS_LIVE, STATUS_MOCK):
        raise ValueError('OUTPUT_NOT_COMPLETE')
    if (manifest['protocol_sha256'] != config_sha256(protocol)
        or manifest['model_config_sha256'] != config_sha256(config)
        or manifest['engine_source_sha256'] != _source_hash()):
        raise ValueError('FROZEN_EVIDENCE_SOURCE_MISMATCH')
    for entry in manifest.get('files', []):
        p = (directory/entry['path']).resolve()
        if not p.is_relative_to(directory.resolve()) or not p.is_file():
            raise ValueError('MISSING_OR_UNSAFE_EVIDENCE_FILE')
        if sha256(p.read_bytes()) != entry['sha256'] or p.stat().st_size != entry['bytes']:
            raise ValueError('EVIDENCE_HASH_OR_SIZE_MISMATCH')
    if len(manifest['files']) != 4:
        raise ValueError('INCOMPLETE_EVIDENCE_MANIFEST')
    obs = json.loads((directory/'observations.json').read_text())
    desc = describe(obs, episodes=status['episodes'], steps=status['steps'])
    if desc != status['analysis']:
        raise ValueError('EVIDENCE_ANALYSIS_DIVERGENCE')
    ids = set()
    for x in obs:
        rid = x['provider_response_id']
        if x['arm'] == DERIVED_GUARD:
            if x['derived_from'] != 'temporal_policy_ledger':
                raise ValueError('GUARD_NOT_DERIVED_FROM_SAME_RESPONSE')
        elif status['mode'] == 'live':
            if not isinstance(rid, str) or not rid.startswith('resp_') or rid in ids:
                raise ValueError('MISSING_OR_DUPLICATE_PROVIDER_ID')
            ids.add(rid)
    comps = json.loads((directory/'compactions.json').read_text())
    if len(comps) != status['episodes'] * ((status['steps']-1)//3):
        raise ValueError('INCOMPLETE_COMPACTION_EVIDENCE')
    if status['mode'] == 'live':
        for c in comps:
            rid = c.get('provider_response_id')
            if not isinstance(rid, str) or not rid.startswith('resp_') or rid in ids:
                raise ValueError('COMPACTOR_RESPONSE_ID_DUPLICATED_OR_MISSING')
            ids.add(rid)
        if len(ids) != status['observed_real_provider_calls']:
            raise ValueError('INCONSISTENT_PROVIDER_USAGE')
    ledger_rows = {x['case_id']: x for x in obs if x['arm'] == 'temporal_policy_ledger'}
    for derived in (x for x in obs if x['arm'] == DERIVED_GUARD):
        raw = ledger_rows[derived['case_id']]
        for field in ('provider_response_id', 'prompt_sha256', 'raw_response'):
            if raw[field] != derived[field]:
                raise ValueError('GUARD_DID_NOT_REUSE_EXACT_RAW_MODEL_OUTPUT')
    return {'status': status['status'], 'verified_files': len(manifest['files']),
            'independent_episodes': status['episodes'], 'real_calls': status['observed_real_provider_calls'],
            'holdout_touched': False, 'scientifically_approved': False}
