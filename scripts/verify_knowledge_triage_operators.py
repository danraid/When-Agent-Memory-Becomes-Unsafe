#!/usr/bin/env python3
"""Bounded offline, unmodified pinned upstream Knowledge Triage operator integration checks.

Component coverage is not official full-framework, classifier cascade or paper replication.
No model, holdout, oracle feedback, external data or paid calls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from scripts.audit_upstream_typecompact import _load_upstream, PIN

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(upstream: Path):
    kb_mod, op, classifier = _load_upstream(upstream)
    K = classifier.KnowledgeType
    I = kb_mod.Item
    KB = kb_mod.KnowledgeBase
    # The test uses source-exposed labels on purpose, not the model classifier.
    constraint = I(text="Do not approve category travel before signed authorisation.", type=K.CONSTRAINT,
                   topic="travel", scope=("travel",), source="fixture-authored")
    irrelevant = [I(text="Operational report %d" % j, type=K.BELIEF,
                    topic="travel", source="fixture-authored") for j in range(4)]
    items = [constraint] + irrelevant
    original = KB(items=items)
    safe, status = op.type_compact(original, budget=512)
    assert status == "ok" and constraint in safe.items
    unsafe, unsafe_status = op.type_compact(original, budget=1)
    assert unsafe_status == "COMPACTION_UNSAFE"
    assert unsafe.total_tokens > 1, "An unsafe budget must not be reported as compliant"
    # Official implementation is not modified. Record measurable overflow.
    partitions = op.type_decompose(original, partition_budget=24)
    assert partitions
    copies = [p for p in partitions if any(i.topic == "travel" for i in p.items)]
    locality_ok = all(constraint in p.items for p in copies)
    assert locality_ok
    overflow_partitions = sum(p.tokens > 24 for p in partitions)
    relevance = lambda q, i: 100.0 if i.type != K.CONSTRAINT else 0.0
    in_scope = lambda q, i: i.type == K.CONSTRAINT and q == "travel"
    retrieved = op.type_retrieve(items, "travel", 3, relevance, in_scope)
    assert retrieved and retrieved[0] is constraint
    # Explicit corner case: k smaller than number of in-scope constraints.
    c2 = I(text="Must not release pending authorised revocation.", type=K.CONSTRAINT,
           topic="travel", scope=("travel",), source="fixture-authored")
    saturated = op.type_retrieve([constraint, c2], "travel", 1, relevance, in_scope)
    assert len(saturated) == 1
    # If k < number of constraints, official code truncates. Not a retention guarantee.
    return {
        "classification": "OFFLINE_PINNED_UPSTREAM_OPERATOR_COMPONENT_INTEGRATION_NOT_FRAMEWORK_REPLICATION",
        "upstream_commit": PIN, "official_modules_unmodified": True,
        "module_sha256": {name: sha(upstream/"knowledge_triage"/(name+".py"))
                          for name in ("classifier","kb","operators")},
        "typecompact_sufficient_budget_status": status,
        "typecompact_overflow_status": unsafe_status,
        "typecompact_overflow_actual_estimated_tokens": unsafe.total_tokens,
        "typedecompose_partition_count": len(partitions),
        "typedecompose_constraint_locality_ok": locality_ok,
        "typedecompose_budget_exceeding_partition_count": overflow_partitions,
        "typeretrieve_priority_constraint_first": True,
        "typeretrieve_k_less_than_constraint_count": True,
        "typeretrieve_retained_constraints_when_k_1_of_2": len(saturated),
        "official_classifier_cascade_executed": False,
        "downstream_gpt_executed": False,
        "naturalistic_data_executed": False,
        "holdout_touched": False,
        "scientific_approval": False,
        "limitations": [
            "Source-labelled test items bypass the upstream automatic classification.",
            "TypeDecompose may overrun token budget when constraints are replicated.",
            "TypeRetrieve k truncation prevents unlimited pinning of constraints.",
            "A full original-framework baseline needs upstream cascade and downstream decisions."
        ]
    }

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a=p.parse_args()
    report=run(a.upstream)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
