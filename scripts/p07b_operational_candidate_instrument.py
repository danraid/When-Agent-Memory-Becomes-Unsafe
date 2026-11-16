"""P07b sourced *operational candidate* packet, explicitly not naturalistic gold.

Every original PEP/RFC excerpt is verified against a pinned commit+git blob.
Operational requests are STUDY-DRAFTED; effective/observed times, issuer rank,
scope applicability and adjudications are unknown until genuine human review.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scripts.verify_p07_public_sources import git, verify
from scripts.p07b_build_verified_cases import source_span


SPECS = {
    "pep-5-to-387": {
        "request": ("A Python core contributor proposes removing an existing feature "
                    "without an advance warning or deprecation cycle. Assess whether "
                    "the cited backwards-compatibility process permits this change."),
        "anchor": "* Similarly a feature cannot be removed without notice between any two",
        "lines": 2,
        "domain": "python_language_compatibility",
        "operational_scope_to_review": "Python core release compatibility and exceptions",
    },
    "pep-291-to-387": {
        "request": ("A Python 3 standard-library maintainer cites PEP 291 as binding "
                    "compatibility policy for a proposed removal. Assess which document "
                    "has applicable authority for that Python-version scope."),
        "anchor": "* Unless it is going through the deprecation process below, the",
        "lines": 3,
        "domain": "python_stdlib_governance",
        "operational_scope_to_review": "Python 2 versus Python 3 release policy applicability",
    },
    "pep-215-to-292": {
        "request": ("A Python implementation proposal introduces a new dollar-prefixed "
                    "string-literal syntax, claiming it is the mechanism from the "
                    "superseding string-template standard. Evaluate that claim."),
        "anchor": "this because it involves no syntax changes",
        "lines": 2,
        "domain": "python_language_feature_specification",
        "operational_scope_to_review": "language grammar versus library string.Template",
    },
    "pep-631-to-621": {
        "request": ("A Python build backend accepts malformed entries in a "
                    "pyproject.toml project dependencies list. Assess the applicable "
                    "dependency metadata requirements and error behaviour."),
        "anchor": "Each string represents a dependency of the project and MUST be",
        "lines": 2,
        "domain": "python_packaging_metadata",
        "operational_scope_to_review": "PEP 621 metadata and dependency parsing for build backend",
    },
    "rust-rfc-1201-to-2972": {
        "request": ("A Rust compiler patch accepts a naked function marked with an "
                    "inline attribute and a non-assembly function body. Assess whether "
                    "the superseding constrained naked-functions proposal permits it."),
        "anchor": "1. must not specify the",
        "lines": 2,
        "domain": "rust_compiler_feature_specification",
        "operational_scope_to_review": "naked function invariants and implementation status",
    },
    "rust-rfc-1183-to-1974": {
        "request": ("A Rust toolchain patch relies on a previous global-allocator "
                    "override interface in place of the later allocator mechanism. "
                    "Assess applicability, deprecation and release-version constraints."),
        "anchor": "deprecated and eventually removed. The `alloc_system` crate is replaced with the",
        "lines": 2,
        "domain": "rust_global_allocator_api",
        "operational_scope_to_review": "compiler version, stabilisation and allocator interface",
    },
}

CLASSIFICATION = "REAL_EXTERNAL_SOURCE_RESEARCH_DRAFTED_OPERATIONAL_SCENARIOS_NO_GOLD"
SPLIT = "public_development_instrument_draft_only"


def h(data: bytes) -> str:
    return sha256(data).hexdigest()


def quote_lines(source_text: str, anchor: str, count: int) -> dict:
    lines = source_text.splitlines()
    matching = [i for i, line in enumerate(lines) if anchor in line]
    if len(matching) != 1:
        raise ValueError("NORMATIVE_ANCHOR_NOT_UNIQUE_OR_MISSING:" + anchor)
    start = matching[0]
    sample = lines[start:start + count]
    if len(sample) != count or any(not x.strip() for x in sample):
        raise ValueError("NORMATIVE_QUOTE_TRUNCATED")
    excerpt = "\n".join(sample)
    return {
        "line_start_1based": start + 1,
        "line_end_1based": start + count,
        "verbatim_excerpt": excerpt,
        "excerpt_sha256": h(excerpt.encode("utf-8")),
    }


def published_proposal_date(text: str, repo: str) -> str | None:
    if repo == "python/peps":
        m = re.search(r"(?im)^Created:\s*(.+?)\s*$", text)
    else:
        m = re.search(r"(?im)^- Start Date:\s*(.+?)\s*$", text)
    return m.group(1) if m else None


def build(manifest_path: Path, roots: dict[str, Path]) -> tuple[dict,dict,dict]:
    certified = verify(manifest_path, roots)
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    pairs = manifest["paired_documents"]
    if certified["pairs"] != 6 or set(SPECS) != {p["id"] for p in pairs}:
        raise ValueError("P07B_SOURCE_MATRIX_CHANGED")
    cases = []
    source_details = []
    blank_reviews = []
    for index, pair in enumerate(pairs, 1):
        spec = SPECS[pair["id"]]
        rev = pair["revision"]
        root = roots[pair["repository"]]
        src_bytes = git(root, "show", rev + ":" + pair["source_path"])
        dst_bytes = git(root, "show", rev + ":" + pair["target_path"])
        src_text = src_bytes.decode("utf-8")
        dst_text = dst_bytes.decode("utf-8")
        link = source_span(src_text, pair["repository"], pair["target_number"])
        norm = quote_lines(dst_text, spec["anchor"], spec["lines"])
        cid = "P07B-OP-DRAFT-%03d" % index
        documents = []
        for kind, path, data, blob, body in (
            ("source",pair["source_path"],src_bytes,pair["source_blob_sha"],src_text),
            ("target",pair["target_path"],dst_bytes,pair["target_blob_sha"],dst_text),
        ):
            documents.append({
                "source_id": cid + "-" + kind,
                "url": f"https://github.com/{pair['repository']}/blob/{rev}/{path}",
                "repository":pair["repository"],"revision":rev,
                "git_blob_sha1":blob,"sha256":h(data),"source_path":path,
                "document_created_date_as_published":published_proposal_date(body,pair["repository"]),
                "created_date_is_effective_date":False,
                "source_licence_redistribution_review":"PENDING_HUMAN_SOURCE_RIGHTS_CHECK",
            })
        candidate = {
            "case_id":cid,"split":SPLIT,"classification":CLASSIFICATION,
            "origin_document_pair_id":pair["id"],
            "research_authored_request_not_observed_operational_event":True,
            "request":{"text":spec["request"],"domain":spec["domain"]},
            "proposed_scope_requiring_human_confirmation":spec["operational_scope_to_review"],
            "source_documents":documents,
            "events":[
                {"event_id":cid+"-SRC","source_id":documents[0]["source_id"],
                 "issuer":"EXTERNAL_PUBLIC_DOCUMENT_AUTHOR_NOT_POLICY_AUTHORITY_ATTESTED",
                 "created_at":documents[0]["document_created_date_as_published"],
                 "observed_at":None,"effective_at":None,"issuer_rank":None,
                 "scope_applicability":None,
                 "claim":"Original source names replacement",
                 "excerpt_verbatim":link["quoted_line"],
                 "line_start_1based":link["source_line_number"],
                 "quote_sha256":link["quoted_line_sha256"]},
                {"event_id":cid+"-TARGET","source_id":documents[1]["source_id"],
                 "issuer":"EXTERNAL_PUBLIC_DOCUMENT_AUTHOR_NOT_POLICY_AUTHORITY_ATTESTED",
                 "created_at":documents[1]["document_created_date_as_published"],
                 "observed_at":None,"effective_at":None,"issuer_rank":None,
                 "scope_applicability":None,
                 "claim":"Extracted passage from superseding document",
                 "excerpt_verbatim":norm["verbatim_excerpt"],
                 "line_start_1based":norm["line_start_1based"],
                 "line_end_1based":norm["line_end_1based"],
                 "quote_sha256":norm["excerpt_sha256"]},
            ],
            "decision_time":None,
            "real_issuer_hierarchy_validated":False,
            "actual_effective_time_validated":False,
            "actual_observation_time_validated":False,
            "request_scope_validated":False,
            "case_writer_status":"AI_ASSISTED_RESEARCH_DRAFT_NOT_HUMAN_ORIGINAL",
            "case_writer_human_independence_verified":False,
            "adjudication_status":"UNADJUDICATED",
            "ready_for_model_confirmatory_execution":False,
            "missing_authority_ambiguity_requires_abstention_or_exclusion":True,
            "human_authenticity_not_inferred_from_git_hash":True,
        }
        if any(k in candidate for k in ("expected_action","gold_action","reference_action","adjudicated_action")):
            raise ValueError("REFERENCE_LABEL_LEAK_IN_CANDIDATE_CASE")
        cases.append(candidate)
        source_details.append({"case_id":cid,"pair":pair["id"],
                               "original_source_sha256":h(src_bytes),
                               "original_target_sha256":h(dst_bytes),
                               "source_link_line_sha256":link["quoted_line_sha256"],
                               "target_normative_excerpt_sha256":norm["excerpt_sha256"],
                               "document_blob_identity_verified":True,
                               "external_doc_not_naturalistic_case":True})
        blank_reviews.append({
            "case_id":cid,
            "independent_human_case_writer_id":None,
            "independent_human_adjudicator_id":None,
            "reviewer_qualification_verified":False,
            "writer_and_adjudicator_distinct_verified":False,
            "blind_to_model_outputs_attested":False,
            "authentic_scope_and_issuer_trace":None,
            "independently_verified_effective_at":None,
            "independently_verified_observed_at":None,
            "decision_time":None,
            "action":None,
            "reason_and_document_citations":None,
            "disagreement_resolution":None,
            "source_licence_and_privacy_reviewed":False,
            "status":"EMPTY_HUMAN_REVIEW_FORM_NOT_SUBMITTED",
        })
    cases_packet={
        "schema":"WAMBU-P07B-OPERATIONAL-CANDIDATES-V1",
        "classification":CLASSIFICATION,"split":SPLIT,
        "source_manifest_sha256":h(raw_manifest),
        "original_external_document_pairs":6,
        "research_drafted_operational_requests":len(cases),
        "genuine_observed_operational_cases":0,
        "independent_human_adjudications":0,
        "human_qualified_reference_labels":0,
        "cases":cases,"holdout_touched":False,"scientifically_approved":False,
    }
    provenance={
        "schema":"WAMBU-P07B-OP-SOURCE-VERIFICATION-V1",
        "source_manifest_sha256":h(raw_manifest),
        "original_git_provenance_report":certified,
        "verified_case_source_details":source_details,
        "source_verification_complete":True,
        "human_semantic_review_complete":False,
        "operational_authority_validated":False,
        "holdout_touched":False,
    }
    intake={
        "schema":"WAMBU-P07B-EMPTY-HUMAN-REVIEW-INTAKE-V1",
        "classification":"BLANK_REAL_HUMAN_REVIEW_FORMS_NOT_REVIEW",
        "adjudications":blank_reviews,
        "genuine_human_adjudications":0,
        "unfilled_forms":len(blank_reviews),
        "model_predictions_excluded":True,
        "never_promote_to_human_review_automatically":True,
    }
    return cases_packet, provenance, intake


def write_artifacts(out: Path, result: tuple[dict,dict,dict]) -> None:
    if out.exists() and any(out.iterdir()):
        raise ValueError("CANNOT_OVERWRITE_ORIGINAL_CANDIDATE_ARTIFACTS")
    out.mkdir(parents=True,exist_ok=True)
    files = ["candidate_cases_no_gold.json","immutable_source_provenance.json",
             "blank_independent_human_review_forms.json"]
    for name, value in zip(files,result):
        (out/name).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
                              encoding="utf-8")
    (out/"manifest.json").write_text(json.dumps({
        "sha256":{p.name:h(p.read_bytes()) for p in out.glob("*.json") if p.name!="manifest.json"},
        "real_external_documents_verified":True,"operational_gold_qualified":False,
        "human_adjudications":0,"holdout_touched":False,"scientifically_approved":False,
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,default=Path("protocol/P07_PUBLIC_SOURCE_CANDIDATES.json"))
    p.add_argument("--python-peps",type=Path,required=True)
    p.add_argument("--rust-rfcs",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    result=build(a.manifest,{"python/peps":a.python_peps,"rust-lang/rfcs":a.rust_rfcs})
    write_artifacts(a.out,result)
    print(json.dumps({"status":"READY_FOR_GENUINE_INDEPENDENT_HUMAN_INTAKE_NOT_VALIDATED",
        "verified_source_pairs":6,"research_drafted_cases":len(result[0]["cases"]),
        "actual_observed_operational_cases":0,"human_reference_actions":0,
        "confirmatory_touched":False},indent=2))


if __name__=="__main__":
    main()
