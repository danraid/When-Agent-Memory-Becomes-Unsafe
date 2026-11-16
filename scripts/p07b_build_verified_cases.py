"""P07b public source-backed supersession probes, NOT human policy adjudications.

Reuses the existing exact-commit/blob verifier. The *documents* are genuinely
external; each question/negative control is study-constructed and labeled as such.
Only source-substring evidence enters the model casebook. Evaluator-only links
never enter the model input. No invented effective dates or authority ranks.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scripts.verify_p07_public_sources import git, verify

QUESTION = ("At the specified, pinned Git revision, does the SOURCE document "
            "explicitly identify the TARGET document as superseding it? "
            "Judge only the displayed source excerpt and target identity; "
            "do not infer organisational authority or policy applicability.")
LABELS = ("supported", "not_supported", "insufficient_evidence")
SPLIT = "public_development_source_review_only"


class SourceGateError(ValueError):
    pass


def hash_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def source_span(text: str, repo: str, number: str) -> dict:
    if repo == "python/peps":
        pat = re.compile(r"(?im)^Superseded-By:\s*" + re.escape(number) + r"\s*$")
    elif repo == "rust-lang/rfcs":
        pat = re.compile(r"(?i)superseded\s+by[^\n]{0,120}" + re.escape(number))
    else:
        raise SourceGateError("UNAPPROVED_SOURCE_REPOSITORY")
    m = pat.search(text)
    if m is None:
        raise SourceGateError("MISSING_VERIFIED_SUPERSESSION_SPAN")
    start = text.rfind("\n", 0, m.start()) + 1
    end = text.find("\n", m.end())
    if end < 0:
        end = len(text)
    line = text[start:end].strip()
    # Preserve only the immutable, relevant source line, never rewrite it.
    if not line or len(line) > 300:
        raise SourceGateError("UNBOUNDED_OR_EMPTY_SOURCE_LINE")
    return {"quoted_line": line, "source_line_number": text.count("\n", 0, start) + 1,
            "quoted_line_sha256": hash_bytes(line.encode("utf-8"))}


def target_header(text: str, repo: str, number: str) -> str:
    lines = [s.strip() for s in text.splitlines()[:60] if s.strip()]
    if repo == "python/peps":
        found = next((s for s in lines if re.fullmatch(r"PEP:\s*" + re.escape(number), s, re.I)), None)
        if not found:
            raise SourceGateError("TARGET_PEP_HEADER_INVALID")
    else:
        found = next((s for s in lines if s.startswith("- Feature Name:")), None)
        if not found:
            raise SourceGateError("TARGET_RFC_HEADER_INVALID")
    return found[:200]


def build(manifest_path: Path, roots: dict[str, Path]) -> tuple[dict, dict, dict]:
    checked = verify(manifest_path, roots)
    manifest_raw = manifest_path.read_bytes()
    data = json.loads(manifest_raw)
    if (data.get("split") != SPLIT or
            data.get("status") != "SOURCE_CANDIDATES_NOT_HUMAN_ADJUDICATED" or
            len(data.get("paired_documents", [])) != 6):
        raise SourceGateError("SOURCE_MANIFEST_NOT_P07B_V1")
    samples = []
    by_repo = {}
    for pair in data["paired_documents"]:
        repo, revision = pair["repository"], pair["revision"]
        root = roots[repo]
        src = git(root, "show", f"{revision}:{pair['source_path']}")
        tgt = git(root, "show", f"{revision}:{pair['target_path']}")
        source_text, target_text = src.decode("utf-8"), tgt.decode("utf-8")
        span = source_span(source_text, repo, pair["target_number"])
        header = target_header(target_text, repo, pair["target_number"])
        base = {"manifest_pair_id": pair["id"], "repo": repo, "revision": revision,
                "source_path": pair["source_path"], "source_blob_sha": pair["source_blob_sha"],
                "source_sha256": hash_bytes(src), "source_span": span,
                "target_path": pair["target_path"], "target_blob_sha": pair["target_blob_sha"],
                "target_sha256": hash_bytes(tgt), "target_header": header,
                "target_number": pair["target_number"]}
        samples.append(base)
        by_repo.setdefault(repo, []).append(base)
    expanded = []
    for positive in samples:
        expanded.append((positive, positive, "supported"))
        alternatives = [p for p in by_repo[positive["repo"]]
                        if p["target_number"] != positive["target_number"]]
        if not alternatives:
            raise SourceGateError("UNAVAILABLE_DIFFERENT_TARGET_NEGATIVE_CONTROL")
        # Negative controls pair a real source with a different real target.
        alternative = sorted(alternatives, key=lambda p: p["target_path"])[0]
        expanded.append((positive, alternative, "not_supported"))
    # Deterministic mix before neutral IDs. Never send labels or origin in prompts.
    expanded.sort(key=lambda triple: hash_bytes((
        "P07B-SOURCE-PAIR-CHALLENGE-V1|" + triple[0]["manifest_pair_id"] +
        "|" + triple[1]["target_path"]).encode()))
    cases, sidecar = [], []
    for idx, (base, target, label) in enumerate(expanded, 1):
        cid = f"P07B-SOURCE-{idx:03d}"
        source_url = (f"https://github.com/{base['repo']}/blob/"
                      f"{base['revision']}/{base['source_path']}")
        target_url = (f"https://github.com/{target['repo']}/blob/"
                      f"{target['revision']}/{target['target_path']}")
        case = {
            "case_id": cid, "split": SPLIT, "task_kind": "DOCUMENT_RELATION_ONLY",
            "question": QUESTION,
            "source_document": {"url": source_url, "revision": base["revision"],
                "blob_sha1": base["source_blob_sha"],
                "full_sha256": base["source_sha256"],
                "path": base["source_path"]},
            "target_document": {"url": target_url, "revision": target["revision"],
                "blob_sha1": target["target_blob_sha"],
                "full_sha256": target["target_sha256"],
                "path": target["target_path"]},
            "source_evidence": base["source_span"],
            "target_identity": {"header_exact": target["target_header"],
                                "number": target["target_number"]},
            "label_source": "NONE_IN_MODEL_VISIBLE_CASE",
            "effective_date_verified": False,
            "issuer_precedence_verified": False,
            "operational_action_adjudicated": False,
        }
        cases.append(case)
        sidecar.append({"case_id": cid, "source_pair": base["manifest_pair_id"],
                        "reference_link_status_from_verified_text": label,
                        "reference_kind": "DETERMINISTIC_DOCUMENT_LINK_NOT_HUMAN_GOLD",
                        "source_span_sha256": base["source_span"]["quoted_line_sha256"],
                        "constructed_question_not_observed_action": True,
                        "human_adjudication": False})
    result = {
        "schema": "P07B-PUBLIC-SOURCE-SUPERSESSION-CASES-V1",
        "classification": "VERIFIABLE_REAL_DOCUMENTS_STUDY_CONSTRUCTED_QUESTIONS",
        "split": SPLIT,
        "cases": cases,
        "source_manifest_sha256": hash_bytes(manifest_raw),
        "provenance_verifier_status": checked["status"],
        "real_document_pairs": 6,
        "derived_question_cases": 12,
        "independent_human_adjudications": 0,
        "true_naturalistic_operational_cases": 0,
        "protected_holdout_touched": False,
    }
    reference = {
        "schema": "P07B-EVALUATOR-ONLY-SUPERSESSION-LINK-SIDECAR-V1",
        "labels_not_model_visible": True, "human_gold": False,
        "constructed_controls": True, "references": sidecar,
        "scientific_approval": False,
    }
    provenance = {
        "schema": "P07B-PUBLIC-IMMUTABLE-SOURCE-PROVENANCE-V1",
        "source_manifest_sha256": hash_bytes(manifest_raw),
        "verified": checked, "cases": len(cases),
        "source_records": [{k: v for k, v in s.items() if k != "source_span"}
                           for s in samples],
        "source_span_hashes": {
            s["manifest_pair_id"]: s["source_span"]["quoted_line_sha256"] for s in samples},
        "all_sources_original": True, "all_questions_study_constructed": True,
        "human_adjudications": 0, "confirmatory_touched": False,
    }
    if any(any(k in c for k in ("gold_action", "expected_action",
                                "adjudicated_action", "reference_link_status_from_verified_text"))
           for c in cases):
        raise SourceGateError("MODEL_INPUT_REFERENCE_LABEL_LEAK")
    return result, reference, provenance


def save(out: Path, values: tuple[dict,dict,dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    names = ("source_cases_public.json", "reference_sidecar_evaluator_only.json",
             "source_provenance.json")
    for name, data in zip(names, values):
        (out/name).write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
                              + "\n", encoding="utf-8")
    (out/"source_manifest.json").write_text(json.dumps({
        "schema": "P07B-SOURCE-EVIDENCE-HASHES-V1",
        "files_sha256": {p.name: hash_bytes(p.read_bytes())
                         for p in sorted(out.glob("*.json")) if p.name != "source_manifest.json"},
        "human_reference": False, "source_provenance_verified": True,
        "confirmatory_touched": False}, indent=2) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path,
                   default=Path("protocol/P07_PUBLIC_SOURCE_CANDIDATES.json"))
    p.add_argument("--python-peps", type=Path, required=True)
    p.add_argument("--rust-rfcs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = build(args.manifest, {"python/peps": args.python_peps,
                                    "rust-lang/rfcs": args.rust_rfcs})
    save(args.out, result)
    print(json.dumps({"verified_document_pairs": 6, "constructed_cases": 12,
                      "human_adjudications": 0,
                      "status": "P07B_SOURCE_DOCUMENTS_VERIFIED_AI_REVIEW_READY"}))


if __name__ == "__main__":
    main()
