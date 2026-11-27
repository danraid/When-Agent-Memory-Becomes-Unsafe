# WAMBU R04 | Temporal-authority stress instrument: real pilot and detached audit

**19 November 2026 (UTC).** Exploratory development results. **Scientific instrument-discriminability verdict: FAIL / CEILING PERSISTS.** This is a negative observation, not an implementation failure or a retrospective confirmatory study.

## Predeclared design

The [prospective development-only protocol](../protocol/R04_TEMPORAL_AUTHORITY_STRESS_DEV_V1.json) fixed **two independent seeded episodes**, **18 queries per episode**, nine expected approvals and nine expected rejections in each episode, and three paid arms with the same public event packet:

1. source-only event history;
2. recursive summary plus identical history;
3. deterministic time-aware policy ledger derived only from identical history.

The signed *synthetic* events include initial and superseding restrictions, scoped temporary exemptions, a revocation and a non-authoritative contradictory note, with some retrospective as-of-time queries. The event records are simulated, not real cryptographic signatures or independently adjudicated institutional policies. Queries are shuffled by the development seed before model execution, with the synthetic oracle and scenario tags excluded from prompts. The three methods have **matched source availability**, but not matched computation or token consumption.

## Exact observed run evidence

- [Live run #44518845870](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44518845870): PASS, [artifact #14527287005](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44518845870/artifacts/14527287005), ZIP SHA-256 `b1da9e3f0682cf1f33a7d65362620fe12eb950fbcbcbe7b16a11f793e047046e`.
- [Detached, zero-paid-call audit #44519469398](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44519469398): PASS, [artifact #14528050471](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44519469398/artifacts/14528050471), ZIP SHA-256 `da468190d5cb038bf464586c608cd50d12a35fe53a0999b985c554747fecccb9`.
- All **116 observed provider calls**: 108 decisions, eight recursive compactions, distinct response IDs. All 36 paired scenarios were reconstructed in the detached audit, including source and query SHA-256, episode/order, expected sidecar actions and complete provider usage. No missing or failed checks.
- An initial preflight CI failure due to case-sensitive parsing of an authorised event was fixed *before* the live model run; historical failed CI remains archived. Source and label contracts passed before real calls.

## Results

| Arm | Correct raw agent decisions | Invalid replies | Input tokens for decision calls |
|---|---:|---:|---:|
| Original signed event packet only | **36/36** | 0 | 10,810 |
| Original packet plus recursive summary | **36/36** | 0 | 19,342 |
| Original packet plus derived temporal ledger | **36/36** | 0 | 12,054 |

**Paired action disagreements: zero.** No method failed a policy-update or exception query in this development sample. The new instrument therefore did **not** address the empirical ceiling observed in the prior R03 pilot, even with more varied valid scenarios. This is not a proof of safety, accuracy in naturally occurring tasks, equivalence, or superiority. Two episodes do not support independent inferential statistical claims.

The source-only arm has the least input-token use, but this is a *prompt accounting observation*, not an end-to-end cost-performance conclusion. No outcome-driven case filtering, relabelling or revised success threshold was applied after observing model responses.

## Bounded completion and next scientific dependency

**Engineering completion: COMPLETE**. Source-isolation tests, real 116-call execution, immutable evidence and independent audit all passed.

**Scientific R04 milestone: PARTIAL / NONDISCRIMINATIVE**. The empirical terminal condition (non-ceiling discrimination without leaking or handicapping source information) **failed**. Do **not** escalate the same saturated source-easy synthetic exercise into a confirmatory trial.

The next defensible work unit is an independently grounded R01 policy-action task corpus with authentic event-time authority, human-independent agent adjudication explicitly identified as AI (not human), and historically replayable observable decisions. Only then choose tasks prospective to model outcomes with sufficiently complex state, differentiated memory budgets and independent adjudicator evidence. If all tasks remain easy with full-policy source exposure, define a different scientific estimand (e.g., provenance fidelity under resource limitations) prospectively rather than manufacturing mistakes.

The one-shot paid R04 push trigger was disabled after completion. Octen was **not** used here. Full R02 original-method benchmarks remain a separate possible Octen dependency. Author final approval, protected holdout and external submission remain prohibited by issue #50.
