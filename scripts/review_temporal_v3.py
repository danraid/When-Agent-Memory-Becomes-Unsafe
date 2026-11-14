#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from temporal_v3.review import review

def main():
 p=argparse.ArgumentParser()
 for name in ('empirical','out','ledger'): p.add_argument('--'+name,required=True,type=Path)
 a=p.parse_args()
 read=lambda p: json.loads(p.read_text())
 x=review(empirical=a.empirical,output=a.out,ledger=a.ledger,
    protocol=read(ROOT/'protocol/TEMPORAL_V3.json'),
    model_config=read(ROOT/'study/model_config.json'),
    reviewer_config=read(ROOT/'study/reviewer_config.json'))
 print(json.dumps({'classification':x['classification'],'reviewers':len(x['reviewers']),'scientifically_approved':False}))
if __name__=='__main__':main()
