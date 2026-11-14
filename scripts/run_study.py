#!/usr/bin/env python3
"""Article-specific CLI. Offline smoke by default; GPT explicitly opt-in."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from study.runner import run,verify_output,config_sha256,sources_sha256
from article_hub.evidence import write_json


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main(argv=None):
    p=argparse.ArgumentParser(description='When Agent Memory Becomes Unsafe research instrument')
    sub=p.add_subparsers(dest='cmd',required=True)
    runp=sub.add_parser('run')
    runp.add_argument('--mode',choices=('mock','live'),default='mock')
    runp.add_argument('--split',choices=('development','pilot','confirmatory'),default='development')
    runp.add_argument('--episodes',type=int,default=2)
    runp.add_argument('--steps',type=int,default=12)
    runp.add_argument('--execute',action='store_true',help='Allow real paid API calls')
    runp.add_argument('--out',required=True,type=Path)
    runp.add_argument('--ledger',type=Path,default=ROOT/'runs'/'live-ledger.json')
    runp.add_argument('--lock',type=Path)
    runp.add_argument('--approval',type=Path)
    sub.add_parser('freeze-proposal')
    ver=sub.add_parser('verify')
    ver.add_argument('--directory',type=Path,required=True)
    args=p.parse_args(argv)
    if args.cmd=='verify':
        print(json.dumps(verify_output(args.directory),indent=2))
        return 0
    protocol=load(ROOT/'protocol'/'STUDY_PLAN.json')
    paper=load(ROOT/'paper.json')
    paper['api']=load(ROOT/'study'/'model_config.json')
    if args.cmd=='freeze-proposal':
        result={'status':'PENDING_AUTHOR_REVIEW_NOT_FROZEN',
                'protocol_sha256':config_sha256(protocol),
                'study_sources_sha256':sources_sha256(),
                'paper_config_sha256':config_sha256(paper),
                'scientifically_approved':False}
        write_json(ROOT/'protocol'/'FREEZE_PROPOSAL.json',result)
        print(json.dumps(result,indent=2))
        return 0
    if args.mode=='live' and not args.execute:
        raise SystemExit('LIVE_REQUIRES_EXPLICIT_EXECUTE')
    lock=load(args.lock) if args.lock else None
    approval=load(args.approval) if args.approval else None
    status=run(protocol=protocol,paper=paper,split=args.split,mode=args.mode,
               episodes=args.episodes,steps=args.steps,output=args.out,
               ledger=args.ledger,lock=lock,approval=approval,
               private_seed=os.environ.get('HUB_HOLDOUT_SEED') if args.split=='confirmatory' else None)
    print(json.dumps({'status':status['status'],'observed_decisions':status['observed_decisions'],
                      'observed_compactions':status['observed_compactions'],
                      'scientifically_approved':False},indent=2))
    return 0
if __name__=='__main__':
    raise SystemExit(main())
