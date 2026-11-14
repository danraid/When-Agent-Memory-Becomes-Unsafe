# Artigo 1 | Real GPT development pilot audit (2026-11-14)

**Outcome: TECHNICAL PILOT PASS / SCIENTIFIC INFERENCE NOT AUTHORISED.**

## Provenance
- Repository: `danraid/When-Agent-Memory-Becomes-Unsafe`.
- [Github Actions run 43618151905](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43618151905), **attempt 2**, conclusion `success`; attempt 1 was previously blocked for a missing repository secret.
- [Original artifact 14123516185](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43618151905/artifacts/14123516185), stored for 90 days. Use this artifact rather than the earlier 185-byte blocker artifact.
- Split: `development`; two independent synthetic-policy episodes, 12 steps per episode.
- GPT-6.1 Terra: **96 actual model decision calls**, 6 genuine recursive summary compactions.
- GPT-6 Luna: 2 blind advisory reviews.
- **104 unique provider response IDs**, 104 paid model calls total; 120 scored observations because 24 guard-condition decisions are deterministically derived from already observed model responses, not new independent calls.
- Observed provider-reported usage summed from these calls: 53,845 input tokens and 4,875 output tokens. The usage ledger reports reserved accounting values rather than billing totals.
- GitHub Actions unit tests, preflight, empirical manifest verification, advisory review and final scientific-gate assertions all passed.
- Empirical 4/4 and advisory 1/1 file hash-and-size manifest entries independently rechecked against the downloaded artifact; each matched.

## Descriptive benchmark (24 scored cases per condition)

| Condition | Raw accuracy | Unsafe approvals / 12 eligible rejections | False rejections |
| --- | ---: | ---: | ---: |
| Full history | 24/24 (100%) | 0 | 0 |
| Recent window | 17/24 (70.8%) | 2 | 5 |
| Recursive GPT summary | 24/24 (100%) | 0 | 0 |
| Pinned policy ledger | 24/24 (100%) | 0 | 0 |
| Pinned ledger + deterministic guard | 24/24 (100%) | 0 | 0 |

Actual recursive compaction depth reached 3 per episode (6 total compactions).

**Critical limitations:** only two independent episodes; substantial non-independence among repeated decision cases; synthetic policies and fixed-oracle trajectories, not a general agent-in-the-wild study; unequal exposure to protected policy between some baselines; guard derived from the pinned ledger decision and did not produce separate GPT calls. The exploratory candidate contrast between pinned ledger and recursive summary after two compactions is descriptively zero in this sample and must not be presented as evidence of equivalence or statistical superiority. No confirmatory p-value or confidence claim is warranted.

## Low-cost blinded model feedback

The contract reviewer sampled 8 responses and noted valid JSON and allowed actions. The methodological reviewer warned that the fixed, non-random review sample is unrepresentative; cases repeat across conditions; and the pinned ledger may gain a privileged second presentation of authorised policy. Reviewers had no gold labels and do not constitute independent human peer review.

## Decision and next bounded milestone
- **COMPLETE:** real API secret and provider connectivity, pilot code execution, ledger accounting, original response provenance, recursive compactions, two advisory reviews, evidence SHA-256 verification.
- **PARTIAL:** study-specific empirical design and reviewer-guided validity remediation.
- **NOT STARTED:** prospectively frozen, suitably powered confirmatory experiment.
- **UNTOUCHED:** confirmatory holdout and private seed.
- **NOT AUTHORISED:** scientific approval, publication-ready results or journal submission.

Next: address reviewer-identified methodological confounds in the development protocol, define independent replication and power-analysis plan, perform source-method evidence audit, then freeze protocol before any confirmatory run. Do not refit and then report the original development run as confirmation.
