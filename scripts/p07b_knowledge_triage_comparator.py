"""Native original Knowledge Triage *component* comparison on verified P07b excerpts.

Calls author source at exact original git SHA without vendoring/modification.
Does NOT imitate the unreproduced original classifier cascade or present custom
lexical retrieval/scopes as original published benchmark protocols.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from scripts.audit_upstream_typecompact import _load_upstream, PIN, UPSTREAM


def audit(cases_path: Path, reference_path: Path, upstream: Path, out: Path):
    revision = subprocess.run(["git", "-C", str(upstream), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    if revision != PIN:
        raise ValueError("UNPINNED_UPSTREAM_KNOWLEDGE_TRIAGE")
    license_text = (upstream/"LICENSE").read_text(encoding="utf-8")
    if "Apache" not in license_text:
        raise ValueError("SOURCE_LICENSE_UNVERIFIED")
    cases_raw = cases_path.read_bytes()
    data = json.loads(cases_raw)
    if data.get("schema") != "P07B-PUBLIC-SOURCE-SUPERSESSION-CASES-V1" or len(data.get("cases",[])) != 12:
        raise ValueError("INVALID_PUBLIC_SOURCE_CASEBOOK")
    if not reference_path.is_file():
        raise ValueError("MISSING_EVALUATOR_SIDECAR")
    reference = json.loads(reference_path.read_text())
    if len(reference.get("references", [])) != 12:
        raise ValueError("INVALID_SEPARATE_EVALUATOR_SIDECAR")
    kbmod, ops, classifier = _load_upstream(upstream)
    rows = []
    for case in data["cases"]:
        # Only source-visible evidence; *never* include reference labels in the
        # original operators or retrieval.
        lines = [case["source_evidence"]["quoted_line"], case["target_identity"]["header_exact"]]
        kb = kbmod.KnowledgeBase.from_lines(lines, topic="public_document_link",
                                           source=case["source_document"]["url"])
        native_types = [i.type.value for i in kb.items]
        baseline_original = {i.text: i.type.value for i in kb.items}
        for budget in (16, 32, 64):
            compact, status = ops.type_compact(kb, budget)
            if status not in ("ok", "COMPACTION_UNSAFE"):
                raise ValueError("UNKNOWN_UPSTREAM_STATUS")
            partitions = ops.type_decompose(kb, budget)
            violations, total_constraints = ops.constraint_locality_violations(partitions)
            query = "superseded target linked document"
            # Integration glue not from the paper: explicitly named and excluded
            # from any claim of full end-to-end method parity.
            def lexical(q, item):
                return sum(w in item.text.lower() for w in q.lower().split())
            def scope(q, item):
                return item.topic == "public_document_link"
            retrieved = ops.type_retrieve(kb.items, query, 2, lexical, scope)
            control = ops.baseline_retrieve(kb.items, query, 2, lexical)
            constraints = kb.by_type(classifier.KnowledgeType.CONSTRAINT)
            rows.append({
                "case_id": case["case_id"],
                "original_upstream_sha": revision,
                "native_classifier": "knowledge_triage.classifier.classify_instruction",
                "native_classifier_type_per_item": native_types,
                "budget_estimated_tokens": budget,
                "typecompact_status": status,
                "compacted_output_text_sha256": sha256("\n".join(i.text for i in compact.items).encode()).hexdigest(),
                "typecompact_output_estimated_tokens": compact.total_tokens,
                "typecompact_b_min": kb.b_min,
                "typecompact_over_budget": compact.total_tokens > budget,
                "typecompact_source_lines_kept": sum(i.text in [x.text for x in compact.items] for i in kb.items),
                "typedecompose_partitions": len(partitions),
                "typedecompose_over_budget": any(p.tokens > budget for p in partitions),
                "typedecompose_scope_violations": violations,
                "typedecompose_original_constraint_count": total_constraints,
                "typeretrieve_original_constraint_recall_at_2": ops.constraint_recall_at_k(retrieved, constraints),
                "lexical_baseline_constraint_recall_at_2": ops.constraint_recall_at_k(control, constraints),
                "relevance_and_scope_provided_by": "WAMBU_LEXICAL_AND_TOPIC_ADAPTER_NOT_PUBLISHED_EVALUATOR",
                "source_annotated_labels_used": False,
                "reference_labels_passed_to_upstream": False,
            })
    source_sha = {
        p: sha256((upstream/"knowledge_triage"/p).read_bytes()).hexdigest()
        for p in ("classifier.py","kb.py","operators.py",
                  "classifier_cascade.py","cascade_singleton.py","safety_margin.py")
    }
    status = {
        "classification": "SOURCE_PINNED_UNMODIFIED_ORIGINAL_KT_3_OPERATORS_NATIVE_REGEX_ONLY",
        "status": "COMPONENTS_EXECUTED_FULL_PUBLISHED_KT_COMPARATOR_NOT_QUALIFIED",
        "upstream": UPSTREAM, "original_revision": revision,
        "upstream_source_files_sha256": source_sha,
        "upstream_license": "Apache-2.0",
        "public_casebook_sha256": sha256(cases_raw).hexdigest(),
        "cases": len(data["cases"]), "operator_trials": len(rows),
        "operator_methods": ["type_compact","type_decompose","type_retrieve"],
        "typecompact_unsafe_count": sum(r["typecompact_status"]=="COMPACTION_UNSAFE" for r in rows),
        "typecompact_overbudget_count": sum(r["typecompact_over_budget"] for r in rows),
        "typedecompose_overbudget_count": sum(r["typedecompose_over_budget"] for r in rows),
        "native_regex_only": True,
        "original_encoder_executed": False,
        "original_llm_cascade_executed": False,
        "safety_margin_executed": False,
        "paper_dataset_and_model_budget_parity": False,
        "matched_downstream_agent_decisions": False,
        "independent_semantic_reference_available": False,
        "full_original_knowledge_triage_replication": False,
        "human_review_count": 0,
        "model_calls": 0, "confirmatory_touched": False,
        "scientifically_approved": False,
        "limits": [
            "Three unmodified original operators used at exact upstream revision.",
            "Original native regex classifier, NOT the original encoder/LLM cascade.",
            "Research-designed source-excerpt task not the authors' published corpus.",
            "Lexical retrieval relevance and source-topic scope are article adapters.",
            "Original TypeDecompose may produce over-budget partitions; reported as such.",
            "No action labels or genuine human-adjudicated policy decisions exist in this task.",
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    for filename, data_to_save in (("kt_component_report.json",status), ("kt_component_rows.json",rows)):
        (out/filename).write_text(json.dumps(data_to_save, ensure_ascii=False, indent=2, sort_keys=True)+"\n")
    (out/"kt_component_manifest.json").write_text(json.dumps({
        "sha256": {p.name: sha256(p.read_bytes()).hexdigest()
                   for p in out.glob("kt_component_*.json") if p.name!="kt_component_manifest.json"},
        "full_replication": False, "scientifically_approved":False,
    },indent=2)+"\n")
    return status


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True,type=Path)
    p.add_argument("--references",required=True,type=Path)
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    r=audit(args.cases,args.references,args.upstream,args.out)
    print(json.dumps({k:r[k] for k in ("status","cases","operator_trials","full_original_knowledge_triage_replication")},indent=2))


if __name__=="__main__":
    main()
