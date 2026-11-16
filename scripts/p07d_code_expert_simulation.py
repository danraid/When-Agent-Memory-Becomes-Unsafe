"""Blind AI simulations of engineering reviewers for real code-change cases.

These model roles are neither humans nor professional, independent reviewers.
They cannot grant human scientific labels; source provenance and literal evidence
are checked, uncertain applicability may always be marked insufficient.
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
    "backwards_compatibility":"openai/gpt-4.1-mini",
    "time_and_authority":"google/gemini-2.5-flash",
    "adversarial_code_review":"anthropic/claude-haiku-4.5",
}
ROLES_DESC={
    "backwards_compatibility":"Inspect whether changed code may breach explicit quoted backward-compatibility or language constraints. Identify only concerns supported by source text.",
    "time_and_authority":"Critically assess whether the pinned source guidance was actually effective at the PR decision time, distinguishing revision from activation. Abstain if historical applicability is not verified.",
    "adversarial_code_review":"Challenge code-diff interpretation, missing tests, alternative interpretations, scope leaps, and unsupported correctness claims. Prefer abstention when evidence cannot settle applicability.",
}
LABELS={"plausible_compliance","potential_conflict","insufficient_evidence"}


def visible_evidence(case):
    parts=[case["title"],case["description_retrospective"]]
    parts += [x["patch"] for x in case["code_patches_retrospective"]]
    parts += [x["exact_text"] for x in case["source_guidance"]["quoted_rules"]]
    parts += [x["excerpt"] for x in case["preclosure_comments"]]
    parts += [x["excerpt"] for x in case["preclosure_reviews"]]
    return parts


def prompt(role,case):
    if role not in ROLES:
        raise ValueError("UNDECLARED_AI_SIMULATED_EXPERT_ROLE")
    allowed={k:case[k] for k in (
        "task","repository_domain","title","description_retrospective",
        "created_at","code_patches_retrospective","preclosure_comments",
        "preclosure_reviews","source_guidance",
        "historical_normative_applicability_not_verified",
        "retrospective_diff_not_guaranteed_at_pr_creation",
    )}
    return (
        "You are an AI simulation of a scientific/engineering expert role, NOT a "
        "human reviewer. No web access or memorized PR knowledge. Do NOT predict "
        "or assert GitHub merge status. Treat PR code patches as retrospective; "
        "the pinned normative source might be revised after the decision date. "
        "Do not infer effective policy time or issuer jurisdiction.\n"
        "ROLE "+role+": "+ROLES_DESC[role]+"\n"
        "VISIBLE_SOURCE_ONLY:\n"+json.dumps(allowed,ensure_ascii=False,sort_keys=True)+
        "\nReturn ONLY one JSON object with precisely: "
        "assessment (plausible_compliance | potential_conflict | insufficient_evidence), "
        "quote (exact nonempty substring of a provided normative line, code patch, "
        "title, description or historical comment), "
        "rationale (12-1300 characters), confidence (number 0..1), "
        "normative_applicability_verified (false), "
        "human_expert (false). No invented runtime test results."
    )


def parse_vote(raw,case):
    text,unboxed=remove_exact_envelope(raw)
    try:
        v=json.loads(text)
    except (ValueError,TypeError):
        raise ValueError("AI_OUTPUT_NOT_COMPLETE_JSON") from None
    required={"assessment","quote","rationale","confidence",
              "normative_applicability_verified","human_expert"}
    if not isinstance(v,dict) or set(v)!=required:
        raise ValueError("AI_OUTPUT_SCHEMA_MISMATCH")
    if v["assessment"] not in LABELS:
        raise ValueError("AI_UNKNOWN_ASSESSMENT")
    if (not isinstance(v["quote"],str) or not v["quote"].strip() or
        not any(v["quote"] in x for x in visible_evidence(case))):
        raise ValueError("AI_QUOTE_NOT_VERBATIM_IN_VISIBLE_EVIDENCE")
    if (not isinstance(v["rationale"],str) or
        not 12<=len(v["rationale"])<=1300):
        raise ValueError("AI_INVALID_RATIONALE")
    if (type(v["confidence"]) not in (int,float) or
        not 0<=v["confidence"]<=1):
        raise ValueError("AI_INVALID_CONFIDENCE")
    if (v["normative_applicability_verified"] is not False or
        v["human_expert"] is not False):
        raise ValueError("AI_FALSE_AUTHORITY_OR_HUMAN_CLAIM")
    return v,unboxed


def execute(casebook:Path,config:Path,out:Path,key:str,transport=None):
    if not key:
        raise ValueError("MISSING_OPENROUTER_KEY")
    if out.exists() and any(out.iterdir()):
        raise ValueError("EVIDENCE_OUTPUT_NONEMPTY_NO_OVERWRITE")
    sourcebytes=casebook.read_bytes()
    cases=json.loads(sourcebytes)
    cfg=json.loads(config.read_text())
    if (cases.get("schema")!="WAMBU-P07D-REAL-CODE-BLIND-INPUTS-V1" or
        len(cases.get("cases",[]))!=8 or
        cfg["model_roles"]!=ROLES or
        cfg["expected_paid_reviews"]!=24 or
        cfg["max_paid_calls_reserved"]!=30):
        raise ValueError("INVALID_PREDECLARED_SOURCE_OR_AI_MATRIX")
    out.mkdir(parents=True,exist_ok=True)
    save(out/"metadata.json",{
        "schema":"WAMBU-P07D-REAL-CODE-AI-ROLE-REVIEWS-V1",
        "classification":"AI_SIMULATED_ROLES_NOT_HUMAN_EXPERTS",
        "models":ROLES,"casebook_sha256":digest(sourcebytes),
        "config_sha256":digest(config.read_bytes()),
        "expected_calls":24,"max_calls":30,
        "human_reviewers":0,"holdout_touched":False,
        "scientifically_approved":False,
        "github_sha":os.getenv("GITHUB_SHA"),
        "started_utc":datetime.now(timezone.utc).isoformat(),
    })
    client=OpenRouter(key,out/"ledger.json",30,transport)
    rows=[]
    response_ids=set()
    for case in cases["cases"]:
        for role,model in ROLES.items():
            p=prompt(role,case)
            row={"case_id":case["case_id"],"role":role,"model":model,
                 "prompt_sha256":digest(p.encode()),
                 "assessment":None,"error":None,
                 "source_label_visible":False,"human_expert":False}
            try:
                resp=client.call(model,p,max_tokens=420)
                rid=resp["response_id"]
                if rid in response_ids:
                    raise ValueError("DUPLICATE_PROVIDER_RESPONSE_ID")
                response_ids.add(rid)
                # Preserve raw provider output even if parsing fails.
                row.update({
                    "original_text":resp["text"],
                    "provider_id":rid,"observed_model":resp["observed_model"],
                    "usage":resp["usage"],"finish_reason":resp["finish_reason"],
                })
                vote,unboxed=parse_vote(resp["text"],case)
                row["assessment"]=vote
                row["json_fence_unboxed"]=unboxed
            except (ValueError,BenchmarkError) as exc:
                row["error"]=str(exc)[:180]
            rows.append(row)
            save(out/"reviews.json",rows)
            print(case["case_id"],role,"VALID" if row["assessment"] else "INVALID",flush=True)
    bycase=defaultdict(list)
    for r in rows:
        bycase[r["case_id"]].append(r)
    cases_summary=[]
    for c in cases["cases"]:
        grp=bycase[c["case_id"]]
        answers=[x["assessment"]["assessment"] for x in grp if x["assessment"]]
        cases_summary.append({
            "case_id":c["case_id"],"n_valid_votes":len(answers),
            "unanimous_ai_assessment":answers[0] if len(answers)==3
                and len(set(answers))==1 else None,
            "disagreement_or_incomplete":len(answers)<3 or len(set(answers))>1,
            "human_adjudicated":False,
        })
    summary={
        "status":"AI_PANEL_ALL_VALID_ADVISORY_ONLY" if all(x["assessment"] for x in rows)
                else "AI_PANEL_PARTIAL_OR_INVALID_NO_AUTOMATIC_RETRY",
        "expected_reviews":24,
        "valid_reviews":sum(x["assessment"] is not None for x in rows),
        "invalid_reviews":sum(x["assessment"] is None for x in rows),
        "provider_response_ids":len(response_ids),
        "error_counts":dict(Counter(x["error"] for x in rows if x["error"])),
        "cases":cases_summary,
        "independent_human_adjudicators":0,
        "real_software_changes_observed":8,
        "real_policy_authorization_gold":0,
        "full_original_knowledge_triage_reproduced":False,
        "scientifically_approved":False,"holdout_touched":False,
    }
    save(out/"summary.json",summary)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "science_approved":False,"human_adjudicators":0,
        "confirmatory_touched":False})
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",type=Path,required=True)
    p.add_argument("--config",type=Path,
                   default=Path("protocol/P07D_REAL_CODE_CHANGE_MATRIX.json"))
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    if not args.execute:
        p.error("The existing OpenRouter secret is used only on explicit execution.")
    result=execute(args.cases,args.config,args.out,
                   os.getenv("OPENROUTER_API_KEY") or
                   os.getenv("OPENROUTER") or "")
    print(json.dumps({k:result[k] for k in (
        "status","valid_reviews","expected_reviews",
        "provider_response_ids","independent_human_adjudicators")}))
    return 0 if result["valid_reviews"]==24 else 3


if __name__=="__main__":
    raise SystemExit(main())
