"""P10 provider-distinct, blind AI advisory science panel on existing WAMBU evidence.

This is independent *AI inference* conditional on four different model providers,
not actual human expertise, a prospective confirmatory study, or author signoff.
Original provider responses are preserved unedited. No unbounded paid retries.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, save

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={"support_exploratory_review","major_revision","reject_scientific_claim","abstain_unverifiable"}
REQUIRED={"recommendation","major_objections","minor_objections","verified_points",
          "unverified_points","scope","is_human_reviewer"}
OBJECTION={"finding","source_id","quoted_evidence","required_change"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def config_and_evidence(config_path:Path):
    raw=config_path.read_bytes()
    cfg=json.loads(raw)
    require(cfg["schema"]=="WAMBU-P10-AI-MANAGED-INDEPENDENT-ADVISORY-2026-11-16-V1",
            "INVALID_PREDECLARED_PANEL")
    require(len(cfg["reviewers"])==4 and cfg["max_calls"]==5 and
            cfg["author_final_decision"] is None and
            cfg["confirmatory_holdout_touched"] is False,
            "INVALID_PANEL_AUTHORITY")
    allmodels=[x["model"] for x in cfg["reviewers"]]+[cfg["chair"]["model"]]
    require(len(set(x.split("/")[0] for x in allmodels))==5,"REVIEWER_PROVIDERS_NOT_DISTINCT")
    manuscript=(ROOT/cfg["manuscript"]).read_text(encoding="utf-8")
    ledger_path=ROOT/cfg["claim_ledger"]
    ledger=json.loads(ledger_path.read_text(encoding="utf-8"))
    index={c["id"]:c for c in ledger["claims"]}
    novelty=(ROOT/cfg["novelty_screen"]).read_text(encoding="utf-8")
    require(len(manuscript)<=cfg["max_manuscript_chars"],"MANUSCRIPT_EXCEEDS_BOUND")
    receipts={}
    for claim in ledger["claims"]:
        path=ROOT/claim["evidence"]
        require(path.is_file() and path.resolve().is_relative_to(ROOT.resolve()),
                "UNTRUSTED_CLAIM_SOURCE_PATH")
        s=path.read_text(encoding="utf-8")
        receipts[claim["id"]]={"source_id":claim["id"],"source_path":claim["evidence"],
                               "source_sha256":digest(path.read_bytes()),
                               "source_text":s[:cfg["max_source_chars_per_claim"]],
                               "truncated":len(s)>cfg["max_source_chars_per_claim"]}
    return cfg, raw, manuscript, ledger, novelty, receipts


def prompts(config_path:Path):
    cfg,cfg_raw,paper,ledger,novelty,receipts=config_and_evidence(config_path)
    prompts=[]
    for r in cfg["reviewers"]:
        selected=[receipts[key] for key in r["claims"]]
        scope={"reviewer_id":r["id"],"speciality":r["focus"],
               "paper":paper,"selected_evidence":selected,
               "external_novelty_screen_excerpt":novelty[:cfg["max_novelty_chars"]],
               "note":"Evidence excerpts and a development paper are not an original-replay proof. Full archived source may be larger than presented context."}
        p=("You are a simulated independent SCIENTIFIC CRITIC driven by an AI model, NOT "
           "a real human reviewer. Independently evaluate only your assigned scope, "
           "without seeing any other reviewers or hidden final decision. Do not claim "
           "you ran source code, inspected GitHub artifacts or browsed externally; "
           "you may only say you assessed the provided excerpts. Do not fabricate "
           "citations, author responses, or method novelty. The user alone has final "
           "approval and the private confirmatory holdout is unopened.\n"
           "RETURN ONLY A SINGLE JSON OBJECT with fields: recommendation (one of "
           "support_exploratory_review | major_revision | reject_scientific_claim | "
           "abstain_unverifiable), major_objections (list), minor_objections (list), "
           "verified_points (list), unverified_points (list), scope (string), "
           "is_human_reviewer (false). Each objection contains finding, source_id, "
           "quoted_evidence, required_change; quote must be an exact contiguous "
           "substring of the supplied paper or the source_text for source_id. "
           "source_id must be one of the selected claim IDs or manuscript. "
           "Uncertain facts remain unverified. Avoid generic praise; report serious "
           "falsification and information-access concerns.\n"
           "EVIDENCE_PACKET:\n"+json.dumps(scope,ensure_ascii=False,sort_keys=True))
        prompts.append((r,p,selected))
    return cfg,cfg_raw,ledger,receipts,prompts


def interpret(raw:str, packet:list[dict], manuscript:str):
    # Preserve raw bytes; parse an exact single complete JSON object only.
    from scripts.p07b_detached_panel_audit import remove_exact_envelope
    content,_=remove_exact_envelope(raw)
    try:
        v=json.loads(content)
    except (ValueError,TypeError):
        raise ValueError("REVIEW_NOT_SINGLE_JSON") from None
    require(isinstance(v,dict) and set(v)==REQUIRED,"REVIEW_SCHEMA_ERROR")
    require(v["recommendation"] in ALLOWED,"REVIEW_RECOMMENDATION_NOT_PREDECLARED")
    require(v["is_human_reviewer"] is False,"FALSE_HUMAN_REVIEWER_CLAIM")
    require(isinstance(v["scope"],str) and len(v["scope"])>5,"INVALID_SCOPE")
    source={x["source_id"]:x["source_text"] for x in packet}
    source["manuscript"]=manuscript
    for k in ("major_objections","minor_objections","verified_points","unverified_points"):
        require(isinstance(v[k],list) and len(v[k])<=20,"INVALID_REVIEW_LIST:"+k)
    for k in ("major_objections","minor_objections"):
        for objection in v[k]:
            require(isinstance(objection,dict) and set(objection)==OBJECTION,
                    "OBJECTION_SCHEMA")
            require(objection["source_id"] in source,"UNDECLARED_SOURCE_ID")
            require(isinstance(objection["quoted_evidence"],str) and len(objection["quoted_evidence"])>=8
                    and objection["quoted_evidence"] in source[objection["source_id"]],
                    "NON_VERBATIM_EVIDENCE")
            require(all(isinstance(objection[t],str) and len(objection[t])>=8
                        for t in ("finding","required_change")),"UNSUPPORTED_OBJECTION")
    for k in ("verified_points","unverified_points"):
        require(all(isinstance(x,str) and len(x)>=8 for x in v[k]),"INVALID_REVIEW_POINT")
    return v


def chair_prompt(manuscript_sha:str, records:list[dict])->str:
    panel=[{"reviewer":r["reviewer_id"],"model":r["requested_model"],
            "response_id":r.get("response_id"),"parsed_recommendation":r.get("review",{}).get("recommendation"),
            "valid_review":r.get("review") is not None,
            "full_original_text":r.get("original_response_text"),
            "error":r.get("error")} for r in records]
    return ("You are an AI science panel chair, not a human, editor or journal. "
            "Four AI reviewers from distinct model providers independently read "
            "different evidence domains of an exploratory paper. Review their "
            "original responses, including missing/invalid responses. Do not "
            "invent expertise or approvals. No private confirmatory sample has been "
            "opened. The author ALONE makes the final decision. Summarise the "
            "actual reviewer objections and disagreements; classify only what is "
            "eligible for further exploratory scientific review. "
            "RETURN exactly one JSON object with keys: "
            "advisory_recommendation (support_exploratory_review | major_revision | "
            "reject_scientific_claim | abstain_unverifiable), "
            "critical_objections (list of strings), minority_positions (list of strings), "
            "required_repairs (list of strings), "
            "confidence_caveat (string), author_final_decision (null), "
            "human_independent_review_completed (false), "
            "confirmatory_validated (false). "
            "Never mark the publication or scientific validation completed.\n"
            "PAPER_SHA256: "+manuscript_sha+"\nPANEL:\n"+
            json.dumps(panel,sort_keys=True,ensure_ascii=False))


def run(config_path:Path,out:Path,secret:str,transport=None):
    require(bool(secret),"OPENROUTER_KEY_UNAVAILABLE")
    require(not(out.exists() and any(out.iterdir())),"ORIGINAL_EVIDENCE_ALREADY_EXISTS")
    cfg,config_bytes,ledger,receipts,items=prompts(config_path)
    manuscript=(ROOT/cfg["manuscript"]).read_text()
    manifest={
        "classification":"FOUR_PROVIDER_INDEPENDENT_AI_ADVISORY_ONLY",
        "manuscript_sha256":digest(manuscript.encode()),
        "config_sha256":digest(config_bytes),
        "claim_ledger_sha256":digest((ROOT/cfg["claim_ledger"]).read_bytes()),
        "selected_source_sha256":{k:x["source_sha256"] for k,x in receipts.items()},
        "reviewers":cfg["reviewers"],"chair":cfg["chair"],"planned_calls":5,
        "author_final_decision":None,"independent_human_reviewers":0,
        "protected_holdout_touched":False,"confirmatory_executed":False,
        "scientifically_approved":False,"journal_submitted":False,
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "git_sha":os.environ.get("GITHUB_SHA")
    }
    out.mkdir(parents=True,exist_ok=True)
    save(out/"metadata.json",manifest)
    client=OpenRouter(secret,out/"provider_ledger.json",cfg["max_calls"],transport)
    records=[]
    ids=set()
    for role,prompt,selected in items:
        item={"reviewer_id":role["id"],"requested_model":role["model"],
              "prompt_sha256":digest(prompt.encode()),
              "selected_claim_ids":[x["source_id"] for x in selected],
              "response_id":None,"review":None,"error":None,
              "is_human_reviewer":False}
        try:
            result=client.call(role["model"],prompt,cfg["review_max_tokens"])
            item.update({
                "response_id":result["response_id"],
                "observed_model":result["observed_model"],
                "usage":result["usage"],"finish_reason":result["finish_reason"],
                "original_response_text":result["text"]
            })
            require(result["response_id"] not in ids,"DUPLICATE_PROVIDER_RESPONSE")
            ids.add(result["response_id"])
            item["review"]=interpret(result["text"],selected,manuscript)
        except (BenchmarkError,ValueError) as exc:
            item["error"]=str(exc)[:200]
        records.append(item)
        save(out/"original_independent_reviews.json",records)
        print(role["id"],"VALID" if item["review"] else "MISSING_OR_INVALID",flush=True)
    chairp=chair_prompt(manifest["manuscript_sha256"],records)
    chair={"chair_id":cfg["chair"]["id"],"model":cfg["chair"]["model"],
           "prompt_sha256":digest(chairp.encode()),
           "original_response_text":None,"response_id":None,"decision":None,"error":None}
    try:
        result=client.call(cfg["chair"]["model"],chairp,cfg["chair_max_tokens"])
        chair.update({"original_response_text":result["text"],
                      "response_id":result["response_id"],
                      "observed_model":result["observed_model"],
                      "usage":result["usage"]})
        require(result["response_id"] not in ids,"DUPLICATE_PROVIDER_RESPONSE")
        ids.add(result["response_id"])
        from scripts.p07b_detached_panel_audit import remove_exact_envelope
        raw,_=remove_exact_envelope(result["text"])
        decision=json.loads(raw)
        require(isinstance(decision,dict) and set(decision)=={
            "advisory_recommendation","critical_objections","minority_positions",
            "required_repairs","confidence_caveat","author_final_decision",
            "human_independent_review_completed","confirmatory_validated"},
            "CHAIR_SCHEMA_INVALID")
        require(decision["advisory_recommendation"] in ALLOWED
                and decision["author_final_decision"] is None
                and decision["human_independent_review_completed"] is False
                and decision["confirmatory_validated"] is False,
                "CHAIR_FALSE_SCIENTIFIC_PROMOTION")
        for key in ("critical_objections","minority_positions","required_repairs"):
            require(isinstance(decision[key],list) and len(decision[key])<=25
                    and all(isinstance(x,str) for x in decision[key]),"CHAIR_INVALID_LIST")
        require(isinstance(decision["confidence_caveat"],str),"CHAIR_INVALID_CONFIDENCE")
        chair["decision"]=decision
    except (BenchmarkError,ValueError) as exc:
        chair["error"]=str(exc)[:200]
    save(out/"original_ai_chair.json",chair)
    summary={
        "status":"AI_ADVISORY_COMPLETE_FOR_AUTHOR_REVIEW" if all(
            r["review"] is not None for r in records) and chair["decision"] is not None
            else "AI_ADVISORY_PARTIAL_UNVERIFIED_RESPONSES",
        "number_of_reviewers_expected":4,
        "number_of_reviewers_valid":sum(r["review"] is not None for r in records),
        "chair_valid":chair["decision"] is not None,
        "votes_by_recommendation":dict(Counter(
            r["review"]["recommendation"] for r in records if r["review"])),
        "advisory_only":True,"author_final_decision":None,
        "human_independent_scientific_reviewers":0,
        "confirmatory_validated":False,
        "scientifically_approved":False,
        "journal_submitted":False,
        "heldout_private_sample_touched":False
    }
    save(out/"summary.json",summary)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "author_final_decision":None,"human_experts":0,
        "confirmatory_validated":False,"scientifically_approved":False})
    print(json.dumps(summary,indent=2),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=ROOT/"protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if not a.execute:
        p.error("Use --execute for the five finite OpenRouter requests")
    result=run(a.config,a.out,os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    return 0 if result["status"]=="AI_ADVISORY_COMPLETE_FOR_AUTHOR_REVIEW" else 3


if __name__=="__main__":
    raise SystemExit(main())
