#!/usr/bin/env python3
"""V3 pilot-only CLI. There is intentionally no confirmatory subcommand."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from temporal_v3.runner import run, verify


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd',required=True)
    r = sub.add_parser('run')
    r.add_argument('--split',choices=['development','pilot'],default='development')
    r.add_argument('--mode',choices=['mock','live'],default='mock')
    r.add_argument('--execute',action='store_true')
    r.add_argument('--episodes',type=int,default=4)
    r.add_argument('--steps',type=int,default=18)
    r.add_argument('--out',type=Path,required=True)
    r.add_argument('--ledger',type=Path,default=Path('runs/v3/provider-ledger.json'))
    v = sub.add_parser('verify')
    v.add_argument('--directory',type=Path,required=True)
    args = p.parse_args(argv)
    protocol = json.loads((ROOT/'protocol/TEMPORAL_V3.json').read_text())
    config = json.loads((ROOT/'study/model_config.json').read_text())
    if args.cmd == 'verify':
        print(json.dumps(verify(args.directory,protocol,config),indent=2));return 0
    if args.mode == 'live' and not args.execute:
        raise SystemExit('LIVE_REQUIRES_EXPLICIT_EXECUTE')
    report = run(protocol=protocol,config=config,output=args.out,ledger=args.ledger,
                 mode=args.mode,split=args.split,episodes=args.episodes,steps=args.steps)
    print(json.dumps({k:report[k] for k in ('status','episodes','steps','observed_real_provider_calls','observed_compactions')},indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
