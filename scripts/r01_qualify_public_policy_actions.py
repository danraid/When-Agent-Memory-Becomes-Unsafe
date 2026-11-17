"""R01: fail-closed qualification of real development cases, never simulated gold.

All classifications derive from already archived source-identity and historical
scope metadata. Missing contemporary issuer/effective/exception evidence blocks
admission to an operational policy-action benchmark.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[1]
TRIAGE=ROOT/"protocol/P07E_HISTORICAL_SCOPE_TRIAGE.json"
CASES=ROOT/"protocol/P07D_REAL_CODE_CHANGE_MATRIX.json"
VALID_TOPIC={"DIRECT_POLICY_TOPIC","LATER_RULE_NOT_ADOPTED_AS_OF_CASE",
             "NONMATCHING_RULE_SCOPE","ADJACENT_BUT_NO_VERIFIED_NORMATIVE_CLAUSE"}
REQUIRED_AUTHORITY=("issuer","rule","published_at","effective_at","scope","exceptions",
                    "source_revision","source_sha256","evidence_url")
ACTIONS={"approve","reject","abstain"}


def inspect(triage_path:Path=TRIAGE,cases_path:Path=CASES,authorities=None):
    t=json.loads(triage_path.read_text(encoding="utf-8"))
    c=json.loads(cases_path.read_text(encoding="utf-8"))
    if t.get("schema")!="WAMBU-P07E-CASE-SCOPE-TRIAGE-V1" or c.get("schema")!="WAMBU-P07D-REAL-CODE-CHANGE-CASES-V1":
        raise ValueError("R01_INVALID_SOURCE_MATRIX")
    by_id={x["id"]:x for x in c["cases"]}
    tags={x["id"]:x for x in t["cases"]}
    if len(tags)!=8 or set(tags)!=set(by_id) or len(c["cases"])!=8:
        raise ValueError("R01_IDENTITY_OR_CARDINALITY_DRIFT")
    authorities={} if authorities is None else authorities
    if set(authorities)-set(tags):
        raise ValueError("R01_UNKNOWN_AUTHORITY_CASE")
    rows=[]
    for case_id in sorted(tags):
        tag=tags[case_id]
        if tag["scope_tag"] not in VALID_TOPIC:
            raise ValueError("R01_UNKNOWN_HISTORICAL_TOPIC_TAG")
        entry=authorities.get(case_id)
        verified=False
        reason="NO_VERIFIED_CONTEMPORANEOUS_AUTHORITY_AND_ACTION"
        if entry is not None:
            # This check is intentionally *structural only*: external identity,
            # sources, time and adoption must still be audited independently.
            if not isinstance(entry,dict) or not all(entry.get(k) for k in REQUIRED_AUTHORITY):
                reason="INCOMPLETE_AUTHORITY_EVIDENCE"
            elif entry.get("independently_source_verified") is not True:
                reason="SOURCE_IDENTITY_NOT_INDEPENDENTLY_VERIFIED"
            elif entry.get("policy_in_force_at_decision") is not True:
                reason="POLICY_EFFECTIVE_TIME_NOT_PROVEN"
            elif entry.get("actor_permission_verified") is not True:
                reason="ACTOR_PERMISSION_NOT_PROVEN"
            elif entry.get("decision_action") not in ACTIONS:
                reason="NO_ACTION_OR_EXPLICIT_ABSTENTION"
            elif not entry.get("adjudication_provenance"):
                reason="NO_ADJUDICATION_PROVENANCE"
            else:
                # Even fully populated self-reported evidence is not equivalent
                # to independently checked truth; do not promote automatically.
                reason="STRUCTURE_COMPLETE_AWAITING_INDEPENDENT_EVIDENCE_AUDIT"
        rows.append({
            "case_id":case_id,
            "public_pr_url":f"https://github.com/{by_id[case_id]['repository']}/pull/{by_id[case_id]['pr']}",
            "normative_source_key":by_id[case_id]["normative"],
            "documentary_screen":tag["scope_tag"],
            "direct_topic_candidate":tag["scope_tag"]=="DIRECT_POLICY_TOPIC",
            "historical_source": "P07E_SOURCE_HISTORY_NOT_POLICY_ADOPTION_PROOF",
            "operational_admission":"BLOCKED_NO_INDEPENDENT_ACTION_GOLD",
            "admission_reason":reason,
            "correct_action":None,
            "human_adjudicator_count":0,
            "ai_role_votes_not_gold":True,
            "workflow_merge_status_not_gold":True,
            "confirmatory_eligible":False,
        })
    if sum(x["direct_topic_candidate"] for x in rows)!=5:
        raise ValueError("R01_HISTORICAL_SCREEN_COUNT_DRIFT")
    result={
        "schema":"WAMBU-R01-AUTHORITY-QUALIFICATION-V1",
        "classification":"REAL_PR_HISTORICAL_SCREEN_NO_AGENT_ACTION_GOLD",
        "source_sha256":{"p07d":sha256(cases_path.read_bytes()).hexdigest(),
                         "p07e":sha256(triage_path.read_bytes()).hexdigest()},
        "case_count":8,"direct_documentary_candidates":5,
        "excluded_current_document_pairs":3,
        "qualified_action_gold":0,"qualified_cases_for_accuracy":0,
        "expert_simulations_not_human":True,
        "human_adjudications":0,"protected_holdout_touched":False,
        "source_evidence_complete":False,"author_final_approval":False,
        "cases":rows}
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    data=inspect()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:data[k] for k in ("case_count","direct_documentary_candidates",
        "excluded_current_document_pairs","qualified_action_gold")},indent=2))


if __name__=="__main__":
    main()
