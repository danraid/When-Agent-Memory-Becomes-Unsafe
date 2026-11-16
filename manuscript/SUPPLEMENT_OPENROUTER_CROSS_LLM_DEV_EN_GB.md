# Supplementary exploratory evidence: cross-LLM memory and policy safety via OpenRouter

**Date of evidence:** 16 November 2026. **Classification:** development-only, not confirmatory, not independently adjudicated and not ready for scientific submission. This supplement is **not** a claim of positive superiority, statistical significance or peer-review acceptance.

## A. Public benchmark: LongMemEval-S cleaned

A separately executed public LongMemEval-S cleaned six-question methods pilot compared GPT-4.1 Mini, Gemini 2.5 Flash, DeepSeek Chat V3.1 and Qwen3 Next 80B A3B Instruct. All 72/72 model-condition answers were scored in the successful [v2 run #43848720505](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43848720505), with a detached hash-verified [audit #43852118636](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43852118636). The full-history arm was more accurate than the recent-window and recursive-summary arms in this tiny sample, but unequal information and summarisation capacities prevent a model-level causal interpretation. LongMemEval provides external question-answering task structure, **not external policy-authorisation gold labels**.

## B. Distinct synthetic policy-safety experiments

The earlier [two-episode policy-safety pilot #43861773114](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43861773114) preserved 714/720 scored model-condition rows and ten successful compactions; five Gemini HTTP 429 failures caused six missing/derived rows.

The independently seeded, four-episode [policy-safety v2 run #43869990582](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43869990582) yielded 1,433/1,440 scored model-condition rows, 20/20 successful compacted-memory outputs, four Gemini HTTP 429 failures, and three unscorable guard derivatives. Although the original paid workflow concluded `failure` due to incompleteness, the evidence hashes were valid. A [separate zero-provider-call audit #43899734220](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43899734220) successfully reconstructed all development episodes, prompt digests, response provenance, deterministic evaluator decisions, derived guards and episode-level contrasts. The complete factual audit is [here](../docs/OPENROUTER_POLICY_V2_DETACHED_EVIDENCE_AUDIT_2026-11-16.md).

For the four-episode run, unsafe raw approvals among the scored reference-reject decisions were:

| Model | Full history | Recent 3 records | Recursive summary | Verified policy ledger | Guard final |
|---|---:|---:|---:|---:|---:|
| GPT-4.1 Mini | 2/40 | 9/40 | 1/40 | 1/40 | 0/40 |
| Gemini 2.5 Flash | 0/39 | 16/40 | 3/40 | 1/38 | 0/38 |
| DeepSeek V3.1 | 0/40 | 2/40 | 0/40 | 0/40 | 0/40 |
| Qwen3 Next 80B | 0/40 | 8/40 | 1/40 | 1/40 | 0/40 |

The predeclared exploratory contrast was the episode-mean raw unsafe-approval rate of recursive memory *minus* the verified policy ledger, restricted to reference-reject cases after two completed compacting steps. The four-episode contrasts were **0.0** for GPT-4.1 Mini and DeepSeek, **−0.035714** for Qwen3 Next (one episode favoured recursive memory), and **not estimable** for Gemini because two eligible episodes contained missing ledger responses. No null-hypothesis p-values or confidence intervals were justified for a pilot with only four independent episodes.

This evidence does **not** establish a universal advantage for an external policy ledger over recursive memory. It illustrates how a recent-only window can lose active policy context in the study's unequal-information architecture, while also exposing a substantial false-rejection trade-off. False rejections with recursive memory were GPT-4.1 Mini 6/32, Gemini 3/32, DeepSeek 15/32 and Qwen3 Next 10/32, underscoring that low unsafe-approval rates can coexist with poor task utility. The guard achieved zero observed *final* unsafe approvals on scored cases by deterministic override of the ledger arm's raw response. It was not an independent LLM treatment.

## C. Limits and publication gate

These remain synthetic, English-only, fixed-oracle policy events generated within the project, paired across arms but unequal in authoritative information access. Independent semantic reference labelling has not occurred; 4 episode-level replications lack adequate inferential power; and original Knowledge Triage has not been reproduced in its complete author-published cascade with matching tasks and budgets. Post-hoc pooling of the separate 2-episode and 4-episode pilots would risk masking instrumentation changes and cannot be treated as a prospective, preregistered inferential dataset.

The proper next scientific milestone is a genuinely independently sourced and blind-adjudicated development instrument, followed by a faithful comparator and protocol-specific expert review. The confirmatory holdout remains untouched, the author freeze is absent and journal submission remains blocked. This supplement is only transparent additional exploratory evidence for a possible negative/mixed-results article.
