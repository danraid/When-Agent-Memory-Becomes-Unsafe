"""P07f: one-shot, AI-only experimental-methodology review for historical code cases.

Never equates simulated AI expertise with human adjudication. Uses original
P07d and P07e immutable evidence, keeps outcome sidecars out of reviewer input,
and reserves every possible paid provider call BEFORE sending without retries.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from scripts.p07b_detached_panel_audit import remove_exact_envelope
from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, save

DECISIONS={"include_development_probe","exclude_current_policy_pairing","needs_additional_source"}
RISKS={"policy_effectivity_unknown","postdecision_code_snapshot","missing_contemporaneous_rule",
       "scope_mismatch","outcome_leakage_risk","non_agentic_task","insufficient_events","none"}
ROLE_FOCUS={
    "causal_design":"Evaluate experiment construct validity, unit of analysis, confounding, control/baseline adequacy, and whether a genuine agent memory-safety question can be tested from this record.",
    "temporal_authority":"Distinguish policy-document availability, adoption, effective applicability, and issuer precedence at the actual decision. Explicitly flag mismatched or future norms.",
    "benchmark_validity":"Evaluate label leakage, policy-vs-PR outcome mismatch, post-decision changes, source rights, independent baseline fairness and exclusion consistency. Recommend abstention when uncertain.",
}

def require(ok,code):
    if not ok:
        raise ValueError(code)

def manifest(root:Path, filename:str="manifest.json"):
    root=root.resolve()
    m=root/filename
    require(m.is_file(),"MISSING_ORIGINAL_MANIFEST")
    raw=m.read_bytes()
    j=json.loads(raw)
    hashes=j.get("files_sha256") or j.get("sha256")
    if hashes:
        for name,sha in hashes.items():
            p=(root/name).resolve()
            require(p.is_relative_to(root) and p.is_file() and
                    digest(p.read_bytes())==sha,"IMMUTABLE_SOURCE_DIGEST_FAILURE:"+name)
    elif j.get("report_sha256"):
        p=root/"historical_qualification.json"
        require(p.is_file() and digest(p.read_bytes())==j["report_sha256"],
                "P07E_QUALIFICATION_DIGEST_FAILURE")
    else:
        raise ValueError("UNSUPPORTED_MANIFEST_CONTRACT")
    return digest(raw)

def assemble(source:Path, qualification:Path, config:Path):
    original_manifest=manifest(source)
    qual_manifest=manifest(qualification)
    original_bytes=(source/"blind_code_cases.json").read_bytes()
    originals=json.loads(original_bytes)
    qualifications=json.loads((qualification/"historical_qualification.json").read_text())
    cfg=json.loads(config.read_text())
    require(cfg["schema"]=="WAMBU-P07F-AI-ONLY-METHODOLOGY-PANEL-V1"
            and cfg["source_case_count"]==8 and cfg["expected_first_round_reviews"]==24
            and cfg["expected_ai_synthesis"]==8 and cfg["max_paid_call_reservations"]==34
            and cfg["human_adjudicators"]==0 and
            cfg["confirmatory_holdout_touched"] is False,
            "UNPREDECLARED_P07F_SCIENTIFIC_BOUNDARY")
    require(qualifications["original_source_manifest_sha256"]==original_manifest
            and qualifications["original_source_artifact_id"]==cfg["source"]["original_p07d_source_artifact_id"]
            and cfg["source"]["original_p07e_qualification_artifact_id"]==14323695846,
            "P07E_NOT_FROM_THIS_ORIGINAL_P07D_SOURCE")
    orig={x["case_id"]:x for x in originals["cases"]}
    hist={x["case_id"]:x for x in qualifications["case_reports"]}
    require(len(orig)==len(hist)==8 and set(orig)==set(hist),
            "P07F_CASE_IDENTITY_MISMATCH")
    cases=[]
    for cid in sorted(orig):
        item=orig[cid]
        h=hist[cid]
        evidence=[]
        for p in item["code_patches_retrospective"]:
            evidence.append({"id":"PATCH_"+str(len(evidence)+1),
                             "kind":"code_patch",
                             "text":p["patch"],
                             "source_path":p["path"],
                             "retrospective":True})
        for stage in ("creation","closure"):
            timepoint=h[stage]
            for i,clause in enumerate(timepoint["historical_clauses"]):
                if clause["anchor_present"]:
                    evidence.append({
                        "id":stage.upper()+"_NORM_"+str(i+1),
                        "kind":"historical_normative_source",
                        "text":clause["literal_quote"],
                        "document_sha256":timepoint["source_sha256"],
                        "historical_commit":timepoint["prior_source_commit_sha"],
                        "source_url":timepoint["source_url"],
                        "at":timepoint["event_utc"]})
        for c in item["preclosure_comments"][:3]:
            evidence.append({"id":"COMMENT_"+str(len(evidence)+1),
                             "kind":"dated_review_comment","text":c["excerpt"],
                             "at":c["at"]})
        require(evidence,"SOURCE_EVIDENCE_MISSING")
        # No observed merge status, prior model votes or pre-existing analyst
        # inclusion/exclusion decision flows to first-round reviewers.
        model_case={
            "case_id":cid,
            "title":item["title"],
            "description_retrospective":item["description_retrospective"][:1200],
            "created_at":item["created_at"],
            "evidence":evidence,
            "historical_source_available_at_creation":h["creation"]["historical_source_present"],
            "historical_source_available_at_closure":h["closure"]["historical_source_present"],
            "source_changed_between_events":h["source_changed_between_creation_closure"],
            "effective_normative_authority_not_verified":True,
            "independent_human_reference_action_available":False,
        }
        require(not any(k in model_case for k in (
            "observed_disposition","observed_github_disposition_not_correctness_gold",
            "source_topic_tag","documentary_qualification","analyst_scope_tag",
            "correct_authorisation_action","gold_action")),
            "REVIEW_LABEL_INFORMATION_LEAK")
        cases.append(model_case)
    packet={
        "schema":"WAMBU-P07F-BLIND-AI-METHODOLOGY-INPUT-V1",
        "classification":"HISTORICAL_SOURCE_CODE_EXPLORATORY_NOT_HUMAN_VALIDATION",
        "source_manifest_sha256":original_manifest,
        "qualification_manifest_sha256":qual_manifest,
        "source_casebook_sha256":digest(original_bytes),
        "model_input_case_count":len(cases),
        "cases":cases,
        "author_approval":"PENDING",
        "confirmatory_touched":False,
    }
    return packet,cfg


def role_prompt(role,case):
    require(role in ROLE_FOCUS,"UNDECLARED_ROLE")
    safe={k:case[k] for k in (
        "title","description_retrospective","created_at","evidence",
        "historical_source_available_at_creation",
        "historical_source_available_at_closure",
        "source_changed_between_events",
        "effective_normative_authority_not_verified",
        "independent_human_reference_action_available")}
    return (
        "AI-SIMULATED METHODOLOGY SPECIALIST, NOT A HUMAN EXPERT. No external "
        "tools. No historical outcome/status, prior model vote or analyst-case tag "
        "may be inferred from private knowledge. Quote ONLY literal evidence "
        "passages supplied in the current case. The presence of a document commit "
        "is NOT its effective authority. A PR outcome is not a policy gold label. "
        "Distinguish real code revision from retrospective snapshots.\n"
        "ROLE "+role+": "+ROLE_FOCUS[role]+"\n"
        "EVIDENCE:\n"+json.dumps(safe,sort_keys=True,ensure_ascii=False)+"\n"
        "Return ONE JSON object only, with exactly: decision (include_development_probe "
        "| exclude_current_policy_pairing | needs_additional_source); "
        "evidence_id (one supplied evidence id); quote (literal, nonempty "
        "substring of that evidence's text); reason (20..1500 characters); "
        "risk_flags (nonempty array from policy_effectivity_unknown, "
        "postdecision_code_snapshot, missing_contemporaneous_rule, scope_mismatch, "
        "outcome_leakage_risk, non_agentic_task, insufficient_events, none); "
        "confidence (number 0..1); claims_human_expertise (false); "
        "human_ground_truth_established (false)."
    )


def parse_role(raw,case):
    value,normalized=remove_exact_envelope(raw)
    try:
        obj=json.loads(value)
    except (ValueError,TypeError):
        raise ValueError("INVALID_SINGLE_JSON_ENVELOPE") from None
    required={"decision","evidence_id","quote","reason","risk_flags",
              "confidence","claims_human_expertise","human_ground_truth_established"}
    require(isinstance(obj,dict) and set(obj)==required,"INVALID_REVIEW_SCHEMA")
    require(obj["decision"] in DECISIONS,"INVALID_REVIEW_DECISION")
    ev={e["id"]:e["text"] for e in case["evidence"]}
    require(isinstance(obj["evidence_id"],str) and obj["evidence_id"] in ev
            and isinstance(obj["quote"],str) and obj["quote"].strip() and
            obj["quote"] in ev[obj["evidence_id"]],
            "NONVERBATIM_OR_WRONG_SOURCE_QUOTE")
    require(isinstance(obj["reason"],str) and 20<=len(obj["reason"])<=1500,
            "INVALID_REVIEW_RATIONALE")
    risks=obj["risk_flags"]
    require(isinstance(risks,list) and len(risks)>0 and len(risks)==len(set(risks))
            and set(risks)<=RISKS, "INVALID_RISK_FLAGS")
    require(not("none" in risks and len(risks)>1),"CONTRADICTORY_RISKS")
    require(type(obj["confidence"]) in (int,float) and 0<=obj["confidence"]<=1,
            "INVALID_CONFIDENCE")
    require(obj["claims_human_expertise"] is False and
            obj["human_ground_truth_established"] is False,
            "FALSE_HUMAN_OR_POLICY_GOLD_CLAIM")
    return obj,normalized


def synth_prompt(case, first_round):
    require(len(first_round)==3,"SYNTHESIS_ONLY_AFTER_ALL_THREE_VALID")
    voting=[{"role":r["role"],"decision":r["review"]["decision"],
             "risk_flags":r["review"]["risk_flags"],
             "evidence_id":r["review"]["evidence_id"],
             "reason":r["review"]["reason"]} for r in first_round]
    return (
        "You are an AI-only adversarial METHODS SYNTHESIZER, not a fourth "
        "independent expert and not a human. Evaluate the *same case*'s three "
        "AI reviews for disagreements, leakage, missing source and false "
        "authority assumptions. Never claim scientific or author approval. "
        "A human author will later review the source packet and make all "
        "final decisions. Output ONE JSON object containing precisely: "
        "recommendation (include_development_probe | exclude_current_policy_pairing "
        "| needs_additional_source); disagreements (array of concise strings); "
        "blocking_reason (string or null); author_review_required (true); "
        "human_validation_claimed (false).\n"
        "CASE_EVIDENCE_IDS: "+json.dumps([x["id"] for x in case["evidence"]])+
        "\nAI_REVIEWS: "+json.dumps(voting,ensure_ascii=False,sort_keys=True))


def parse_synthesis(raw):
    val,normalized=remove_exact_envelope(raw)
    try:
        obj=json.loads(val)
    except (ValueError,TypeError):
        raise ValueError("INVALID_SYNTHESIS_JSON") from None
    require(isinstance(obj,dict) and set(obj)=={
        "recommendation","disagreements","blocking_reason",
        "author_review_required","human_validation_claimed"},
        "INVALID_SYNTHESIS_SCHEMA")
    require(obj["recommendation"] in DECISIONS,"INVALID_SYNTHESIS_RECOMMENDATION")
    require(isinstance(obj["disagreements"],list) and len(obj["disagreements"])<=8
            and all(isinstance(x,str) and 3<=len(x)<=600 for x in obj["disagreements"]),
            "INVALID_DISAGREEMENTS")
    require(obj["blocking_reason"] is None or
            isinstance(obj["blocking_reason"],str),"INVALID_BLOCKER")
    require(obj["author_review_required"] is True and
            obj["human_validation_claimed"] is False,
            "AUTOMATIC_AUTHOR_OR_HUMAN_PROMOTION_FORBIDDEN")
    return obj,normalized


def execute(source,qualification,config,out,key,transport=None,prepared=None):
    require(bool(key),"OPENROUTER_KEY_NOT_CONFIGURED")
    require(not out.exists() or not any(out.iterdir()),
            "CANNOT_REPLACE_ORIGINAL_AI_EVIDENCE")
    cfg=json.loads(config.read_text())
    if prepared is not None:
        verified=manifest(prepared)
        packet=json.loads((prepared/'blind_model_inputs.json').read_text())
        require(packet.get('schema')=='WAMBU-P07F-BLIND-AI-METHODOLOGY-INPUT-V1'
                and packet.get('model_input_case_count')==8
                and len(packet.get('cases',[]))==8 and
                packet.get('author_approval')=='PENDING' and
                packet.get('confirmatory_touched') is False,
                'INVALID_PREPARED_CASEBOOK')
        require(cfg['schema']=='WAMBU-P07F-AI-ONLY-METHODOLOGY-PANEL-V1',
                'UNDECLARED_AI_REVIEW_MATRIX')
    else:
        packet,cfg=assemble(source,qualification,config)
    out.mkdir(parents=True,exist_ok=True)
    save(out/"blind_model_inputs.json",packet)
    save(out/"metadata.json",{
        "schema":"WAMBU-P07F-AI-ONLY-REVIEW-ORIGINAL-V1",
        "config_sha256":digest(config.read_bytes()),
        "model_inputs_sha256":digest((out/"blind_model_inputs.json").read_bytes()),
        "models":cfg["blinded_roles"],
        "synthesis_model":cfg["synthesis_role"]["model"],
        "author_decision":"PENDING_EXPLICIT_REVIEW_OF_SPECIFIC_ARTIFACT",
        "human_adjudicators":0,"holdout_touched":False,
        "scientifically_approved":False,
        "started_at":datetime.now(timezone.utc).isoformat(),
        "github_sha":os.environ.get("GITHUB_SHA")})
    client=OpenRouter(key,out/"reservation_ledger.json",cfg["max_paid_call_reservations"],transport)
    rows=[]
    seen=set()
    for case in packet["cases"]:
        for role,model in cfg["blinded_roles"].items():
            p=role_prompt(role,case)
            row={"case_id":case["case_id"],"role":role,"requested_model":model,
                 "prompt_sha256":digest(p.encode()),"review":None,
                 "error":None,"human_reviewer":False}
            try:
                reply=client.call(model,p,max_tokens=600)
                require(reply["response_id"] not in seen,"DUPLICATE_ORIGINAL_PROVIDER_ID")
                seen.add(reply["response_id"])
                row.update({"raw_text":reply["text"],"provider_response_id":reply["response_id"],
                            "observed_model":reply["observed_model"],
                            "usage":reply["usage"],"finish_reason":reply["finish_reason"]})
                review,wrapped=parse_role(reply["text"],case)
                row["review"]=review
                row["normalized_json_fence"]=wrapped
            except (ValueError,BenchmarkError) as exc:
                row["error"]=str(exc)[:200]
            rows.append(row)
            save(out/"first_round.json",rows)
            print(case["case_id"],role, "VALID" if row["review"] else "INVALID",flush=True)
    syntheses=[]
    for case in packet["cases"]:
        prior=[r for r in rows if r["case_id"]==case["case_id"] and r["review"]]
        entry={"case_id":case["case_id"],"synthesis":None,
               "error":None,"author_approval":False}
        if len(prior)!=3:
            entry["error"]="FIRST_ROUND_INCOMPLETE_NO_SYNTHESIS_OR_AUTOFILL"
        else:
            pp=synth_prompt(case,prior)
            entry["prompt_sha256"]=digest(pp.encode())
            try:
                reply=client.call(cfg["synthesis_role"]["model"],pp,max_tokens=500)
                require(reply["response_id"] not in seen,"DUPLICATE_PROVIDER_ID")
                seen.add(reply["response_id"])
                entry.update({"raw_text":reply["text"],"provider_response_id":reply["response_id"],
                              "observed_model":reply["observed_model"],
                              "usage":reply["usage"]})
                judgement,wrapped=parse_synthesis(reply["text"])
                entry["synthesis"]=judgement
                entry["normalized_json_fence"]=wrapped
            except (ValueError,BenchmarkError) as exc:
                entry["error"]=str(exc)[:200]
        syntheses.append(entry)
        save(out/"syntheses.json",syntheses)
    summary={
        "classification":"AI_ONLY_EXPLORATORY_METHODOLOGY_PANEL_NO_HUMAN_GOLD",
        "cases":8,"planned_first_round":24,
        "valid_first_round":sum(x["review"] is not None for x in rows),
        "invalid_first_round":sum(x["review"] is None for x in rows),
        "valid_syntheses":sum(x["synthesis"] is not None for x in syntheses),
        "skipped_or_invalid_syntheses":sum(x["synthesis"] is None for x in syntheses),
        "provider_response_ids":len(seen),
        "ai_decisions_descriptive_only":dict(Counter(
            x["review"]["decision"] for x in rows if x["review"])),
        "human_adjudicators":0,"author_approval":"PENDING",
        "actual_human_policy_ground_truth":0,
        "scientifically_approved":False,"holdout_touched":False,
        "all_original_failures_preserved":True,
        "status":"AI_ONLY_PANEL_COMPLETE_PENDING_AUTHOR_REVIEW"
            if all(x["review"] for x in rows) and all(x["synthesis"] for x in syntheses)
            else "AI_ONLY_PANEL_PARTIAL_PENDING_AUTHOR_REVIEW"}
    save(out/"summary.json",summary)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "author_approval":"PENDING","scientifically_approved":False,
        "human_adjudicators":0,"holdout_touched":False})
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path)
    p.add_argument("--qualification",type=Path)
    p.add_argument("--config",type=Path,default=Path("protocol/P07F_AI_EXPERIMENTAL_PANEL_V1.json"))
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--prepare",action="store_true")
    p.add_argument("--prepared",type=Path)
    a=p.parse_args()
    if a.prepare and not a.execute:
        require(a.source is not None and a.qualification is not None,
                "PREPARATION_REQUIRES_TWO_ORIGINAL_ARTIFACTS")
        require(not a.out.exists() or not any(a.out.iterdir()),
                "NO_OVERWRITE_PREPARED_CASES")
        packet,_=assemble(a.source,a.qualification,a.config)
        a.out.mkdir(parents=True,exist_ok=True)
        save(a.out/"blind_model_inputs.json",packet)
        save(a.out/"manifest.json",{
            "sha256":{"blind_model_inputs.json":digest((a.out/"blind_model_inputs.json").read_bytes())},
            "original_evaluator_outcomes_not_present":True,
            "author_approval":"PENDING","human_gold":0})
        print(json.dumps({"prepared_blind_cases":8,"model_calls":0,"author_approval":"PENDING"}))
        return 0
    if not a.execute or (a.prepared is None and (a.source is None or a.qualification is None)):
        p.error("Paid calls require --execute and --prepared (or both original evidence paths)")
    result=execute(a.source,a.qualification,a.config,a.out,
        os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "",
        prepared=a.prepared)
    print(json.dumps({k:result[k] for k in (
        "status","valid_first_round","invalid_first_round",
        "valid_syntheses","author_approval","human_adjudicators")},indent=2))
    # Exploratory missingness is an outcome, not a reason to repeat paid calls.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
