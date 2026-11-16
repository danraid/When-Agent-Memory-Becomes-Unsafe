"""Three blind AI role simulations on actually observed public governance events.

Each model sees only an outcome-free retrospective proposal snapshot. Models
are not actual human experts or independent adjudicators. PR merge is recorded
historical behaviour, not normative gold for agent policy authorisation.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from scripts.p07b_detached_panel_audit import remove_exact_envelope
from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, save

ROLES={
    "governance_maintainer":"openai/gpt-4.1-mini",
    "temporal_process_expert":"google/gemini-2.5-flash",
    "adversarial_methodologist":"anthropic/claude-haiku-4.5",
}
TASK_DESCRIPTIONS={
    "governance_maintainer":"Assess whether the proposal, scope and available governance feedback suggest integration or closure, avoiding unsupported certainty.",
    "temporal_process_expert":"Focus on chronology and the difference between historical policy changes, current policy text and publication dates. Never infer missing timelines.",
    "adversarial_methodologist":"Challenge unsupported leap from popularity to merge, mistaken authority assumptions, and hindsight leakage. Abstain if not adequately supported.",
}
LABELS={"merged","closed_without_merge","insufficient_evidence"}


def evidence_text(case:dict)->str:
    return "\n".join([case["title"],case["proposal_excerpt"]]
                     +[c["excerpt"] for c in case["predecision_discussion"]])


def reviewer_prompt(role:str,case:dict)->str:
    if role not in ROLES:
        raise ValueError("UNKNOWN_AI_REVIEW_ROLE")
    safe={k:case[k] for k in ("question","title","proposal_excerpt",
                            "created_at_utc","predecision_discussion")}
    return (
        "SIMULATED AI specialist role, not a human expert, not human peer review.\n"
        "You are blind to historical merge/close outcome, other votes and evaluator sidecar. "
        "Do NOT use external browsing or memorised knowledge of these specific PRs. "
        "Do not infer an actual policy-authorisation gold decision from software PR status.\n"
        "ROLE: "+role+" | "+TASK_DESCRIPTIONS[role]+"\n"
        "CASE:\n"+json.dumps(safe,ensure_ascii=False,sort_keys=True)+"\n"
        "Predict the eventual publicly observed PR disposition, or abstain when "
        "the provided pre-decision evidence is insufficient. "
        "Return a single JSON object with exactly: "
        "disposition (merged | closed_without_merge | insufficient_evidence), "
        "evidence_quote (exact nonempty substring of the presented proposal title, "
        "body or predecision comments), "
        "reason (12-1200 characters), confidence (0..1), "
        "claims_to_be_human_expert (false). No Markdown if possible."
    )


def parse_vote(raw:str,case:dict)->tuple[dict,bool]:
    text,unwrapped=remove_exact_envelope(raw)
    try:
        v=json.loads(text)
    except (ValueError,TypeError):
        raise ValueError("UNPARSABLE_RESPONSE_JSON") from None
    if not isinstance(v,dict) or set(v)!={"disposition","evidence_quote","reason","confidence","claims_to_be_human_expert"}:
        raise ValueError("INVALID_AI_ROLE_SCHEMA")
    if v["disposition"] not in LABELS:
        raise ValueError("INVALID_DISPOSITION")
    if not isinstance(v["evidence_quote"],str) or not v["evidence_quote"].strip() or v["evidence_quote"] not in evidence_text(case):
        raise ValueError("QUOTE_NOT_IN_MODEL_VISIBLE_CASE")
    if not isinstance(v["reason"],str) or not 12<=len(v["reason"])<=1200:
        raise ValueError("INVALID_RATIONALE")
    if type(v["confidence"]) not in (float,int) or not 0<=v["confidence"]<=1:
        raise ValueError("INVALID_CONFIDENCE")
    if v["claims_to_be_human_expert"] is not False:
        raise ValueError("FALSE_HUMAN_EXPERT_IMPERSONATION")
    return v,unwrapped


def execute(cases_path:Path, config_path:Path, out:Path,key:str,transport=None)->dict:
    if not key:
        raise ValueError("OPENROUTER_SECRET_UNAVAILABLE")
    if out.exists() and any(out.iterdir()):
        raise ValueError("ORIGINAL_AI_PANEL_OUTPUT_NOT_OVERWRITABLE")
    raw=cases_path.read_bytes()
    casebook=json.loads(raw)
    cfg=json.loads(config_path.read_text())
    if casebook.get("schema")!="WAMBU-P07C-REAL-GOVERNANCE-INPUTS-V1" or len(casebook.get("cases",[]))!=8:
        raise ValueError("BAD_SOURCE_CASEBOOK")
    if cfg["ai_roles"]!=ROLES or cfg["paid_calls_reserved_max"]<24:
        raise ValueError("UNPREDECLARED_MODEL_MATRIX")
    out.mkdir(parents=True,exist_ok=True)
    meta={
        "schema":"WAMBU-P07C-SIMULATED-AI-EXPERT-REVIEWS-V1",
        "classification":"REAL_PR_EVENTS_AI_SIMULATED_EXPERTS_NOT_HUMANS",
        "original_model_inputs_sha256":digest(raw),
        "original_model_config_sha256":digest(config_path.read_bytes()),
        "role_models":ROLES,
        "expected_ai_calls":24,"max_reservations":cfg["paid_calls_reserved_max"],
        "human_experts":0,"scientifically_approved":False,
        "confirmatory_touched":False,
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "git_sha":os.getenv("GITHUB_SHA"),
    }
    save(out/"metadata.json",meta)
    client=OpenRouter(key,out/"provider_ledger.json",cfg["paid_calls_reserved_max"],transport)
    results=[]
    ids=set()
    for case in casebook["cases"]:
        for role,model in ROLES.items():
            p=reviewer_prompt(role,case)
            row={"case_id":case["case_id"],"role":role,"requested_model":model,
                 "prompt_sha256":digest(p.encode()),"vote":None,"failure":None,
                 "outcome_label_visible":False,"human_reviewer":False}
            try:
                response=client.call(model,p,max_tokens=450)
                rid=response["response_id"]
                if rid in ids:
                    raise ValueError("DUPLICATE_PROVIDER_RESPONSE_ID")
                ids.add(rid)
                # Preserve original provider response even when JSON/schema parse fails.
                row.update({
                    "original_model_text":response["text"],
                    "original_provider_response_id":rid,
                    "provider_observed_model":response["observed_model"],
                    "provider_usage":response["usage"],
                    "provider_finish_reason":response["finish_reason"],
                })
                vote,wrapped=parse_vote(response["text"],case)
                row["json_envelope_unwrapped"]=wrapped
                row["vote"]=vote
            except (BenchmarkError,ValueError) as exc:
                row["failure"]=str(exc)[:170]
            results.append(row)
            save(out/"raw_reviews.json",results)
            print(case["case_id"],role,"OK" if row["vote"] else "MISSING",flush=True)
    grouped=defaultdict(list)
    for row in results:
        grouped[row["case_id"]].append(row)
    by_case=[]
    for case in casebook["cases"]:
        votes=[r["vote"]["disposition"] for r in grouped[case["case_id"]] if r["vote"]]
        unanimous=len(votes)==3 and len(set(votes))==1
        by_case.append({
            "case_id":case["case_id"],"valid_ai_votes":len(votes),
            "unanimous_ai_disposition":votes[0] if unanimous else None,
            "ai_disagreement":len(set(votes))>1,
            "no_human_validation":True,
        })
    summary={
        "status":"SIMULATED_AI_PANEL_COMPLETE_NOT_SCIENTIFICALLY_ADJUDICATED"
                 if all(r["vote"] is not None for r in results)
                 else "SIMULATED_AI_PANEL_PARTIAL_PROVIDER_OR_FORMAT_ERRORS",
        "expected_votes":24,"valid_votes":sum(r["vote"] is not None for r in results),
        "unanimous_ai_cases":sum(r["unanimous_ai_disposition"] is not None for r in by_case),
        "ai_disagreement_cases":sum(r["ai_disagreement"] for r in by_case),
        "error_counts":dict(Counter(r["failure"] for r in results if r["failure"])),
        "case_descriptions":by_case,
        "independent_human_reviewers":0,
        "real_source_events":8,
        "historical_pr_disposition_is_not_policy_correctness":True,
        "scientifically_approved":False,
        "holdout_touched":False,
    }
    save(out/"summary.json",summary)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json") if p.name!="manifest.json"},
        "human_reviewers":0,"holdout_touched":False,
        "scientifically_approved":False,
    })
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True,type=Path)
    p.add_argument("--config",type=Path,
                   default=Path("protocol/P07C_REAL_GOVERNANCE_SOURCE_MATRIX.json"))
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if not a.execute:
        p.error("Paid calls require --execute")
    s=execute(a.cases,a.config,a.out,
              os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    print(json.dumps({k:s[k] for k in ("status","valid_votes","expected_votes","unanimous_ai_cases","independent_human_reviewers")}))
    return 0 if s["valid_votes"]==24 else 3


if __name__=="__main__":
    raise SystemExit(main())
