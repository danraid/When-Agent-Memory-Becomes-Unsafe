"""P07f v2 AI-only role response schema: cite source ID, never copy literal quote.

The original v1 paid run 44076185311 remains immutable, with 4/24 strictly
valid original replies. This v2 is a distinct predeclared exploratory run.
The code deterministically looks up EXACT citation text from evidence IDs;
a model's supplied source-ID choice is validated, not rewritten.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from study.openrouter_comparison import digest, save
import scripts.p07f_ai_methodology_experts as v1


def role_prompt_v2(role,case):
    v1.require(role in v1.ROLE_FOCUS,"UNDECLARED_V2_ROLE")
    safe={k:case[k] for k in (
        "title","description_retrospective","created_at","evidence",
        "historical_source_available_at_creation",
        "historical_source_available_at_closure",
        "source_changed_between_events",
        "effective_normative_authority_not_verified",
        "independent_human_reference_action_available")}
    return (
        "You are an AI SIMULATION of an experimental-design specialist, NOT a "
        "human expert or journal reviewer. Review ONLY supplied source evidence "
        "without browsing, guessing GitHub disposition or relying on memorised PR "
        "outcomes. A norm's Git commit date is NOT proof of its effective force. "
        "All evidence texts are retrospective and correctness is not established.\n"
        "ROLE "+role+": "+v1.ROLE_FOCUS[role]+"\n"
        "CASE:\n"+json.dumps(safe,sort_keys=True,ensure_ascii=False)+"\n"
        "Return one complete JSON OBJECT with these fields exactly: "
        "decision (include_development_probe | exclude_current_policy_pairing | "
        "needs_additional_source), evidence_id (copy ONE existing id exactly, "
        "not a source quote), reason (20-1500 characters), "
        "risk_flags (one or more from policy_effectivity_unknown, "
        "postdecision_code_snapshot, missing_contemporaneous_rule, "
        "scope_mismatch, outcome_leakage_risk, non_agentic_task, "
        "insufficient_events, none), confidence (number 0..1), "
        "claims_human_expertise (false), human_ground_truth_established (false). "
        "Do not add a quote field: the audit system retrieves literal evidence "
        "using the selected ID, preventing inaccurate copy/formatting of quotes. "
        "Do not use markdown fences or explanations outside JSON."
    )


def parse_role_v2(raw,case):
    value,unboxed=v1.remove_exact_envelope(raw)
    try:
        obj=json.loads(value)
    except (ValueError,TypeError):
        raise ValueError("V2_INVALID_SINGLE_JSON_ENVELOPE") from None
    expected={"decision","evidence_id","reason","risk_flags",
              "confidence","claims_human_expertise","human_ground_truth_established"}
    v1.require(isinstance(obj,dict) and set(obj)==expected,
               "V2_INVALID_JSON_SCHEMA")
    v1.require(obj["decision"] in v1.DECISIONS,"V2_INVALID_DECISION")
    ev={e["id"]:e["text"] for e in case["evidence"]}
    v1.require(isinstance(obj["evidence_id"],str) and obj["evidence_id"] in ev,
               "V2_INVALID_EVIDENCE_ID")
    v1.require(isinstance(obj["reason"],str) and 20<=len(obj["reason"])<=1500,
               "V2_INVALID_RATIONALE")
    risks=obj["risk_flags"]
    v1.require(isinstance(risks,list) and len(risks)>0 and
               all(isinstance(x,str) for x in risks) and
               len(set(risks))==len(risks) and set(risks)<=v1.RISKS,
               "V2_INVALID_RISKS")
    v1.require(not("none" in risks and len(risks)>1),
               "V2_CONTRADICTORY_RISKS")
    v1.require(type(obj["confidence"]) in (int,float)
               and 0<=obj["confidence"]<=1,"V2_INVALID_CONFIDENCE")
    v1.require(obj["claims_human_expertise"] is False
               and obj["human_ground_truth_established"] is False,
               "V2_FALSE_HUMAN_OR_GOLD_CLAIM")
    source=ev[obj["evidence_id"]]
    validated={
        **obj,
        "quote":source[:160],
        "quote_origin":"EXACT_VERBATIM_SOURCE_ID_LOOKUP_NOT_LLM_GENERATED",
        "full_original_evidence_sha256":digest(source.encode("utf-8")),
    }
    return validated,unboxed


def activate():
    v1.role_prompt=role_prompt_v2
    v1.parse_role=parse_role_v2


def execute(prepared:Path,config:Path,out:Path,key:str,transport=None):
    cfg=json.loads(config.read_text())
    v1.require(cfg["version"]=="2.0.0" and
               cfg["evidence_contract"]=="AI_SELECTS_EXISTING_EVIDENCE_ID_DETERMINISTIC_SOURCE_LOOKUP_QUOTES" and
               cfg["historical_run_relabeling_forbidden"] is True and
               cfg["human_adjudicators"]==0,"V2_PROTOCOL_NOT_FROZEN")
    activate()
    summary=v1.execute(None,None,config,out,key,transport=transport,prepared=prepared)
    meta=json.loads((out/"metadata.json").read_text())
    meta["schema"]="WAMBU-P07F-V2-ORIGINAL-AI-ROLE-REVIEWS"
    meta["evidence_id_contract"]="DETERMINISTIC_EXACT_VERBATIM_SOURCE_LOOKUP"
    meta["previous_v1_run_id"]=44076185311
    meta["previous_v1_4_of_24_valid_preserved_not_repaired"]=True
    save(out/"metadata.json",meta)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "new_version":"2.0.0",
        "previous_v1_run_untouched":True,
        "author_approval":"PENDING","scientifically_approved":False,
        "human_adjudicators":0,"holdout_touched":False})
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prepared",required=True,type=Path)
    p.add_argument("--config",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if not a.execute:
        p.error("An explicit --execute is required for the new paid v2 run.")
    result=execute(a.prepared,a.config,a.out,
                   os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    print(json.dumps({k:result[k] for k in (
        "status","valid_first_round","invalid_first_round",
        "valid_syntheses","author_approval")},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
