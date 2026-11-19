"""R01 documentary source-memory challenge: prospective engineering instrument only.

The SAME complete public retrospective source digest is the input of each
representation. Later items may appear in the digest; the question asks for
the documentary state at a historical time. Therefore this is NOT an actual
at-decision-time naturalistic case. Result labels are documentary sufficiency,
not qualified operational policy actions.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from r01_documentary.challenge import ROOT, validated

PROTOCOL=ROOT/"protocol/R01_RETROSPECTIVE_PROVENANCE_MEMORY_STRESS_V1.json"


def words(s):
    return len(s.split())


def common_feed():
    doc,_=validated()
    records=sorted(doc["sources"],key=lambda x:(x["created"],x["id"]))
    lines=[]
    for x in records:
        scope=", ".join(x["scope"]) if x["scope"] else "unspecified"
        lines.append(f"SOURCE_ID={x['id']} UTC={x['created']} KIND={x['authority']} "
             f"SCOPE={scope} URL={x['url']}\nCONTENT={x['text']}")
    return "\n\n".join(lines)


def deterministic_ledger():
    doc,_=validated()
    records=sorted(doc["sources"],key=lambda x:(x["created"],x["id"]))
    lines=[]
    for r in records:
        scope=",".join(r["scope"]) or "unspecified"
        summary=" ".join(r["text"].split()[:10])
        lines.append(f"{r['id']} {r['created']} {r['authority']} [{scope}] {summary}")
    return "\n".join(lines)


def compaction_prompt():
    feed=common_feed()
    return ("You are constructing an EVIDENCE MEMORY, not deciding whether a request "
      "is authorised. Preserve source IDs, role or issuer, publication times, "
      "exactly named interfaces, requested permissions and limits. "
      "Do not treat reviewer advice, a proposal or a merged PR as a formal Steering Council grant. "
      "Keep source-dependent uncertainty and possible postdated source evidence. "
      "Output a compact plain-text memory of at most 220 whitespace-delimited words. "
      "Do not add facts or omit explicit formal permissions when compressing.\n"
      "RETROSPECTIVE PUBLIC SOURCE DIGEST:\n"+feed)


def bounded_memory(text):
    budget=json.loads(PROTOCOL.read_text())["budgets"]["memory_max_words"]
    if not isinstance(text,str) or not text.strip() or words(text)>budget:
        raise ValueError("MEMORY_BUDGET_EXCEEDED_OR_EMPTY")
    return text


def decision_prompt(task,memory):
    memory=bounded_memory(memory)
    # Neither case_id nor reference_documentary_state are passed to the model.
    query={"as_of_utc":task["decision_at"],"target_interface":task["api"],
           "question":"From the cited evidence memory, was a specific Steering Council grant to skip deprecation for this interface documented before the as-of time?"}
    output=("You are auditing a RETROSPECTIVE source memory, not acting on a live PR. "
      "Treat any events later than as-of as unavailable for the historical judgement. "
      "The answer must concern only explicit named exceptions from the Python Steering Council. "
      "If the memory lacks sufficient authority or scope, return not_established. "
      "Do not treat absence in this memory as proof no exception existed anywhere. "
      "Cite event IDs retained in memory. "
      'Return JSON {"status":"grant_supported"|"not_established",'
      '"evidence_ids":["source_id"],"reason":"brief"}.\n'
      "COMPACT EVIDENCE MEMORY:\n"+memory+
      "\nHISTORICAL AUDIT QUERY:\n"+json.dumps(query,sort_keys=True))
    for forbidden in ("reference_documentary_state","design_note","correct_action","source_case_index"):
        if forbidden in output:
            raise ValueError("HIDDEN_REFERENCE_LEAKAGE")
    return output


def manifest():
    doc,_=validated()
    p=json.loads(PROTOCOL.read_text())
    if p["status"]!="DEVELOPMENT_DESIGNED_NOT_LIVE_QUALIFIED" or p["holdout"] or p["external_submission"]:
        raise ValueError("INVALID_MEMORY_STRESS_PROTOCOL")
    feed=common_feed()
    ledger=bounded_memory(deterministic_ledger())
    out=[]
    for t in doc["tasks"]:
        prompt=decision_prompt(t,ledger)
        out.append({"id":t["id"],"reference_documentary_state_evaluator_only":t["reference_documentary_state"],
                    "digest_source_sha256":sha256(feed.encode()).hexdigest(),
                    "structured_memory_sha256":sha256(ledger.encode()).hexdigest(),
                    "structured_query_sha256":sha256(prompt.encode()).hexdigest()})
    return {"schema":"WAMBU-R01-RETROSPECTIVE-MEMORY-STRESS-PREFLIGHT-V1",
            "common_source_sha256":sha256(feed.encode()).hexdigest(),
            "source_words":words(feed),
            "ledger_words":words(ledger),
            "max_memory_words":p["budgets"]["memory_max_words"],
            "cases":out,"model_calls":0,
            "independent_action_gold":0,
            "retrospective_not_contemporaneous":True,
            "holdout":False,"external_submission":False}
