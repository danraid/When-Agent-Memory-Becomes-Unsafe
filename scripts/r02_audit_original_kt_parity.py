"""R02: conservative coverage audit of the published Knowledge Triage comparator.

This audits declared method coverage and source-controlled components.  It does
not run the authors' embedding endpoint, LLM cascade or paid experiment.
"""
from __future__ import annotations
import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIREMENTS=ROOT/"protocol/KNOWLEDGE_TRIAGE_REPLICATION_REQUIREMENTS.md"
PREFLIGHT=ROOT/"scripts/p08_full_original_knowledge_triage_preflight.py"
COMPONENT=ROOT/"scripts/p07b_knowledge_triage_comparator.py"

METHODS={
    "original_pinned_source":"SOURCE_PINNED",
    "original_regex_classifier":"COMPONENT_EXERCISED",
    "original_typecompact":"COMPONENT_EXERCISED",
    "original_typedecompose":"COMPONENT_EXERCISED",
    "original_typeretrieve":"COMPONENT_EXERCISED_WITH_LEXICAL_ADAPTER",
    "original_embedding_model":"NOT_EXECUTED",
    "original_gpt_cascade":"NOT_EXECUTED",
    "original_safety_margin":"NOT_EXECUTED",
    "original_retrieval_evaluation":"NOT_REPRODUCED",
    "published_corpus_and_budgets":"NOT_REPRODUCED",
    "matched_information_downstream_decisions":"NOT_REPRODUCED",
}
UNSUPPORTED={"NOT_EXECUTED","NOT_REPRODUCED","COMPONENT_EXERCISED_WITH_LEXICAL_ADAPTER"}


def assess(root:Path=ROOT) -> dict:
    files=[root/p.relative_to(ROOT) for p in (REQUIREMENTS,PREFLIGHT,COMPONENT)]
    if not all(p.is_file() for p in files):
        raise ValueError("R02_SOURCE_OR_SPEC_MISSING")
    spec, preflight, component=(p.read_text(encoding="utf-8") for p in files)
    if not all(t in preflight for t in ("octen-embedding-8b","gpt-5.4-mini",
                                       "original_full_cascade_executed",
                                       "original_paper_corpus_equivalent",
                                       "original_downstream_behaviour_parity")):
        raise ValueError("R02_ORIGINAL_METHOD_PREFLIGHT_CHANGED")
    if not all(t in component for t in ("type_compact","type_decompose",
                                        "type_retrieve","WAMBU_LEXICAL_AND_TOPIC_ADAPTER",
                                        "full_original_knowledge_triage_replication")):
        raise ValueError("R02_COMPONENT_CLAIM_BOUNDARY_CHANGED")
    if not all(t in spec for t in ("COMPACTION_UNSAFE","ADAPTED_NOT_OFFICIAL_REPRODUCTION",
                                   "Original upstream native classifier")):
        raise ValueError("R02_REPLICATION_SPEC_CHANGED")
    missing=[k for k,v in METHODS.items() if v in UNSUPPORTED]
    return {
      "schema":"WAMBU-R02-ORIGINAL-KT-PARITY-MATRIX-V1",
      "classification":"OFFLINE_METHOD_COVERAGE_AUDIT_NOT_FULL_KT_REPRODUCTION",
      "source_file_sha256":{str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in files},
      "method_states":METHODS,
      "missing_or_adapted_methods":missing,
      "strict_original_model_identity_required":{
        "encoder":"octen-embedding-8b","adjudicator":"gpt-5.4-mini"},
      "source_annotated_is_not_native":True,
      "article_typed_archive_is_not_original":True,
      "unsafe_compactions_are_failures":True,
      "full_original_knowledge_triage_replication":False,
      "original_embedding_runtime_verified":False,
      "original_cascade_executed":False,
      "matched_source_budget_evaluation_executed":False,
      "new_model_calls":0,
      "protected_holdout_touched":False,
      "external_submission_authorised":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=assess()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"classification":report["classification"],
          "missing_or_adapted_methods":len(report["missing_or_adapted_methods"]),
          "full_replication":report["full_original_knowledge_triage_replication"]},indent=2))


if __name__=="__main__":
    main()
