#!/usr/bin/env python3
"""Offline, unmodified upstream TypeCompact operator probe at a fixed commit.

This is a component-level probe, NOT a whole-framework or paper replication.
The upstream package is loaded without running its optional integration stack.
No model inference, oracle labels or confirmation data is consumed.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys
import types

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from article_hub.evidence import write_json,sha256,canonical
from temporal_v3.generator import generate_episode

PIN='a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4'
UPSTREAM='https://github.com/searchsim-org/cikm26-knowledge-triage'


def _load_upstream(source: pathlib.Path):
    pkg=source/'knowledge_triage'
    if not (pkg/'operators.py').is_file():
        raise ValueError('PINNED_UPSTREAM_NOT_AVAILABLE')
    mod=types.ModuleType('knowledge_triage')
    mod.__path__=[str(pkg)]
    sys.modules['knowledge_triage']=mod
    for name in ('classifier','kb','operators'):
        full=f'knowledge_triage.{name}'
        spec=importlib.util.spec_from_file_location(full,pkg/(name+'.py'))
        module=importlib.util.module_from_spec(spec)
        sys.modules[full]=module
        spec.loader.exec_module(module)
    return sys.modules['knowledge_triage.kb'],sys.modules['knowledge_triage.operators'],sys.modules['knowledge_triage.classifier']


def audit(upstream: pathlib.Path, out: pathlib.Path, *, episodes: int=8, steps: int=18):
    if not (1<=episodes<=16 and 18<=steps<=24):
        raise ValueError('FINITE_AUDIT_BOUND_REQUIRED')
    kb_mod,operator,classifier=_load_upstream(upstream)
    cases=[]
    for e in range(episodes):
        ep=generate_episode('WAMBU-v3-upstream-component-public','development',e,steps)
        for item in ep['items']:
            events=[x for x in item['history_before'] if x.startswith(('INITIAL AUTHORISED POLICY:','AUTHORISED POLICY AMENDMENT #'))]
            source_lines=events+['Non-authoritative operational observation, no rule update.']*8
            kb=kb_mod.KnowledgeBase.from_lines(source_lines)
            compacted,status=operator.type_compact(kb,512)
            got={x.text for x in compacted.items}
            mapped={x.text:x.type.value for x in kb.items}
            cases.append({'episode_id':ep['episode_id'],'step':item['step'],
                          'source_sha256':sha256(canonical(events)),
                          'status':status,'all_authorised_event_rows_retained':all(x in got for x in events),
                          'classified_constraint_events':sum(mapped[x]=='constraint' for x in events),
                          'total_authorised_events':len(events),
                          'retained_events':sum(x in got for x in events),
                          'compressed_item_count':len(compacted.items),
                          'upstream_operator':'TypeCompact',
                          'upstream_source_kind':'OFFICIAL_OPERATOR_WITH_OFFICIAL_REGEX_CLASSIFIER_COMPONENT_ONLY'})
    report={
      'classification':'OFFLINE_PINNED_UPSTREAM_TYPECOMPACT_COMPONENT_PROBE_NOT_PAPER_REPLICATION',
      'upstream_repository':UPSTREAM,'upstream_revision':PIN,
      'module_sha256':{x:sha256((upstream/'knowledge_triage'/(x+'.py')).read_bytes()) for x in ('classifier','kb','operators')},
      'episodes':episodes,'steps_per_episode':steps,'cases':len(cases),
      'all_authorised_event_rows_retained_cases':sum(x['all_authorised_event_rows_retained'] for x in cases),
      'event_classification_counts':{
        'official_regex_classified_constraints':sum(x['classified_constraint_events'] for x in cases),
        'total_authorised_events':sum(x['total_authorised_events'] for x in cases)},
      'unsafe_budget_failures':sum(x['status']=='COMPACTION_UNSAFE' for x in cases),
      'no_gpt_calls':True,'scientifically_approved':False,'submission_authorized':False,
      'limitations':['The official TypeCompact operator and regex classifier are used unchanged from pinned sources.',
                     'This is not full Knowledge Triage: no TypeDecompose, TypeRetrieve, risk classifier cascade, or LLM downstream decision comparison.',
                     'Only a synthetic authorised-event dataset and offline token budget are evaluated.',
                     'Constraint classification may not match authorised policy semantics.'],
    }
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'component_report.json',report)
    write_json(out/'component_rows.json',cases)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--upstream',required=True,type=pathlib.Path)
    p.add_argument('--out',required=True,type=pathlib.Path)
    p.add_argument('--episodes',type=int,default=8)
    p.add_argument('--steps',type=int,default=18)
    a=p.parse_args()
    result=audit(a.upstream,a.out,episodes=a.episodes,steps=a.steps)
    print(json.dumps({k:result[k] for k in ('classification','cases','all_authorised_event_rows_retained_cases','event_classification_counts','unsafe_budget_failures')},indent=2))
