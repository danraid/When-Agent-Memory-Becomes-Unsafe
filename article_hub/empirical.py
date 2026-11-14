"""Finite, evidence-bound agent benchmark: mock smoke or real opt-in GPT calls."""
from __future__ import annotations
import json
from pathlib import Path
from .benchmark import CONDITIONS, generate_episode, make_prompt
from .evidence import canonical, sha256, write_json
from .judge import adjudicate, summarize
from .llm import request_advisory
from .report import create_manifest
from . import VERSION


class ExperimentGateError(RuntimeError):
    pass


def frozen_hash(protocol):
    return sha256(canonical(protocol))


def engine_source_sha256():
    names = ('benchmark.py', 'judge.py', 'empirical.py', 'statistics.py', 'llm.py')
    return sha256(canonical({n: sha256(Path(__file__).with_name(n).read_bytes()) for n in names}))


def paper_config_sha256(paper):
    return sha256(canonical(paper))


def validate_execution_gate(*, split, mode, protocol, paper=None, episodes=None, steps=None,
                            lock=None, approval=None, holdout_secret=None):
    if split not in {'development', 'pilot', 'confirmatory'}:
        raise ExperimentGateError('INVALID_SPLIT')
    if mode not in {'mock', 'live'}:
        raise ExperimentGateError('INVALID_MODE')
    if split == 'confirmatory':
        if mode != 'live':
            raise ExperimentGateError('CONFIRMATORY_REQUIRES_REAL_EMPIRICAL_RUN')
        if not lock or lock.get('protocol_sha256') != frozen_hash(protocol) or lock.get('status') != 'FROZEN_BY_AUTHOR':
            raise ExperimentGateError('FROZEN_PROTOCOL_REQUIRED')
        if not approval or approval.get('approved') is not True or not str(approval.get('author', '')).strip() or approval.get('protocol_sha256') != frozen_hash(protocol):
            raise ExperimentGateError('RECORDED_HUMAN_APPROVAL_REQUIRED')
        if not isinstance(holdout_secret, str) or len(holdout_secret) < 32:
            raise ExperimentGateError('PRIVATE_HOLDOUT_SEED_REQUIRED')
        if holdout_secret in (protocol.get('seeds') or {}).values():
            raise ExperimentGateError('HOLDOUT_MUST_NOT_REUSE_DEVELOPMENT_SEED')
        if lock.get('evaluator_sha256') != judge_source_sha256():
            raise ExperimentGateError('FROZEN_EVALUATOR_MISMATCH')
        if lock.get('engine_sha256') != engine_source_sha256():
            raise ExperimentGateError('FROZEN_ENGINE_MISMATCH')
        if paper is None or lock.get('paper_config_sha256') != paper_config_sha256(paper):
            raise ExperimentGateError('FROZEN_MODEL_CONFIG_MISMATCH')
        design = protocol.get('confirmatory_design') or {}
        if (type(episodes) is not int or type(steps) is not int or
            episodes != design.get('episodes') or steps != design.get('steps')):
            raise ExperimentGateError('CONFIRMATORY_SAMPLE_SIZE_NOT_PREREGISTERED')
    return True


def judge_source_sha256():
    return sha256(Path(__file__).with_name('judge.py').read_bytes())


def mock_agent(prompt):
    # This is intentionally a weak, declared test stub. It does not read labels.
    return {'text': '{"action":"approve"}', 'model': 'MOCK_ALWAYS_APPROVE_NOT_GPT',
            'usage': {'input_tokens': 0, 'output_tokens': 0}}


def run_benchmark(*, paper, protocol, output, split='development', mode='mock',
                  episodes=2, steps=7, holdout_secret=None, lock=None, approval=None,
                  ledger=None, model_call=None):
    validate_execution_gate(split=split, mode=mode, protocol=protocol, paper=paper,
                            episodes=episodes, steps=steps, lock=lock,
                            approval=approval, holdout_secret=holdout_secret)
    if type(episodes) is not int or not 1 <= episodes <= 100 or type(steps) is not int or not 4 <= steps <= 24:
        raise ValueError('Hard upper bounds exceeded')
    if mode == 'live' and model_call is not None:
        raise ExperimentGateError('LIVE_CANNOT_USE_INJECTED_TEST_MODEL')
    if mode == 'mock' and split != 'development':
        raise ExperimentGateError('MOCK_ALLOWED_ONLY_FOR_DEVELOPMENT_TECHNICAL_TESTS')
    seeds = protocol.get('seeds') or {}
    seed_secret = holdout_secret if split == 'confirmatory' else seeds.get(split)
    if not isinstance(seed_secret, str) or not seed_secret:
        raise ExperimentGateError('MISSING_SPLIT_SEED')
    if paper.get('hub_schema_version') != 1:
        raise ExperimentGateError('UNKNOWN_PAPER_SCHEMA')
    if protocol.get('schema_version') != 1 or protocol.get('task_family') != 'synthetic_access_policy_memory_v1':
        raise ExperimentGateError('UNKNOWN_EXPERIMENT_PROTOCOL')
    planned_calls = episodes * steps * len(CONDITIONS)
    limits = paper.get('api', {}).get('budget', {})
    if mode == 'live':
        if not paper.get('api', {}).get('enabled'):
            raise ExperimentGateError('LIVE_GPT_DISABLED')
        if planned_calls > limits.get('max_calls', 0):
            raise ExperimentGateError('PLANNED_CALLS_EXCEED_BUDGET')
        if ledger is None:
            raise ExperimentGateError('PERSISTENT_JOB_LEDGER_REQUIRED')
    if model_call is None:
        if mode == 'mock':
            model_call = mock_agent
        else:
            def model_call(prompt):
                result = request_advisory(prompt, paper['api'], ledger)
                return {'text': result['advisory_text'], 'model': result['model'],
                        'usage': result['observed_usage'],
                        'provider_response_id': result.get('provider_response_id'),
                        'reservation_usd': result['conservative_reserved_usd']}
    records = []
    output = Path(output)
    if output.exists():
        if any(output.iterdir()):
            raise ExperimentGateError('OUTPUT_DIRECTORY_MUST_BE_NEW_OR_EMPTY')
    else:
        output.mkdir(parents=True)
    for idx in range(episodes):
        episode = generate_episode(seed_secret, split, idx, steps)
        for step_idx, event in enumerate(episode['events']):
            for condition in CONDITIONS:
                prompt = make_prompt(episode, step_idx, condition)
                observed = model_call(prompt)
                if not isinstance(observed, dict) or not isinstance(observed.get('text'), str):
                    raise ExperimentGateError('INVALID_MODEL_RESPONSE')
                evaluation = adjudicate(episode['policy'], event, observed['text'],
                                        guard=(condition == 'structured_memory_with_guard'))
                records.append({
                    'case_id': episode['episode_id'] + f'-{step_idx:02d}',
                    'condition': condition, 'episode_content_sha256': episode['content_sha256'],
                    'prompt_sha256': sha256(prompt.encode('utf-8')),
                    'input_prompt': prompt, 'raw_response': observed['text'],
                    'model': observed.get('model', 'UNKNOWN'),
                    'usage': observed.get('usage', {}), 'provider_response_id': observed.get('provider_response_id'),
                    'evaluation': evaluation,
                })
    summary = summarize(records)
    classification = ('EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED' if mode == 'live'
                      else 'SYNTHETIC_TEST_FIXTURE_NOT_EMPIRICAL')
    result = {'classification': classification, 'split': split, 'mode': mode,
              'research_approval': False, 'publication_authorized': False,
              'protocol_sha256': frozen_hash(protocol),
              'evaluator_sha256': judge_source_sha256(),
              'holdout_seed_sha256': sha256(holdout_secret.encode('utf-8')) if split == 'confirmatory' else None,
              'episodes': episodes, 'steps_per_episode': steps, 'observations': len(records),
              'planned_calls': planned_calls, 'summary': summary,
              'independent_evaluation': 'DETERMINISTIC_RULE_JUDGE_NOT_PEER_REVIEW',
              'limits': 'Synthetic access-policy domain only; no claims of general agent reliability.'}
    data_path = output/'observations.json'
    summary_path = output/'summary.json'
    write_json(data_path, records)
    write_json(summary_path, result)
    manifest = create_manifest([data_path, summary_path], root=output, classification=classification)
    manifest['protocol_sha256'] = frozen_hash(protocol)
    manifest['evaluator_sha256'] = judge_source_sha256()
    manifest['engine_sources'] = {
        f'article_hub/{name}': sha256(Path(__file__).with_name(name).read_bytes())
        for name in ('benchmark.py', 'judge.py', 'empirical.py', 'statistics.py', 'llm.py')
    }
    write_json(output/'manifest.json', manifest)
    return {'output_directory': str(output), 'classification': classification, 'observations': len(records),
            'summary': result['summary'], 'hub_version': VERSION,
            'scientific_approval': False, 'publication_authorized': False}
