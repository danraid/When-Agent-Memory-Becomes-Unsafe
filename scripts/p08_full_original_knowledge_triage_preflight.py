"""Source-pinned, fail-closed fidelity gate for the original full Knowledge Triage.

This gate is NOT a replacement implementation. It inspects exact upstream
algorithms, models, credentials and published experimental parity; it refuses to
promote the existing three original components to full methodological parity.
Never logs a credential, triggers a paid request or accesses private holdouts.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess

from scripts.audit_upstream_typecompact import PIN, UPSTREAM

OFFICIAL_MODELS = {
    "embedding": "octen-embedding-8b",
    "cascade_llm": "gpt-5.4-mini",
}
REQUIRED_SOURCES = (
    "knowledge_triage/classifier.py",
    "knowledge_triage/classifier_cascade.py",
    "knowledge_triage/cascade_singleton.py",
    "knowledge_triage/clients.py",
    "knowledge_triage/secrets.py",
    "knowledge_triage/safety_margin.py",
    "knowledge_triage/kb.py",
    "knowledge_triage/operators.py",
    "knowledge_triage/preservation.py",
    "experiments/_helpers.py",
    "pyproject.toml",
    "LICENSE",
)


def require(check, reason):
    if not check:
        raise ValueError(reason)


def assess(upstream:Path, environment:dict|None=None) -> dict:
    env=dict(os.environ if environment is None else environment)
    commit=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                          check=True,capture_output=True,text=True).stdout.strip()
    require(commit==PIN,"NOT_ORIGINAL_PINNED_REVISION")
    files={}
    for name in REQUIRED_SOURCES:
        p=upstream/name
        require(p.is_file(),"UPSTREAM_COMPONENT_MISSING:"+name)
        files[name]=sha256(p.read_bytes()).hexdigest()
    source=(upstream/"knowledge_triage/classifier_cascade.py").read_text()
    singleton=(upstream/"knowledge_triage/cascade_singleton.py").read_text()
    helpers=(upstream/"experiments/_helpers.py").read_text()
    pyproject=(upstream/"pyproject.toml").read_text()
    ops=(upstream/"knowledge_triage/operators.py").read_text()
    licence=(upstream/"LICENSE").read_text()
    require("Apache" in licence,"UPSTREAM_APACHE_LICENCE_NOT_VERIFIED")
    require("octen-embedding-8b" in source and "gpt-5.4-mini" in singleton,
            "ORIGINAL_EMBEDDING_OR_ADJUDICATOR_DIFFERENT")
    require("regex_predict" in source and "EncoderClassifier" in source
            and "llm_adjudicate" in source and "abstain_as_hard" in source,
            "ORIGINAL_CASCADE_STAGES_MISSING")
    require("classify_batch_cached" in singleton and "get_cascade" in singleton,
            "ORIGINAL_CASCADE_ENTRYPOINT_MISSING")
    require("type_compact(" in ops and "type_decompose(" in ops and "type_retrieve(" in ops,
            "ORIGINAL_OPERATOR_METHOD_MISSING")
    require("load_scifact_chunks" in helpers and "embed_batch" in helpers
            and "text-embedding-3-large" in helpers,
            "PUBLISHED_RETRIEVAL_HELPERS_DIFFER")
    require("openai" in pyproject and "numpy" in pyproject,
            "UPSTREAM_DEPENDENCY_FILE_DIFFER")

    # These variables are those the *upstream code* uses. A generic OpenRouter
    # secret does not prove access to the authors' embedding service.
    capabilities={
        "original_embedding_service_key_configured":bool(env.get("CUSTOM_LLM_API_KEY")),
        "original_embedding_service_endpoint_configured":bool(env.get("CUSTOM_LLM_ENDPOINT")),
        "original_gpt_api_key_configured":bool(env.get("OPENAI_API_KEY")),
        "only_openrouter_key_is_not_original_endpoint_evidence":
            bool(env.get("OPENROUTER_API_KEY") or env.get("OPENROUTER")),
    }
    conditions={
        "source_revision_and_code_verified":True,
        "upstream_algorithm_unchanged":True,
        "original_embedding_endpoint_configured":
            capabilities["original_embedding_service_key_configured"] and
            capabilities["original_embedding_service_endpoint_configured"],
        "original_gpt_api_configured":capabilities["original_gpt_api_key_configured"],
        "original_embedding_model_identity_runtime_verified":False,
        "original_llm_model_identity_runtime_verified":False,
        "original_full_cascade_executed":False,
        "original_safety_margin_executed":False,
        "original_paper_corpus_equivalent":False,
        "original_published_budgets_matched":False,
        "original_downstream_behaviour_parity":False,
        "independent_human_reference_actions_available":False,
    }
    blockers=[key for key,ok in conditions.items() if not ok]
    return {
        "schema":"WAMBU-P08-ORIGINAL-KT-FULL-FIDELITY-PREFLIGHT-V1",
        "status":"BLOCKED_FULL_KT_REPLICATION_REQUIREMENTS_NOT_MET",
        "classification":"IMMUTABLE_UPSTREAM_SOURCE_PREFLIGHT_NOT_EXECUTION",
        "upstream_repository":UPSTREAM,
        "upstream_sha":commit,
        "upstream_sources_sha256":files,
        "original_models":OFFICIAL_MODELS,
        "source_derived_retrieval_helper_model":"text-embedding-3-large",
        "capabilities_without_secrets":capabilities,
        "checks":conditions,
        "blocking_requirements":blockers,
        "full_original_knowledge_triage_reproduction":False,
        "authors_original_methods_run_during_this_preflight":False,
        "new_paid_model_calls":0,
        "human_adjudications":0,
        "confirmatory_touched":False,
        "scientifically_approved":False,
        "note":("Source inspection is not model availability verification. "
                "Do not substitute OpenRouter or an alternative embedding/model "
                "and claim author-method identity. Original component evidence "
                "remains valid but does not close this gate."),
    }


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args(argv)
    result=assess(args.upstream)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":result["status"],
        "upstream_sha":result["upstream_sha"],
        "unresolved_requirements":len(result["blocking_requirements"]),
        "model_calls":result["new_paid_model_calls"],
        "human_adjudications":result["human_adjudications"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
