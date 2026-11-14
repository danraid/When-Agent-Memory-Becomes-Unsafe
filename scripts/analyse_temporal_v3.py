#!/usr/bin/env python3
"""Comprehensive pilot evidence report. Deliberately no confirmatory statistics."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from temporal_v3.runner import verify, STATUS_LIVE
from article_hub.evidence import write_json

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--empirical',required=True,type=Path)
 p.add_argument('--advisory',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args()
 config=json.loads((ROOT/'study/model_config.json').read_text())
 protocol=json.loads((ROOT/'protocol/TEMPORAL_V3.json').read_text())
 observed=verify(a.empirical,protocol,config)
 if observed['status']!=STATUS_LIVE:raise SystemExit('REAL_V3_PILOT_REQUIRED')
 s=json.loads((a.empirical/'summary.json').read_text())
 r=json.loads((a.advisory/'reviewers.json').read_text())
 if len(r['reviewers'])!=2 or r['gold_labels_supplied'] is not False:raise SystemExit('BLIND_REVIEW_NOT_VERIFIED')
 if s.get('holdout_touched') or s.get('scientifically_approved'):raise SystemExit('CONFIRMATORY_BOUNDARY_VIOLATION')
 a.out.mkdir(parents=True,exist_ok=True)
 report={'status':'V3_EXPLORATORY_FEASIBILITY_ONLY',
         'scientifically_approved':False,'submission_authorized':False,
         'pilot':s['analysis'],'provider_calls_decision_and_compaction':s['observed_real_provider_calls'],
         'reviewer_calls':len(r['reviewers']),
         'reviewer_concerns':[{'kind':x['kind'],'text':x['review_text']} for x in r['reviewers']],
         'novelty_block':'CITATIONS_CIKM_2026_AND_SUPERSEDE_2026_REQUIRE_HUMAN_METHOD_REVIEW',
         'confirmatory_data_touched':False}
 write_json(a.out/'report.json',report)
 lines=['# WAMBU-001 v3 | Temporal policy supersession live pilot','',
        '**EXPLORATORY ONLY. This is not confirmatory evidence or journal approval.**','',
        f"Independent episodes: {s['episodes']}; paid model calls (excluding two reviewers): {s['observed_real_provider_calls']}",'',
        '| Method | Cases | Stale-rule wrongful rejection / revocation probes | Missed new enforcement / probes | Raw accuracy |',
        '| --- | ---: | ---: | ---: | ---: |']
 for k,v in s['analysis']['arms'].items():
    lines.append(f"| {k} | {v['cases']} | {v['stale_rule_wrongful_rejections']}/{v['revocation_cases']} | {v['missed_new_enforcements']}/{v['new_enforcement_cases']} | {v['raw_accuracy']:.3f} |")
 lines.extend(['',f"Exploratory episode-mean contrast (adapted typed retention minus temporal ledger): {s['analysis']['candidate_difference_mean']:.4f}.",
 'No confirmatory p-value or CI is calculated. The comparator is **adapted typed retention**, not a published algorithm reproduction.',
 'Existing CIKM 2026 and Supersede 2026 prior art require a novelty/method review. The result may be null.',
 'Private confirmatory holdout was NOT accessed. Manuscript submission NOT authorized.'])
 (a.out/'report.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'status':report['status'],'episodes':s['episodes'],
  'decision_calls':s['observed_real_provider_calls']-s['observed_compactions'],
  'compaction_calls':s['observed_compactions'],
  'contrast':s['analysis']['candidate_difference_mean']},indent=2))
if __name__=='__main__':main()
