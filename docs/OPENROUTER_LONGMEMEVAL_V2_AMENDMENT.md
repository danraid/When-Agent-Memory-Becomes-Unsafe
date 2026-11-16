# WAMBU-001 | Prospective LongMemEval-S development amendment v2 (16 Nov 2026)

**Classification:** EXPLORATORY / DEVELOPMENT. **Not a confirmatory protocol freeze.**

## Rationale and original evidence

First run [43800537863](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43800537863) produced 60/72 scored answers and 12 Qwen3-32B non-scored arms. Its audit is in [OPENROUTER_PILOT_AUDIT_2026-11-16.md](OPENROUTER_PILOT_AUDIT_2026-11-16.md). Original results are immutable historical data and never rebranded as a completed benchmark.

## Amendment applied before new paid execution

- **New predeclared model matrix:** OpenAI GPT-4.1 Mini; Google Gemini 2.5 Flash; DeepSeek Chat V3.1; **Qwen3 Next 80B A3B Instruct**. The latter is a **different checkpoint/family configuration** than Qwen3 32B, selected for its explicitly non-thinking instruction profile and 262K context capacity (OpenRouter model listing). Do **not** attribute changes to a repaired Qwen3 32B.
- The separate OpenRouter judge remains Anthropic Claude Haiku 4.5. It is a fallible model-assisted scorer, **not independent peer review**. Public benchmark gold answers are supplied only to the judge **after** answers are produced.
- Same official cleaned LongMemEval-S dataset version path, 500-item validation, stratified six-question fixed-seed selection, and identical three memory arms as the original, but updated response token caps: compacted summary 1,400, model answer 400, judge verdict 32. This changes the generation regime across **all** model arms, which is why v2 is a **new exploratory experiment**, not a matched direct extension of v1.
- Continue enforcing a maximum of 750 provider-call reservations in this finite pilot and **no automatic retries** of uncertain/billed requests. Errors remain errors. Report HTTP codes, finish reasons and non-sensitive completion-token counts for empty responses.
- Preserve full manifest hashes, source/config/model IDs, 6 selected IDs, per-arm predictions, judge decisions, attempted versus scored calls, original status, null/negative outcomes and per-type descriptive rates. A pass needs 72/72 scored responses, independently matching artifact file digests, 4 distinct subject model slugs, and no holdout access.
- If anything is incomplete, label the run **INCOMPLETE**, preserve evidence and diagnose before another paid attempt. Do not silently score missing as an observed wrong model decision or replace failed cases with easier ones.

## Limits and next research milestone

The three memory arms test systems with different information access. Six cases give no power for model ranking. LongMemEval evaluates answer preservation, not WAMBU-001 unauthorised approval decisions. Genuine safety claims require a **separate** action-level, independently adjudicated public-authority benchmark and a distinct author-frozen confirmatory protocol. All existing WAMBU scientific gates remain closed.

**External references:** official benchmark https://github.com/xiaowu0162/LongMemEval ; Qwen3 Next Instruct https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct .
