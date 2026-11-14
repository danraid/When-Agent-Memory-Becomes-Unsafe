"""Low-cost blinded LLM advisory reviews. NEVER independent scientific review."""
from __future__ import annotations
import json
from pathlib import Path
from article_hub.evidence import sha256, write_json
from article_hub.llm import request_advisory
from article_hub.report import create_manifest
from .runner import verify_output, StudyGateError


def blind_sample(observations: list[dict], per_condition: int = 2) -> list[dict]:
    allowed=('full_history','recent_window','recursive_summary','pinned_ledger')
    result=[]
    for condition in allowed:
        rows=sorted((x for x in observations if x['condition']==condition), key=lambda x:x['case_id'])
        for x in rows[:per_condition]:
            # Deliberately exclude evaluation, policy reference, expected labels and future events.
            result.append({'case_id':x['case_id'],'condition':condition,
                'prompt_excerpt':x['prompt'][-2400:],
                'raw_response':x['raw_response'], 'provider_response_id':x['provider_response_id']})
    if len(result) != len(allowed) * per_condition:
        raise StudyGateError('INSUFFICIENT_BLIND_REVIEW_SAMPLE')
    return result


def review(*, data_dir, output, config, ledger):
    valid=verify_output(data_dir)
    if valid['status']!='REAL_DEVELOPMENT_OR_PILOT_OBSERVED_NOT_SCIENTIFICALLY_APPROVED':
        raise StudyGateError('REVIEWS_REQUIRE_REAL_OBSERVED_PILOT')
    data_dir=Path(data_dir);output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise StudyGateError('REVIEW_OUTPUT_MUST_BE_EMPTY')
    output.mkdir(parents=True,exist_ok=True)
    observations=json.loads((data_dir/'observations.json').read_text())
    sample=blind_sample(observations)
    reviews=[]
    for kind,instruction in (
        ('contract','Assess raw JSON responses for syntax/format failures or parsing ambiguities. Do not guess reference labels.'),
        ('methodology','Identify confounding, privileged-policy baseline issues, missing independent episodes, and limitations in the design. Do not claim scientific novelty or approval.'),
    ):
        prompt=('You are an advisory methodological reviewer, not an independent peer reviewer. '
                'No reference labels, final deterministic outcomes or hidden future inputs are supplied. '
                + instruction + '\nRandomly selected? NO: deterministic lexicographic first two cases per condition. '
                'Return short specific concerns.\nSAMPLE:\n' + json.dumps(sample,ensure_ascii=False,sort_keys=True))
        response=request_advisory(prompt, config, ledger)
        rid=response.get('provider_response_id')
        if response.get('model')!='gpt-6-luna' or not isinstance(rid,str) or not rid.startswith('resp_'):
            raise StudyGateError('REVIEW_PROVIDER_PROVENANCE_MISSING')
        reviews.append({'kind':kind,'classification':'MODEL_ADVISORY_NOT_PEER_REVIEW',
                        'provider_response_id':rid,'model':response['model'],
                        'review_text':response['advisory_text'],'usage':response['observed_usage'],
                        'prompt_sha256':response['prompt_sha256'],
                        'scientific_approval':False})
    raw_ids={x['provider_response_id'] for x in observations if x['provider_response_id']}
    ids=[x['provider_response_id'] for x in reviews]
    if len(set(ids))!=2 or any(x in raw_ids for x in ids):
        raise StudyGateError('REVIEW_PROVIDER_IDS_NOT_INDEPENDENT_CALLS')
    result={'classification':'LOW_COST_BLINDED_AI_ADVISORY_NOT_PEER_REVIEW',
            'reviewers':reviews,'reviewed_cases':len(sample),
            'sample_rule':'first two cases lexically for each paid decision condition',
            'gold_labels_supplied':False,
            'scientifically_approved':False,'submission_authorized':False}
    write_json(output/'reviewers.json',result)
    man=create_manifest([output/'reviewers.json'],root=output,classification=result['classification'])
    write_json(output/'manifest.json',man)
    return result
