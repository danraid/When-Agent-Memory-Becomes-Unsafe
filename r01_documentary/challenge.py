"""Real R01 documentary authority probes; no operational action correctness gold.

Only original public source snippets and time-stamped, case-linked materials
are allowed in the model packet. The answer/reference field is separate.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"fixtures/R01_REAL_DOCUMENTARY_TEMPORAL_CHALLENGE_V1.json"
PRIMARY=ROOT/"evidence/R01_OPERATIONAL_AUTHORITY_5_CASES_2026-11-19.json"
ALLOWED=("grant_supported","not_established")


def stamp(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))


def validated():
    doc=json.loads(FIXTURE.read_text())
    primary=json.loads(PRIMARY.read_text())
    if doc.get("schema")!="WAMBU-R01-REAL-DOCUMENTARY-TEMPORAL-CHALLENGE-V1":
        raise ValueError("INVALID_R01_FIXTURE_SCHEMA")
    if primary.get("scope_qualified")!=1 or primary.get("fully_independent_correct_operational_actions")!=0:
        raise ValueError("SOURCE_QUALIFICATION_DRIFT")
    cases={x["id"]:x for x in primary["cases"]}
    if set(cases)!={"P07D-CODE-001","P07D-CODE-002","P07D-CODE-003",
                   "P07D-CODE-004","P07D-CODE-008"}:
        raise ValueError("INVALID_ORIGINAL_CASE_IDENTITY")
    sources={x["id"]:x for x in doc["sources"]}
    if len(sources)!=len(doc["sources"]) or len(doc["tasks"])!=12:
        raise ValueError("INVALID_SOURCE_OR_TASK_CARDINALITY")
    if len({x["id"] for x in doc["tasks"]})!=12:
        raise ValueError("DUPLICATE_TASK_ID")
    for task in doc["tasks"]:
        if task["case_id"] not in cases or task["reference_documentary_state"] not in ALLOWED:
            raise ValueError("INVALID_CASE_OR_REFERENCE")
        if task["reference_label_visible_to_model"] is not False:
            raise ValueError("ANSWER_LEAKAGE_FLAG")
    return doc,primary


def sources_for(task,doc,primary):
    case={x["id"]:x for x in primary["cases"]}[task["case_id"]]
    allowed={
      "P07D-CODE-001":{"SC_REQUEST_288","SC_DECISION_288","WG_RECOMMENDATION_59","CPY_PR_133080"},
      "P07D-CODE-002":{"AST_PR_140345","AST_REVIEW_140344","AST_AUTHOR_140344"},
      "P07D-CODE-003":{"UNICODE_PR_130697"},
      "P07D-CODE-004":{"INSPECT_PR_112639"},
      "P07D-CODE-008":{"GLOBALS_PR_133654"},
    }[task["case_id"]]
    items=[x for x in doc["sources"] if x["id"] in allowed
           and stamp(x["created"])<=stamp(task["decision_at"])]
    policy={
       "id":"PEP387_AT_PREDECISION",
       "created":case["policy_commit_at"],
       "url":f"https://github.com/python/peps/blob/{case['policy_sha']}/peps/pep-0387.rst",
       "authority":"normative_general_process",
       "text":"PEP 387 provides a warning-oriented backwards compatibility process; an exception needs Steering Council approval, not a general developer recommendation.",
       "scope":[],
       "sha":case["policy_sha"]
    }
    if stamp(policy["created"])>stamp(task["decision_at"]):
        raise ValueError("FUTURE_POLICY_SNAPSHOT")
    return sorted([*items,policy],key=lambda x:(x["created"],x["id"]))


def prompt_for(task,doc,primary):
    evidence=sources_for(task,doc,primary)
    packet=[{k:r[k] for k in ("id","created","authority","text","url","scope") if k in r}
            for r in evidence]
    body={
       "question":"At the query timestamp, do the supplied PRIMARY source records establish that the Python Steering Council specifically granted an exception to skip the normal deprecation period for the named interface? This is not a request to judge a pull request merge, code quality or safety.",
       "as_of_utc":task["decision_at"],
       "named_interface":task["api"],
       "source_records":packet
    }
    instruction=("You are an evidence-timed policy-documentation analyst. "
       "Judge ONLY whether these supplied records prove a specific Steering Council grant "
       "for the requested interface at the stated time. A mere request, warning recommendation, "
       "discussion draft, PR merge or absent evidence cannot establish a grant. "
       "Answer 'not_established' when sources are insufficient; this does not prove "
       "no grant exists elsewhere. Cite the IDs of actual supplied source records. "
       'Return JSON exactly {"status":"grant_supported"|"not_established",'
       '"evidence_ids":["source_id"],"reason":"brief explanation"}; no Markdown.\n')
    text=instruction+json.dumps(body,ensure_ascii=False,sort_keys=True)
    for needle in ("reference_documentary_state","design_note","correct_action",
                   "evaluator_gold","expected_action"):
        if needle in text:
            raise ValueError("HIDDEN_REFERENCE_LEAKED")
    if any(stamp(x["created"])>stamp(task["decision_at"]) for x in evidence):
        raise ValueError("POST_CUTOFF_EVIDENCE_LEAKED")
    return text,evidence


def grade(task,response,visible):
    ids={x["id"] for x in visible}
    raw=response.strip()
    try:
        data=json.loads(raw)
    except (ValueError,TypeError):
        return {"valid":False,"reason":"INVALID_JSON","status":None,
                "documentary_match":False,"valid_source_ids":False}
    if not isinstance(data,dict):
        return {"valid":False,"reason":"NON_OBJECT_JSON","status":None,
                "documentary_match":False,"valid_source_ids":False}
    valid=(isinstance(data,dict) and
           set(data)=={"status","evidence_ids","reason"} and
           data.get("status") in ALLOWED and isinstance(data.get("evidence_ids"),list)
           and all(type(x) is str for x in data["evidence_ids"]) and
           len(data["evidence_ids"])==len(set(data["evidence_ids"])) and
           isinstance(data.get("reason"),str) and bool(data["reason"].strip()))
    cited=valid and all(i in ids for i in data["evidence_ids"])
    positive=(data.get("status")=="grant_supported")
    # Prevent a unsupported 'grant' from passing merely by guessing the label.
    positive_citations=(not positive) or (
        task["case_id"]=="P07D-CODE-001"
        and {"SC_REQUEST_288","SC_DECISION_288"}.issubset(set(data["evidence_ids"])))
    return {"valid":bool(valid),"status":data.get("status") if valid else None,
            "documentary_match":bool(valid and data["status"]==task["reference_documentary_state"]),
            "valid_source_ids":bool(cited),
            "grant_cites_original_scope_and_decision":bool(positive_citations),
            "unsupported_grant":bool(positive and not positive_citations)}


def build():
    doc,primary=validated()
    return [{"id":t["id"],"case_id":t["case_id"],
             "prompt_sha256":sha256(prompt_for(t,doc,primary)[0].encode()).hexdigest(),
             "source_ids":[x["id"] for x in prompt_for(t,doc,primary)[1]],
             "expected_for_evaluator_only":t["reference_documentary_state"]}
            for t in doc["tasks"]]
