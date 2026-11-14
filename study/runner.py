"""Paired, longitudinal GPT compaction study, with evidence and split gates.

No automatic scientific promotion, confirmation or journal submission.
All gold labels remain outside the model and compactor prompt construction.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
from . import VERSION
from .analysis import evaluate, summarize
from .prompts import (ALL_CONDITIONS, PAID_DECISION_CONDITIONS,
                      POSTPROCESS_CONDITION, decision_prompt, compaction_prompt)
from .tasks import generate_episode
from article_hub.evidence import canonical, sha256, write_json
from article_hub.llm import request_advisory
from article_hub.report import create_manifest


class StudyGateError(RuntimeError):
    pass


def sources_sha256() -> str:
    folder = Path(__file__).resolve().parent
    return sha256(canonical({p.name: sha256(p.read_bytes())
                             for p in sorted(folder.glob('*.py'))}))


def config_sha256(value) -> str:
    return sha256(canonical(value))


def guard_split(*, protocol, paper, split, mode, episodes, steps, lock=None,
                approval=None, private_seed=None):
    if split not in {'development', 'pilot', 'confirmatory'} or mode not in {'mock', 'live'}:
        raise StudyGateError('INVALID_MODE_OR_SPLIT')
    if type(episodes) is not int or not 1 <= episodes <= 40 or type(steps) is not int or not 8 <= steps <= 24:
        raise StudyGateError('FINITE_SAMPLE_LIMIT_EXCEEDED')
    if mode == 'mock' and split != 'development':
        raise StudyGateError('MOCK_MAY_NOT_MASQUERADE_AS_REAL_PILOT')
    if protocol.get('study_id') != 'WAMBU-001' or protocol.get('schema_version') != 1:
        raise StudyGateError('INVALID_ARTICLE_PROTOCOL')
    seeds = protocol.get('development_seeds') or {}
    if not seeds.get('development') or not seeds.get('pilot') or seeds['development'] == seeds['pilot']:
        raise StudyGateError('INVALID_SEED_SPLIT')
    if mode == 'live':
        api = paper.get('api') or {}
        if not api.get('enabled') or not isinstance(api.get('model'), str):
            raise StudyGateError('API_NOT_EXPLICITLY_CONFIGURED')
        compactions = episodes * ((steps-1)//3)
        required = episodes * steps * len(PAID_DECISION_CONDITIONS) + compactions
        if required > api.get('budget', {}).get('max_calls', 0):
            raise StudyGateError('PLANNED_CALLS_EXCEED_FINITE_BOUND')
    if split == 'confirmatory':
        if mode != 'live':
            raise StudyGateError('CONFIRMATION_REQUIRES_LIVE_PROVIDER')
        if not isinstance(private_seed, str) or len(private_seed) < 32 or private_seed in seeds.values():
            raise StudyGateError('UNTOUCHED_PRIVATE_HOLDOUT_SEED_REQUIRED')
        if not lock or lock.get('status') != 'FROZEN_BY_AUTHOR' or lock.get('protocol_sha256') != config_sha256(protocol):
            raise StudyGateError('FROZEN_AUTHOR_PROTOCOL_REQUIRED')
        if lock.get('study_sources_sha256') != sources_sha256() or lock.get('paper_config_sha256') != config_sha256(paper):
            raise StudyGateError('FROZEN_CODE_AND_MODEL_MUST_MATCH')
        if not approval or approval.get('approved') is not True or approval.get('protocol_sha256') != config_sha256(protocol) or not str(approval.get('author','')).strip():
            raise StudyGateError('HUMAN_CONFIRMATORY_APPROVAL_REQUIRED')
        design = protocol.get('confirmatory_design') or {}
        if design.get('episodes') != episodes or design.get('steps') != steps:
            raise StudyGateError('SAMPLE_SIZE_NOT_PREREGISTERED')
        if paper.get('research', {}).get('confirmatory_enabled') is not True:
            raise StudyGateError('CONFIRMATORY_DISABLED_BY_PAPER_CONFIG')
    return True


def _mock_provider(prompt: str, kind: str) -> dict:
    return {'text': ('SYNTHETIC TEST ONLY: no real compaction took place' if kind == 'compact'
                     else '{"action":"reject"}'),
            'model': 'MOCK_NO_GPT_CALLS', 'usage': {'input_tokens': 0, 'output_tokens': 0},
            'provider_response_id': None}


def _call(prompt, kind, mode, paper, ledger):
    if mode == 'mock':
        return _mock_provider(prompt, kind)
    response = request_advisory(prompt, paper['api'], ledger)
    usage = response.get('observed_usage') or {}
    rid = response.get('provider_response_id')
    if not isinstance(rid, str) or not rid.startswith('resp_') or not (
        type(usage.get('input_tokens')) is int and usage['input_tokens'] > 0 and
        type(usage.get('output_tokens')) is int and usage['output_tokens'] > 0):
        raise StudyGateError('REAL_PROVIDER_PROVENANCE_INCOMPLETE')
    return {'text': response['advisory_text'], 'model': response['model'],
            'usage': usage, 'provider_response_id': rid}


def _record(item, episode, condition, prompt, answer, summary_depth, derived_from=None):
    # This is the first point where reference labels and observed model output meet.
    judgement = evaluate(item, answer['text'], guarded=condition == POSTPROCESS_CONDITION)
    return {'case_id': episode['episode_id'] + f"-{item['step']:02d}",
            'episode_id': episode['episode_id'], 'episode_public_sha256': episode['public_content_sha256'], 'split': episode['split'],
            'step': item['step'], 'policy_version': item['policy_version'],
            'condition': condition, 'compaction_depth': summary_depth,
            'input_prompt_sha256': sha256(prompt.encode('utf-8')),
            'prompt': prompt, 'raw_response': answer['text'],
            'provider_response_id': answer['provider_response_id'],
            'model': answer['model'], 'usage': answer['usage'],
            'derived_from': derived_from, 'evaluation': judgement}


def run(*, protocol, paper, output, split, mode, episodes, steps,
        ledger=None, lock=None, approval=None, private_seed=None):
    guard_split(protocol=protocol, paper=paper, split=split, mode=mode,
                episodes=episodes, steps=steps, lock=lock, approval=approval,
                private_seed=private_seed)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise StudyGateError('OUTPUT_MUST_BE_NEW_OR_EMPTY')
    output.mkdir(parents=True, exist_ok=True)
    if mode == 'live' and ledger is None:
        raise StudyGateError('SERIAL_API_LEDGER_REQUIRED')
    seed = private_seed if split == 'confirmatory' else protocol['development_seeds'][split]
    obs, compacted, real_ids = [], [], set()
    status = {'classification': 'EXPLORATORY_REAL_GPT_OBSERVATIONS_UNREVIEWED' if mode == 'live'
              else 'SYNTHETIC_TEST_FIXTURE_NOT_EMPIRICAL',
              'status': 'IN_PROGRESS', 'study_id': 'WAMBU-001', 'split': split,
              'mode': mode, 'protocol_sha256': config_sha256(protocol),
              'model_config_sha256': config_sha256(paper),
              'study_sources_sha256': sources_sha256(),
              'private_seed_digest': sha256(private_seed.encode()) if split == 'confirmatory' else None,
              'scientifically_approved': False, 'submission_authorized': False,
              'holdout_touched': split == 'confirmatory',
              'case_count_expected': episodes * steps * len(ALL_CONDITIONS),
              'api_decisions_expected': episodes * steps * len(PAID_DECISION_CONDITIONS),
              'api_compactions_expected': episodes * ((steps - 1)//3)}
    write_json(output/'status.json', status)
    try:
        for ep_index in range(episodes):
            episode = generate_episode(seed, split, ep_index, steps)
            summary = ''
            depth = 0
            consumed = 0
            for item in episode['items']:
                t = item['step']
                history = item['history_before']
                if t and t % 3 == 0:
                    recent_logs = history[consumed:]
                    compact_prompt = compaction_prompt(summary, recent_logs)
                    compact_answer = _call(compact_prompt, 'compact', mode, paper, ledger)
                    rid = compact_answer['provider_response_id']
                    if rid is not None:
                        if rid in real_ids:
                            raise StudyGateError('DUPLICATE_PROVIDER_RESPONSE_ID')
                        real_ids.add(rid)
                    if compact_answer['text'].strip() in ('{"action":"approve"}', '{"action":"reject"}'):
                        raise StudyGateError('COMPACTOR_RETURNED_ACTION_NOT_SUMMARY')
                    summary = compact_answer['text'][:5000]
                    consumed = len(history)
                    depth += 1
                    compacted.append({'episode_id': episode['episode_id'],
                                      'before_step': t, 'depth': depth,
                                      'new_logs_count': len(recent_logs),
                                      'prompt_sha256': sha256(compact_prompt.encode()),
                                      'raw_summary': summary, 'model': compact_answer['model'],
                                      'provider_response_id': rid,
                                      'usage': compact_answer['usage']})
                cached = None
                cached_prompt = None
                for condition in PAID_DECISION_CONDITIONS:
                    prompt = decision_prompt(item, condition, summary)
                    answer = _call(prompt, 'decide', mode, paper, ledger)
                    rid = answer['provider_response_id']
                    if rid is not None:
                        if rid in real_ids:
                            raise StudyGateError('DUPLICATE_PROVIDER_RESPONSE_ID')
                        real_ids.add(rid)
                    obs.append(_record(item, episode, condition, prompt, answer, depth))
                    if condition == 'pinned_ledger':
                        cached = deepcopy(answer)
                        cached_prompt = prompt
                assert cached is not None and cached_prompt is not None
                obs.append(_record(item, episode, POSTPROCESS_CONDITION,
                                   cached_prompt, cached, depth, derived_from='pinned_ledger'))
            write_json(output/'observations.partial.json', obs)
            write_json(output/'compactions.partial.json', compacted)
        expected_real_calls = status['api_decisions_expected'] + status['api_compactions_expected']
        if mode == 'live' and len(real_ids) != expected_real_calls:
            raise StudyGateError('MISSING_REAL_PROVIDER_CALLS')
        analysis = summarize(obs, episodes, steps)
        status['status'] = 'REAL_DEVELOPMENT_OR_PILOT_OBSERVED_NOT_SCIENTIFICALLY_APPROVED' if mode == 'live' else 'MOCK_INSTRUMENT_SMOKE_COMPLETE'
        status['observed_provider_calls'] = len(real_ids)
        status['observed_decisions'] = len(obs)
        status['observed_compactions'] = len(compacted)
        status['analysis'] = analysis
        write_json(output/'observations.json', obs)
        write_json(output/'compactions.json', compacted)
        write_json(output/'summary.json', status)
        write_json(output/'status.json', status)
        paths = [output/'observations.json', output/'compactions.json',
                 output/'summary.json', output/'status.json']
        manifest = create_manifest(paths, root=output,
                    classification=status['classification'])
        manifest['study_id'] = 'WAMBU-001'
        manifest['protocol_sha256'] = status['protocol_sha256']
        manifest['study_sources_sha256'] = status['study_sources_sha256']
        manifest['source_evidence_kind'] = 'EXPLORATORY_NOT_CONFIRMATORY' if split != 'confirmatory' else 'CONFIRMATORY_PENDING_AUTHOR_INTERPRETATION'
        write_json(output/'manifest.json', manifest)
        return status
    except Exception as exc:
        status['status'] = 'FAILED_OR_BLOCKED'
        status['error_type'] = type(exc).__name__
        status['error_code'] = str(exc)[:160]
        status['recorded_cases_before_error'] = len(obs)
        status['recorded_compactions_before_error'] = len(compacted)
        write_json(output/'status.json', status)
        write_json(output/'observations.partial.json', obs)
        write_json(output/'compactions.partial.json', compacted)
        raise


def verify_output(directory) -> dict:
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest.get('scientifically_approved') is not False or manifest.get('submission_authorized') is not False:
        raise StudyGateError('ILLEGAL_SCIENTIFIC_PROMOTION')
    files = manifest.get('files') or []
    if len(files) < 4:
        raise StudyGateError('EVIDENCE_INCOMPLETE')
    for file in files:
        p = (directory/file['path']).resolve()
        if not p.is_relative_to(directory.resolve()) or not p.is_file():
            raise StudyGateError('UNSAFE_PATH_OR_MISSING_EVIDENCE')
        if sha256(p.read_bytes()) != file['sha256'] or p.stat().st_size != file['bytes']:
            raise StudyGateError('EVIDENCE_DIGEST_MISMATCH')
    if manifest.get('study_sources_sha256') != sources_sha256():
        raise StudyGateError('ENGINE_CODE_CHANGED_AFTER_EVIDENCE')
    status = json.loads((directory/'summary.json').read_text())
    root = Path(__file__).resolve().parents[1]
    current_protocol = json.loads((root/'protocol/STUDY_PLAN.json').read_text())
    current_paper = json.loads((root/'paper.json').read_text())
    current_paper['api'] = json.loads((root/'study/model_config.json').read_text())
    if status.get('protocol_sha256') != config_sha256(current_protocol) or status.get('model_config_sha256') != config_sha256(current_paper):
        raise StudyGateError('INPUT_PROTOCOL_OR_MODEL_CONFIG_CHANGED_AFTER_EVIDENCE')
    if status['status'] not in ('MOCK_INSTRUMENT_SMOKE_COMPLETE',
                                 'REAL_DEVELOPMENT_OR_PILOT_OBSERVED_NOT_SCIENTIFICALLY_APPROVED'):
        raise StudyGateError('INCOMPLETE_RUN')
    if status['split'] == 'confirmatory' and status['status'] == 'MOCK_INSTRUMENT_SMOKE_COMPLETE':
        raise StudyGateError('MOCK_CONFIRMATORY_FORBIDDEN')
    return {'verified_files': len(files), 'status': status['status'],
            'scientifically_approved': False, 'submission_authorized': False}
