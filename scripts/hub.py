#!/usr/bin/env python3
"""Agentic Research Hub CLI: no network or paid API usage by default."""
from __future__ import annotations
from dataclasses import asdict
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from article_hub import VERSION
from article_hub.discovery import discover, fixture_discovery
from article_hub.evidence import smoke, write_json, sha256
from article_hub.generator import init_paper
from article_hub.llm import request_advisory
from article_hub.empirical import run_benchmark, frozen_hash, judge_source_sha256, engine_source_sha256, paper_config_sha256
from article_hub.report import run_demo
from article_hub.state import plan
from article_hub.editorial import build_editorial


def default_path(path, template):
    return ROOT / (path if (ROOT / path).exists() else template)


def parse_file(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_manifest(directory):
    directory = Path(directory).resolve()
    manifest = parse_file(directory / 'manifest.json')
    if manifest.get('scientifically_approved') is not False or manifest.get('submission_authorized') is not False:
        raise ValueError('A generic hub cannot approve publication')
    count = 0
    for item in manifest.get('files', []):
        path = (directory/item['path']).resolve()
        if not path.is_relative_to(directory) or not path.is_file():
            raise ValueError('Unsafe or missing manifest file')
        if sha256(path.read_bytes()) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Evidence hash or size mismatch: '+item['path'])
        count += 1
    for name, expected in manifest.get('engine_sources', {}).items():
        source = (ROOT/name).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file() or sha256(source.read_bytes()) != expected:
            raise ValueError('Evidence engine source mismatch: ' + name)
    if count == 0:
        raise ValueError('Empty evidence manifest')
    return {'verified_files': count, 'scientific_approval': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=f'Agentic Research Hub {VERSION}, safe by default')
    cmds = parser.add_subparsers(dest='command', required=True)
    p = cmds.add_parser('plan', help='Conservative research DAG; never promotes stages')
    p.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))
    p.add_argument('--state', type=Path, default=default_path('research_state.json','templates/article/research_state.json'))

    s = cmds.add_parser('smoke', help='Deterministic non-scientific smoke fixture')
    s.add_argument('--seed', type=int, default=2026)
    s.add_argument('--n', type=int, default=64)
    s.add_argument('--output', type=Path)

    i = cmds.add_parser('init', help='Generate local paper only, never GitHub remote')
    i.add_argument('--slug', required=True)
    i.add_argument('--title', required=True)
    i.add_argument('--out', type=Path, required=True)

    d = cmds.add_parser('demo', help='Run reproducible synthetic methods demonstration')
    d.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))
    d.add_argument('--seed', type=int, default=2026)
    d.add_argument('--n', type=int, default=400)
    d.add_argument('--output', type=Path, default=ROOT/'runs/demo')

    disc = cmds.add_parser('discover', help='Explicit live OpenAlex/Crossref or synthetic offline fixture')
    choice = disc.add_mutually_exclusive_group(required=True)
    choice.add_argument('--live', action='store_true', help='Use the internet; never use paid GPT')
    choice.add_argument('--fixture', type=Path, help='Use only explicitly mock works (test mode)')
    disc.add_argument('--query-config', type=Path, default=default_path('research_queries.json','templates/article/research_queries.json'))
    disc.add_argument('--output', type=Path, required=True)

    review = cmds.add_parser('advisory', help='Optional GPT advisory, no independent review')
    review.add_argument('--execute', action='store_true', help='Required explicit network and budget opt-in')
    review.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))
    review.add_argument('--prompt-file', type=Path, required=True)
    review.add_argument('--ledger', type=Path, default=ROOT/'runs/openai-ledger.json')
    review.add_argument('--output', type=Path, required=True)

    empirical = cmds.add_parser('empirical', help='Bounded synthetic-task benchmark with mock or opt-in real GPT')
    empirical.add_argument('--split', choices=['development','pilot','confirmatory'], default='development')
    empirical.add_argument('--mode', choices=['mock','live'], default='mock')
    empirical.add_argument('--execute', action='store_true', help='Required for paid live GPT calls')
    empirical.add_argument('--episodes', type=int, default=2)
    empirical.add_argument('--steps', type=int, default=7)
    empirical.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))
    empirical.add_argument('--protocol', type=Path, default=default_path('experiment_protocol.json','templates/article/experiment_protocol.json'))
    empirical.add_argument('--lock', type=Path)
    empirical.add_argument('--approval', type=Path)
    empirical.add_argument('--ledger', type=Path, default=ROOT/'runs/openai-ledger.json')
    empirical.add_argument('--output', type=Path, required=True)

    freeze = cmds.add_parser('freeze-proposal', help='Calculate hashes for author review; never approves a protocol')
    freeze.add_argument('--protocol', type=Path, default=default_path('experiment_protocol.json','templates/article/experiment_protocol.json'))
    freeze.add_argument('--output', type=Path, required=True)
    freeze.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))

    editorial = cmds.add_parser('editorial', help='Produce citation-checked journal-neutral manuscript draft')
    editorial.add_argument('--config', type=Path, default=default_path('paper.json','templates/article/paper.json'))
    editorial.add_argument('--author', type=Path, default=default_path('editorial/author.json','templates/article/editorial/author.json'))
    editorial.add_argument('--content', type=Path, default=default_path('editorial/content.json','templates/article/editorial/content.json'))
    editorial.add_argument('--catalogue', type=Path, default=default_path('editorial/catalogue.json','templates/article/editorial/catalogue.json'))
    editorial.add_argument('--claims', type=Path, default=default_path('editorial/claims.json','templates/article/editorial/claims.json'))
    editorial.add_argument('--journal', type=Path, default=default_path('editorial/journal_profile.json','templates/article/editorial/journal_profile.json'))
    editorial.add_argument('--results', type=Path, help='Optional verified empirical result directory')
    editorial.add_argument('--pdf', action='store_true', help='Optional draft PDF proof, not a journal-certified PDF')
    editorial.add_argument('--output', type=Path, required=True)

    verify = cmds.add_parser('verify', help='Verify immutable SHA256 evidence manifest')
    verify.add_argument('--directory', type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == 'init':
        print(init_paper(ROOT, args.out, args.slug, args.title))
    elif args.command == 'smoke':
        result = smoke(args.seed, args.n)
        if args.output:
            write_json(args.output, result)
        print(json.dumps(result, indent=2))
    elif args.command == 'plan':
        paper = parse_file(args.config)
        if paper.get('hub_schema_version') != 1:
            raise ValueError('Unsupported paper schema')
        state = parse_file(args.state)
        print(json.dumps({'paper': paper.get('slug'), 'hub_version': VERSION,
            'scientific_completion': False, 'decisions': [asdict(x) for x in plan(state)]}, indent=2))
    elif args.command == 'demo':
        paper = parse_file(args.config)
        if paper.get('hub_schema_version') != 1:
            raise ValueError('Unsupported schema')
        result = run_demo(paper=paper, output=args.output, seed=args.seed, n=args.n)
        result['manifest_verification'] = verify_manifest(args.output)
        print(json.dumps(result, indent=2))
    elif args.command == 'discover':
        if args.fixture:
            fixture = parse_file(args.fixture)
            if fixture.get('classification') != 'SYNTHETIC_TEST_FIXTURE':
                raise ValueError('Offline fixtures must have explicit synthetic classification')
            result = fixture_discovery(fixture['results'])
        else:
            opts = parse_file(args.query_config)
            if opts.get('schema_version') != 1:
                raise ValueError('Invalid discovery config')
            result = discover(opts['queries'], per_query=opts.get('per_query', 5),
                crossref_limit=opts.get('crossref_limit', 10),
                api_key=os.environ.get('OPENALEX_API_KEY'),
                mailto=os.environ.get('CROSSREF_CONTACT_EMAIL'))
        write_json(args.output, result)
        if args.live and result['record_count'] == 0 and result.get('errors'):
            raise RuntimeError('ALL_LIVE_DISCOVERY_QUERIES_FAILED; see saved error manifest')
        print(json.dumps({'output': str(args.output), 'classification': result['classification'],
                          'records': result['record_count'], 'scientifically_approved': False,
                          'errors': len(result.get('errors', []))}, indent=2))
    elif args.command == 'advisory':
        if not args.execute:
            raise ValueError('advisory requires explicit --execute; paid calls are off by default')
        config = parse_file(args.config)['api']
        prompt = args.prompt_file.read_text(encoding='utf-8')
        result = request_advisory(prompt, config, args.ledger)
        write_json(args.output, result)
        print(json.dumps({'output': str(args.output), 'classification': result['classification'],
                          'scientific_approval': False, 'observed_usage': result['observed_usage']}, indent=2))
    elif args.command == 'empirical':
        if args.mode == 'live' and not args.execute:
            raise ValueError('Real GPT calls require explicit --execute')
        protocol=parse_file(args.protocol)
        result=run_benchmark(paper=parse_file(args.config), protocol=protocol, output=args.output,
            split=args.split, mode=args.mode, episodes=args.episodes, steps=args.steps,
            lock=parse_file(args.lock) if args.lock else None,
            approval=parse_file(args.approval) if args.approval else None,
            holdout_secret=os.environ.get('HUB_HOLDOUT_SEED') if args.split == 'confirmatory' else None,
            ledger=args.ledger)
        result['manifest_verification'] = verify_manifest(args.output)
        print(json.dumps(result, indent=2))
    elif args.command == 'freeze-proposal':
        protocol=parse_file(args.protocol)
        if protocol.get('schema_version') != 1:
            raise ValueError('Unsupported protocol version')
        proposal={'status': 'PENDING_AUTHOR_DECISION_NOT_A_FREEZE',
            'protocol_sha256': frozen_hash(protocol), 'evaluator_sha256': judge_source_sha256(),
            'engine_sha256': engine_source_sha256(),
            'paper_config_sha256': paper_config_sha256(parse_file(args.config)),
            'instructions': 'Author must separately review and record a FROZEN_BY_AUTHOR lock and approval; never auto-promote.'}
        write_json(args.output, proposal)
        print(json.dumps(proposal, indent=2))
    elif args.command == 'editorial':
        status=build_editorial(paper=parse_file(args.config),author=parse_file(args.author),
            content=parse_file(args.content),catalogue=parse_file(args.catalogue),
            claims=parse_file(args.claims),source_root=ROOT,output=args.output,
            results_directory=args.results,profile=parse_file(args.journal),pdf=args.pdf)
        status['manifest_verification']=verify_manifest(args.output)
        print(json.dumps(status,indent=2))
    elif args.command == 'verify':
        print(json.dumps(verify_manifest(args.directory), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
