# WAMBU-001 | Factual v3 pilot postflight | 14 Nov 2026 UTC

**Disposition: LIVE MODEL EXPERIMENT COMPLETE; OVERALL WORKFLOW FAILED AT MODEL ADVISORY.** The recorded model decisions and compactors ran successfully; two reviewer assessments and the generated postflight descriptive report did not complete. No confirmatory evidence and no scientific approval.

## Exact source and artifact

- [GitHub Actions run 43640571248](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248): completed/**failure**, attempt 1, source [5053bd0d5925c91e35d1dc5ff412d0f5c2e625d8](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/commit/5053bd0d5925c91e35d1dc5ff412d0f5c2e625d8).
- [Job 132587017759](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248/job/132587017759): test suite, mock isolation, API preflight and live study steps all succeeded. Reviewer step failed with `article_hub.llm.AdvisoryError: EMPTY_ADVISORY_NO_APPROVAL`. Postflight report step was skipped; artifact upload succeeded.
- [Original GitHub artifact 14131424960](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248/artifacts/14131424960), ZIP SHA-256 independently recomputed from the downloaded original bytes **`4994fa4fdd80412cbd2722f36840d5388c3358aa6dab3759926f44c1134e09f5`** matches GitHub artifact digest and upload job log. ZIP CRC verification: pass. Nine archived paths.
- Internal `empirical/manifest.json`: SHA-256 and byte lengths match exactly for the four listed source evidence payloads: `observations.json`, `compactions.json`, `summary.json` and `status.json`. Recorded prompts match their SHA-256 fields. Final empirical payloads match `.partial.json` snapshots.
- Source code/protocol hashes are stored in the evidence. This is consistency of uploaded evidence, NOT an independent provider-side authentication of each response ID.

## Empirical observations, strictly descriptive

The original artifact records **four pilot episodes of 18 turns**, **432 scored arm observations** (72 x six arms, including 72 derived guard observations), **360 actual GPT decision responses** (five paid arms), **20 real recursive compactions**, **380 distinct successful observed study provider-response IDs**. The final guard arm reuses the ledger-arm original model output and is not an independent GPT call.

| System arm | Correct of 72 | Raw accuracy | Wrongful stale-rule rejections / 16 revocation probes | Missed new enforcement / 16 probes |
| --- | ---: | ---: | ---: | ---: |
| full_history | 72 | 100% | 0/16 | 0/16 |
| recent_window | 52 | 72.22% | 0/16 | 0/16 |
| recursive_summary | 72 | 100% | 0/16 | 0/16 |
| typed_retention_adapted | 72 | 100% | 0/16 | 0/16 |
| temporal_policy_ledger | 72 | 100% | 0/16 | 0/16 |
| temporal_policy_ledger_guard (derived) | 72 | 100% | 0/16 | 0/16 |

Each episode contains **3 primary-eligible post-two-compaction revocation probes**. All four episode-level adapted-typed-minus-ledger risk differences are **0.0000**. A zero difference does not establish statistical equivalence, novelty, or superiority. The recent-window errors occur elsewhere in the cases, not in these two targeted change-probe categories. The synthetic benchmark shows ceiling effects for the principal targeted outcomes and insufficient discrimination for a confirmatory test.

The archived `provider-ledger.json` reports 381 reserved/accounted calls versus 380 successful study-response IDs, consistent with a **single additional unsuccessful advisory call** at the failed review step. Its USD 2.3787141 is conservative reserved accounting, **not the actual provider invoice**. Neither two successful reviews nor completed blinded assessments can be claimed. No reviewer output or final `analysis/report.json` is present in the original ZIP.

## Cause and bounded recovery decision

The blocking exception is **`EMPTY_ADVISORY_NO_APPROVAL`** after the successful paid empirical step; it is **not a failure of the four pilot episodes**. Do NOT rerun the whole paid workflow: that would repeat 380 model calls to correct a review failure. Preserve the original ZIP unchanged; produce a descriptive-only report from the already verified empirical payload, clearly stating `reviewer_calls_completed=0`, using offline tooling only. Later model-advisory execution, if genuinely necessary, must be separately scoped, finite and accepted; automated retry without necessity is excluded. Even repaired reviewers are not peer reviewers.

## Scientific boundary

The upstream method in the live study is **`typed_retention_adapted`**, not the published end-to-end Knowledge Triage. The [independently tested upstream TypeCompact component](../literature/UPSTREAM_TYPECOMPACT_COMPONENT_RESULT_2026-11-14.md) likewise is not a complete published-system replication. The prior-art warning [CIKM 2026 and Supersede](../literature/FULLTEXT_METHOD_SCREEN_2026-11-14.md) remains live.

The original artifact reports `split=pilot`, `holdout_touched=false`, `scientifically_approved=false`, `submission_authorized=false`. There is no evidence of confirmatory exposure in this run. No preregistration freeze, scholarly approval or journal submission occurred.

**Final factual state:** exploratory observations verified; workflow failed on reviewer; external corroboration of provider billing not done; original artifact retained; confirmation not authorised.
