# WAMBU-001 | v3 original artifact recovery and failure audit

**Observed 14 November 2026 UTC.** This is a descriptive recovery from the **original GitHub Actions artifact**, not a re-run or a confirmatory result.

## Source and run-level outcome

- [Original run 43640571248](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248), triggered on source commit [5053bd0d5925c91e35d1dc5ff412d0f5c2e625d8](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/commit/5053bd0d5925c91e35d1dc5ff412d0f5c2e625d8): **completed/failure** because the post-experiment AI advisory step raised `AdvisoryError: EMPTY_ADVISORY_NO_APPROVAL`.
- The **paid empirical execution and its verify step both succeeded**, before the advisory failure. The advisory step did not produce `reviewers.json`; subsequent report step was skipped. Do not claim two completed v3 reviewers.
- [Original ZIP artifact 14131424960](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248/artifacts/14131424960), uploaded despite job failure, 109223 bytes, 9 ZIP entries, ZIP CRC PASS.
- SHA-256 verified directly from the downloaded ZIP bytes: `4994fa4fdd80412cbd2722f36840d5388c3358aa6dab3759926f44c1134e09f5`, equal to the upload-job log.
- `empirical/manifest.json` lists 4 evidence files; all 4 have matching SHA-256 and size. `summary.json` matches `status.json`; both partial observation and compaction files equal final counterparts. All **432 model prompt hashes** were recomputed successfully.
- **380 distinct empirical provider response IDs:** 360 paid decision outputs (4 episodes × 18 turns × 5 arms) plus 20 actual recursive compactions (5 per episode). The 72 `temporal_policy_ledger_guard` outputs **reuse** corresponding ledger provider response IDs and do not constitute new model calls. Total scored observations: **432**.
- `provider-ledger.json` records **381 accounted/reserved calls**, compared with 380 recorded experimental response IDs. One additional call accounting entry is consistent with the failed advisory attempt but no usable reviewer record or provider attestation exists. USD `2.3787141` is the ledger's **conservative estimate/reservation**, **not an authenticated bill**. Do not infer a successfully completed reviewer call.

## Descriptive results from the original `empirical/summary.json`

| Arm | Correct / 72 | Accuracy | Wrongful stale-rule rejections / 16 revocation probes | Missed newly active enforcement / 16 probes |
| --- | ---: | ---: | ---: | ---: |
| `full_history` | 72 | 100% | 0/16 | 0/16 |
| `recent_window` | 52 | 72.22% | 0/16 | 0/16 |
| `recursive_summary` | 72 | 100% | 0/16 | 0/16 |
| `typed_retention_adapted` | 72 | 100% | 0/16 | 0/16 |
| `temporal_policy_ledger` | 72 | 100% | 0/16 | 0/16 |
| `temporal_policy_ledger_guard` (derived) | 72 | 100% | 0/16 | 0/16 |

Each of four episodes has **3 primary-eligible revocation probes after at least two compactions**; the four episode-level contrasts `typed_retention_adapted minus temporal_policy_ledger` are **0, 0, 0, 0**; episode-mean = **0.0000**. This is a **descriptive null difference**, **not statistical equivalence**, positive evidence of policy superiority, scientific approval, or generalisation.

The current instrument has **strong ceiling effects** and deterministic synthetic authority patterns, consistent with prior-art cautions about trivial supersession prompts. `typed_retention_adapted` is not the full published Knowledge Triage implementation, and unequal information/token budgets are confounders.

## Integrity boundaries and recovery decision

The original source/status declares `split=pilot`, `holdout_touched=false`, `scientifically_approved=false`, `submission_authorized=false`. No confirmation is authorised or accessed during this audit. The archive is a historical, immutable pilot; do not write repaired review outputs into it.

**Decision:** accept the **experimental record as internally verified exploratory evidence**, classify the **complete run as failed on advisory**, and do **not** rerun the 380 paid experiment calls. Defer any new paid adviser call until a separate prospective, finite rationale is approved. For publication readiness, focus next on an independently auditable realistic authority-conflict instrument and comparator parity.

**Novelty gate persists:** [CIKM 2026 overlap](../literature/HIGH_OVERLAP_PRIOR_ART_2026-11-14.md), [full-text/method audit](../literature/FULLTEXT_METHOD_SCREEN_2026-11-14.md), [pinned upstream component audit](../literature/UPSTREAM_TYPECOMPACT_COMPONENT_RESULT_2026-11-14.md). Original Knowledge Triage TypeCompact component checks are not a full-framework replication. No journal submission took place.
