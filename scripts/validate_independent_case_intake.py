#!/usr/bin/env python3
"""P07b independent case intake: validate *structure*, not reviewer authenticity.

No paid model calls, no confirmatory seed access. All inputs are development-only.
A passing schema check is never scientific approval or human identity verification.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_CASE=("case_id","split","source_documents","events","request","decision_time","writer_id","writer_declaration")
REQUIRED_EVENT=("event_id","source_id","issuer","issued_at","effective_at","scope","rule","supersedes")
REQUIRED_SOURCE=("source_id","url","revision","sha256","licence")
REQUIRED_REVIEW=("case_id","adjudicator_id","independence_declaration","action","reason","evidence_event_ids","reviewed_at")
ACTIONS={"approve","reject","abstain"}

def validate(casebook, reviews, allow_simulation=False):
    errors=[]
    if not allow_simulation and (casebook.get("simulation_only") or reviews.get("simulation_only")):
        errors.append("fictional simulation is not genuine independent human adjudication")
    cases=casebook.get("cases",[])
    decisions=reviews.get("adjudications",[])
    if not isinstance(cases,list) or not isinstance(decisions,list):
        return ["cases and adjudications must be arrays"]
    seen=set()
    by_id={}
    for i,c in enumerate(cases):
        prefix=f"case[{i}]"
        for k in REQUIRED_CASE:
            if not c.get(k):errors.append(f"{prefix}: missing {k}")
        if not allow_simulation and (c.get("simulation_only") or c.get("fictional_roleplay")):
            errors.append(f"{prefix}: fictional case cannot count as human case")
        cid=c.get("case_id")
        if cid in seen:errors.append(f"{prefix}: duplicate case_id")
        seen.add(cid);by_id[cid]=c
        if c.get("split")!="development":
            errors.append(f"{prefix}: only development cases permitted")
        if "expected_action" in c or "gold_action" in c or "adjudicated_action" in c:
            errors.append(f"{prefix}: reference label must not be embedded in casebook")
        if not isinstance(c.get("events"),list) or not c.get("events"):
            errors.append(f"{prefix}: events required");continue
        source_ids=set()
        for j,s in enumerate(c.get("source_documents",[])):
            for k in REQUIRED_SOURCE:
                if not s.get(k):errors.append(f"{prefix}: source[{j}] missing {k}")
            source_ids.add(s.get("source_id"))
        event_ids=set()
        for j,e in enumerate(c["events"]):
            for k in REQUIRED_EVENT:
                if k not in e or e[k] is None or (isinstance(e[k],str) and not e[k].strip()):
                    errors.append(f"{prefix}: event[{j}] missing {k}")
            if e.get("source_id") not in source_ids:errors.append(f"{prefix}: unknown source_id")
            if e.get("event_id") in event_ids:errors.append(f"{prefix}: duplicate event_id")
            event_ids.add(e.get("event_id"))
        if not c.get("writer_declaration",{}).get("independent_of_target_model_outputs",False):
            errors.append(f"{prefix}: case writer independence declaration absent")
    reviewed=set()
    for i,d in enumerate(decisions):
        prefix=f"adjudication[{i}]"
        for k in REQUIRED_REVIEW:
            if k not in d or d[k] is None or d[k]=="":errors.append(f"{prefix}: missing {k}")
        if not allow_simulation and (d.get("simulation_only") or d.get("fictional_roleplay")):
            errors.append(f"{prefix}: fictional adjudication cannot count as human review")
        cid=d.get("case_id")
        if cid not in by_id:
            errors.append(f"{prefix}: case not in casebook");continue
        if cid in reviewed:errors.append(f"{prefix}: duplicate adjudication")
        reviewed.add(cid)
        c=by_id[cid]
        if d.get("adjudicator_id")==c.get("writer_id"):
            errors.append(f"{prefix}: writer cannot adjudicate own case")
        if d.get("action") not in ACTIONS:errors.append(f"{prefix}: invalid action")
        decl=d.get("independence_declaration") or {}
        if not isinstance(decl,dict) or not all(decl.get(k) is True for k in
                ("not_case_writer","blind_to_model_outputs","conflict_checked")):
            errors.append(f"{prefix}: incomplete independence declaration")
        valid={e.get("event_id") for e in c.get("events",[])}
        if not isinstance(d.get("evidence_event_ids"),list) or not d.get("evidence_event_ids"):
            errors.append(f"{prefix}: evidence_event_ids must be nonempty")
        elif not set(d["evidence_event_ids"])<=valid:
            errors.append(f"{prefix}: reference cites missing events")
        if d.get("action")=="abstain" and not d.get("ambiguity_basis"):
            errors.append(f"{prefix}: abstain needs ambiguity_basis")
    if cases and len(reviewed)<len(cases):
        errors.append("not every case has an independent adjudication")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True,type=Path)
    p.add_argument("--reviews",required=True,type=Path)
    p.add_argument("--allow-simulation",action="store_true",help="Validate only fictional fixture structure; never authentic human review")
    args=p.parse_args()
    cases=json.loads(args.cases.read_text(encoding="utf-8"))
    reviews=json.loads(args.reviews.read_text(encoding="utf-8"))
    errors=validate(cases,reviews,allow_simulation=args.allow_simulation)
    print(json.dumps({"status":("FICTIONAL_STRUCTURE_ONLY_PASS" if args.allow_simulation else "STRUCTURE_ONLY_PASS") if not errors else "BLOCKED",
                      "case_count":len(cases.get("cases",[])),
                      "review_count":len(reviews.get("adjudications",[])),
                      "human_identity_verified":False,"scientific_approval":False,
                      "confirmatory_touched":False,"errors":errors},indent=2))
    return 0 if not errors else 1

if __name__=="__main__":
    raise SystemExit(main())
