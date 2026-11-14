#!/usr/bin/env python3
"""Two non-independent low-cost model reviews of a real article pilot."""
from pathlib import Path
import json
import sys
import argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from study.review import review

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True)
    args=p.parse_args()
    config=json.loads((ROOT/'study/reviewer_config.json').read_text())
    result=review(data_dir=args.data_dir,output=args.out,config=config,ledger=args.ledger)
    print(json.dumps({'classification':result['classification'],
        'provider_reviews':len(result['reviewers']),'scientific_approval':False},indent=2))
if __name__=='__main__':
    main()
