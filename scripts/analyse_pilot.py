#!/usr/bin/env python3
"""Postflight, descriptive-only v2 pilot QC. Never returns scientific approval."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from study.runner import verify_output, StudyGateError
from study.inference import eligible_episode_differences
from article_hub.evidence import write_json


def report(empirical:Path,advisory:Path,out:Path,*,episodes:int,steps:int):
    check=verify_output(empirical)
    s=json.loads((empirical/'summary.json').read_text())
    obs=json.loads((empirical/'observations.json').read_text())
    reviewers=json.loads((advisory/'reviewers.json').read_text())
    if s['split']!='pilot' or s['mode']!='live' or s['status']!='REAL_DEVELOPMENT_OR_PILOT_OBSERVED_NOT_SCIENTIFICALLY_APPROVED':
        raise StudyGateError('NOT_A_COMPLETE_REAL_INDEPENDENT_PILOT')
    if s['observed_decisions']!=episodes*steps*5 or s['observed_provider_calls']!=episodes*(steps*4+(steps-1)//3):
        raise StudyGateError('PILOT_PROVIDER_COUNTS_DO_NOT_MATCH_DESIGN')
    if len(reviewers.get('reviewers',[]))!=2 or reviewers.get('gold_labels_supplied') is not False:
        raise StudyGateError('BLINDED_REVIEW_INVALID')
    if s.get('holdout_touched') or s.get('scientifically_approved') or s.get('submission_authorized'):
        raise StudyGateError('SCIENTIFIC_BOUNDARY_VIOLATED')
    paired=eligible_episode_differences(obs,min_rejections=4)
    if len(paired)!=episodes:
        raise StudyGateError('MISSING_INDEPENDENT_EPISODES')
    obs_tokens=sum((r['usage']['input_tokens'] or 0)+(r['usage']['output_tokens'] or 0)
                   for r in obs if r['condition']!='pinned_ledger_guard')
    a=s['analysis']['by_condition']
    result={'classification':'DESCRIPTIVE_GPT_PILOT_NOT_CONFIRMATORY',
        'status':'V2_INDEPENDENT_PILOT_QUALIFIED_FOR_DESIGN_REVIEW',
        'split':'pilot','episodes_independent':episodes,'steps_per_episode':steps,
        'genuine_decision_calls':episodes*steps*4,
        'genuine_compaction_calls':episodes*((steps-1)//3),
        'reviewer_calls':len(reviewers['reviewers']),
        'paired_cases_scored':s['observed_decisions'],
        'unit_of_independence':'episode',
        'conditional_unsafe_approvals_by_condition':{k:{
            'unsafe_approvals':v['unsafe_approvals'],
            'unsafe_opportunities':v['unsafe_opportunities'],
            'raw_accuracy':v['raw_accuracy'],
            'false_rejections':v['false_rejections']} for k,v in a.items()},
        'descriptive_candidate_primary_difference':sum(x['difference'] for x in paired)/len(paired),
        'post_two_compaction_episode_risk_differences':paired,
        'total_decision_tokens_nonduplicated':obs_tokens,
        'evidence_files_verified':check['verified_files'],
        'reviewer_feedback':[{'kind':r['kind'],'text':r['review_text']} for r in reviewers['reviewers']],
        'inference':'NO_P_VALUE_OR_CI_NO_CONFIRMATORY_CLAIM',
        'historical_v1_result_pooled':False,
        'holdout_touched':False,
        'scientifically_approved':False,
        'submission_authorized':False}
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'pilot_report.json',result)
    paragraphs=['# WAMBU-001 | Revised v2 live pilot',
        '', '**Classification:** Development-only feasibility evidence, not confirmatory.',
        f'**Independent episodes:** {episodes}; turns per episode: {steps}.',
        f'**Genuine paid decisions:** {result["genuine_decision_calls"]}; recursive compactions: {result["genuine_compaction_calls"]}; advisory calls: {result["reviewer_calls"]}.',
        '', '| Arm | Raw accuracy | Unsafe approvals / reference rejections | False rejections |',
        '| --- | ---: | ---: | ---: |']
    for k,v in a.items():
        paragraphs.append(f'| {k} | {v["raw_accuracy"]:.3f} | {v["unsafe_approvals"]}/{v["unsafe_opportunities"]} | {v["false_rejections"]} |')
    paragraphs+=['',f'**Candidate primary episode-mean difference (summary minus ledger):** {result["descriptive_candidate_primary_difference"]:.4f}, strictly descriptive.',
                 '', 'No independent confirmation, no p-value, no publication authorisation.',
                 'The system intervention changes authoritative information exposure between arms.']
    (out/'pilot_report.md').write_text('\n'.join(paragraphs)+'\n')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--empirical',type=Path,required=True)
    p.add_argument('--advisory',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--episodes',type=int,required=True);p.add_argument('--steps',type=int,required=True)
    a=p.parse_args()
    r=report(a.empirical,a.advisory,a.out,episodes=a.episodes,steps=a.steps)
    print(json.dumps({k:r[k] for k in ('status','episodes_independent','genuine_decision_calls','genuine_compaction_calls','descriptive_candidate_primary_difference')},indent=2))
if __name__=='__main__':main()
