#!/usr/bin/env python3
"""Detached, reproducible audit of an OpenRouter LongMemEval development artifact.

Consumes only completed (or explicitly failed) *original* artifact contents.
Never makes API calls or infers scientific validation from CI green status.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys


def audit(root: Path) -> dict:
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "run_metadata.json").read_text(encoding="utf-8"))
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    observations = json.loads((root / "observations.json").read_text(encoding="utf-8"))

    files = m["files_sha256"]
    if not files or any(not isinstance(key, str) for key in files):
        raise ValueError("INVALID_MANIFEST")
    for name, expected in files.items():
        target = (root / name).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError("MISSING_OR_TRAVERSING_EVIDENCE")
        if sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError("ORIGINAL_EVIDENCE_DIGEST_MISMATCH:" + name)
    if (m["scientifically_approved"] is not False or
            meta["scientifically_approved"] is not False or
            meta["holdout_touched"] is not False or
            summary["submission_authorized"] is not False):
        raise ValueError("ILLEGAL_SCIENCE_PROMOTION")
    questions = meta["selected_question_ids"]
    models = meta["models"]
    arms = meta["arms"]
    expected = len(questions) * len(models) * len(arms)
    if len(set(questions)) != len(questions) or len(set(models)) != len(models):
        raise ValueError("DUPLICATE_QUESTION_OR_MODEL")
    if len(observations) != expected or summary["expected_answers"] != expected:
        raise ValueError("OBSERVATION_COUNT_MISMATCH")
    allowed = {(q, model, arm) for q in questions for model in models for arm in arms}
    actual = [(r["question_id"], r["model"], r["arm"]) for r in observations]
    if len(set(actual)) != len(actual) or set(actual) != allowed:
        raise ValueError("MISSING_DUPLICATED_OR_UNDECLARED_ARMS")
    observed_scored = sum(r["judge_correct"] is not None for r in observations)
    if observed_scored != summary["scored_answers"]:
        raise ValueError("SCORE_COUNT_MISMATCH")
    errors = Counter(r.get("error") for r in observations if r.get("error"))
    model_summary = {}
    by_key = {(r["question_id"], r["model"], r["arm"]): r for r in observations}
    for model in models:
        model_summary[model] = {}
        for arm in arms:
            rows = [by_key[q, model, arm] for q in questions]
            n = len(rows)
            scored = sum(r["judge_correct"] is not None for r in rows)
            correct = sum(r["judge_correct"] is True for r in rows)
            model_summary[model][arm] = {
                "correct": correct, "scored": scored, "expected": n,
                "coverage": scored / n,
                "accuracy_among_scored": correct / scored if scored else None,
                "conservative_correct_over_expected": correct / n,
                "errors": dict(sorted(Counter(r["error"] for r in rows if r["error"]).items())),
            }
        effects = {}
        for target in arms:
            if target == "full_history":
                continue
            pairs = []
            for q in questions:
                base = by_key[q, model, "full_history"]["judge_correct"]
                alt = by_key[q, model, target]["judge_correct"]
                if base is not None and alt is not None:
                    pairs.append(int(alt) - int(base))
            effects[target + "_minus_full_history"] = {
                "paired_questions_with_both_judged": len(pairs),
                "difference_descriptive_only": sum(pairs) / len(pairs) if pairs else None,
                "missing_pairs": len(questions) - len(pairs),
            }
        model_summary[model]["paired_contrasts"] = effects

    return {
        "classification": "INDEPENDENT_DETACHED_DESCRIPTIVE_AUDIT_NOT_CONFIRMATION",
        "observed_run_status": summary["status"],
        "dataset_sha256": meta["dataset_sha256"],
        "config_sha256": meta["config_sha256"],
        "source_sha256": meta["source_sha256"],
        "benchmark": meta["benchmark"],
        "question_ids": questions,
        "total_expected": expected,
        "total_scored": observed_scored,
        "overall_scored_coverage": observed_scored / expected,
        "observed_errors": dict(sorted(errors.items())),
        "models": model_summary,
        "evidence_files_verified": len(files),
        "recommendation": "DO_NOT_RANK_MODELS_FROM_SIX_CASE_PILOT",
        "original_manifest_sha256": sha256((root / "manifest.json").read_bytes()).hexdigest(),
        "holdout_touched": False,
        "scientifically_approved": False,
        "submission_authorized": False,
        "limits": [
            "Six questions give insufficient statistical power for between-model superiority.",
            "LLM-based answer judge is not human adjudication.",
            "Unequal information access between full/recent/recursive arms.",
            "LongMemEval evaluates Q&A, not unauthorised policy actions.",
            "Unscored answers are availability/coverage failures, not observed wrong model decisions.",
        ],
    }


def as_markdown(a: dict) -> str:
    lines = [
        "# WAMBU-001 | Detached LongMemEval exploratory evidence audit",
        "",
        f"**Original classification:** \`{a['observed_run_status']}\`.",
        f"**Coverage:** {a['total_scored']}/{a['total_expected']} ({a['overall_scored_coverage']:.1%}).",
        f"**Verified input manifest file hashes:** {a['evidence_files_verified']}.",
        "**Science status:** development only; holdout untouched; no p-values or model-superiority claims.",
        "",
        "| Requested model | Full history | Recent window | Recursive summary |",
        "| --- | ---: | ---: | ---: |",
    ]
    for model, groups in a["models"].items():
        vals = []
        for key in ("full_history", "recent_window", "recursive_summary"):
            row = groups[key]
            vals.append(f"{row['correct']}/{row['scored']} judged ({row['scored']}/{row['expected']} coverage)")
        lines.append("| " + model + " | " + " | ".join(vals) + " |")
    lines.extend(["", "## Paired within-model contrasts (descriptive only)", ""])
    for model, groups in a["models"].items():
        lines.append(f"**{model}:**")
        for key, pair in groups["paired_contrasts"].items():
            d = pair["difference_descriptive_only"]
            lines.append(f"- {key}: {d:+.3f}" if d is not None else f"- {key}: unavailable")
            lines[-1] += f" (paired {pair['paired_questions_with_both_judged']}/{a['total_expected']//(len(a['models'])*3)} questions)"
    lines.extend(["", "## Provider/coverage failures", ""])
    for name, n in a["observed_errors"].items():
        lines.append(f"- \`{name}\`: {n}")
    if not a["observed_errors"]:
        lines.append("- No scored-arm provider or judge errors recorded.")
    lines.extend(["", "## Interpretation limits", ""])
    for limit in a["limits"]:
        lines.append("- " + limit)
    lines.append("\nThe audit does not reopen the private confirmatory holdout or certify the manuscript for publication.\n")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    result = audit(args.input)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out / "audit.md").write_text(as_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["observed_run_status"],
                      "coverage": result["overall_scored_coverage"],
                      "verified_files": result["evidence_files_verified"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
