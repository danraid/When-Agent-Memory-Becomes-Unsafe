#!/usr/bin/env python3
"""One finite, real-provider hub engineering homologation; no USD spend ceiling."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from article_hub.benchmark import CONDITIONS
from article_hub.empirical import run_benchmark
from article_hub.homologation import live_config, blind_review, publish_homologation
from article_hub.evidence import write_json
from scripts.hub import verify_manifest


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT/'runs'/'homologation')
    p.add_argument('--episodes', type=int, default=2)
    p.add_argument('--steps', type=int, default=5)
    p.add_argument('--agent-model', default='gpt-6.1-terra')
    args=p.parse_args(argv)
    if not 1 <= args.episodes <= 10 or not 4 <= args.steps <= 24:
        raise ValueError('Finite instrument homologation requires 1..10 episodes and 4..24 steps')
    if args.output.exists() and any(args.output.iterdir()):
        raise RuntimeError('HOMOLOGATION_OUTPUT_MUST_BE_NEW')
    args.output.mkdir(parents=True,exist_ok=True)
    preflight={'classification':'HUB_ENGINEERING_PREFLIGHT', 'usd_ceiling_enforced':False,
               'scientifically_approved':False,'submission_authorized':False,
               'episodes':args.episodes,'steps':args.steps, 'agent_model':args.agent_model,
               'reviewer_model':'gpt-6-luna', 'planned_model_calls':args.episodes*args.steps*len(CONDITIONS)+2}
    key=os.environ.get('OPENAI_API_KEY')
    if not key:
        preflight['status']='BLOCKED_OPENAI_API_KEY_NOT_CONFIGURED'
        write_json(args.output/'preflight.json',preflight)
        raise RuntimeError(preflight['status'])
    preflight['status']='READY_FOR_FINITE_REAL_PROVIDER_TEST'
    write_json(args.output/'preflight.json',preflight)
    paper_path=ROOT/'paper.json' if (ROOT/'paper.json').exists() else ROOT/'templates/article/paper.json'
    protocol_path=ROOT/'experiment_protocol.json' if (ROOT/'experiment_protocol.json').exists() else ROOT/'templates/article/experiment_protocol.json'
    paper=json.loads(paper_path.read_text())
    protocol=json.loads(protocol_path.read_text())
    planned=args.episodes*args.steps*len(CONDITIONS)
    config=live_config(paper,agent_model=args.agent_model,max_calls=planned+2)
    write_json(args.output/'live_config.json',config)
    ledger=args.output/'ledger.json'
    experiment_dir=args.output/'empirical'
    run_benchmark(paper=config,protocol=protocol,output=experiment_dir,
                  split='development',mode='live',episodes=args.episodes,steps=args.steps,ledger=ledger)
    verify_manifest(experiment_dir)
    rows=json.loads((experiment_dir/'observations.json').read_text())
    reviews=blind_review(rows,config['api'],ledger)
    review_file=args.output/'reviewers.json'
    write_json(review_file,reviews)
    status=publish_homologation(args.output/'validation',source=ROOT/'scripts/homologate.py',
                                 reviewer=review_file,config=config,empirical_dir=experiment_dir,
                                 expected_cases=planned//len(CONDITIONS))
    assert status['status']=='ENGINEERING_HOMOLOGATED'
    # Parent manifest must list actual real-provider evidence and review records.
    print(json.dumps({'status': status['status'], 'actual_agent_calls':len(rows),
                      'actual_reviewer_calls':len(reviews['reports']),
                      'usd_ceiling_enforced':False, 'scientifically_approved':False},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
