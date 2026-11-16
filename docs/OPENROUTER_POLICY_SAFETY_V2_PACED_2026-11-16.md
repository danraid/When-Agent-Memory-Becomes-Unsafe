# OpenRouter cross-model policy safety: predeclared development v2

**Date:** 2026-11-16. **Classification:** exploratory synthetic development only.  
**Frozen WAMBU confirmatory authority:** unchanged and UNFROZEN; no private holdout, human approval, or journal submission.

## Audit evidence motivating this amendment

The original run [43861773114](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43861773114) finished `failure` due to incomplete provider coverage, not digest corruption. Original archived [artifact 14222994247](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43861773114/artifacts/14222994247) had 714/720 valid scored rows, all ten compactions, and 586 call reservations. Five distinct decisions failed with `OPENROUTER_HTTP_429` for Gemini 2.5 Flash. The sixth unscored row is the deterministic guard derivative of the unavailable pinned-ledger response. All five rate-limited decisions occurred at compaction depth 1, involved reference-APPROVE requests, and therefore did **not** invalidate paired REJECT cases after depth >=2. Original data and manifest hashes must be retained unchanged. The original GitHub workflow's failure status must never be relabelled to success.

The original run is **partially complete** and provides exploratory descriptive observations, not a confirmatory test. The original evidence was independently extracted and checked against 5/5 manifest digests before amendment.

## Bounded v2 terminal state

Run **four NEW, independently seeded, 18-turn development episodes** with the same four decision model slugs, a shared GPT-4.1 Mini compactor, and the original WAMBU deterministic task and judgement code. Complete all 4 x 18 x 4 x 5 = **1,440 scored or explicitly missing model-arm rows** (five conditions include one deterministic guard derivative), with 4 x 5 = **20 genuine compaction attempts**, maximum **1,172 expected paid calls** and **1,250 reserved call limit**. Original two episodes are not recycled or added to this new sample. All original model contrasts, including null and negative effects, are preserved separately.

## Prospective change (written before v2 paid calls)

The model matrix, task family, memory arms, reference policy rules, 18-turn cadence, single compactor and evaluator semantics remain as in the original pilot. In v2 the source module and config have distinct versioned filenames and hashes. Before each new provider call, the API adapter applies a separate minimum spacing for each model: Gemini 2.5 Flash 2.5 seconds; other models 0.5 seconds. After **any** Gemini or other model HTTP 429, it records the failed attempted call and waits at least 30 seconds before the next call **to the same model**. It never automatically retries the failed request. Subsequent calls to other models are unaffected. This is an engineering-rate mitigation, **not** an attempt to alter or repair previously observed outcomes. Provider-side concurrency, quota exhaustion or unexpected infrastructure faults may still cause missing rows.

The experiment evaluates **raw unsafe approvals on reference REJECT cases**, conditional on compaction depth >=2, as an exploratory per-episode contrast between `recursive_summary` and `pinned_ledger`. Secondary descriptions must include false rejections on valid requests, invalid JSON, guard override rates, missingness, HTTP errors, compaction failures, metadata, and raw vs final action. **Guarded raw approvals can still occur:** only the guard's *final action* is safety-overridden, so never write that the guard eliminated all unsafe raw approvals.

## Acceptance and failures

A complete v2 run requires 1,440/1,440 evaluated rows, 20/20 actual compactions, unique provider response IDs for the paid calls, all original file digests matching the manifest, and no holdout access. An incomplete run must remain marked partial with all unscored/missing cases, error codes and exact denominators intact. No success claims may be inferred from an artifact alone or a green offline CI; a green experiment is operational completion only, **not publication validation**.

OpenRouter secret variable is resolved from `OPENROUTER_API_KEY` or `OPENROUTER` in GitHub Actions secrets. Do not expose it or depend on personal local key access. The v2 workflow may trigger only once on merge; no recurring paid jobs, no uncontrolled loops, no private confirmation.

## Interpretation

This is a **synthetic, fixed-oracle, unequal-information policy-safety study** and is not a standardized third-party benchmark. The publicly sourced LongMemEval companion study measures question answering rather than unsafe action authorization, and must be analysed separately. Four episodes cannot establish definitive model rankings or inferential generalization. The original WAMBU scientific gates, independent naturalistic adjudication, full Knowledge Triage replication and prospective author freeze remain outstanding.
