# WAMBU-001 | Cross-LLM authorised-policy safety development pilot

**Predeclared on 2026-11-16, before paid pilot execution.**
**Classification:** exploratory synthetic task, not a public standardized safety benchmark, not an independently adjudicated naturalistic experiment, and not a confirmatory test.

## Objective and terminal state

Re-use the article's deterministic, balanced, policy-supersession episode generator and policy evaluator, on **two independent 18-turn development episodes**, with exactly **four** OpenRouter decision models and a **single shared anchor compactor**. Retain a per-case pairing across full history, last-three-event window, recursively compacted summary, current authorised-policy ledger, and a deterministic guard derivative that reuses the ledger model's raw response (no additional model call). Complete an immutable, source/config-hashed evidence artifact, or label incomplete work as partial with explicit provider failures.

## Predeclared treatment and model matrix

- Fixed compactor: `openai/gpt-4.1-mini`, generating one shared summary per episode and depth. This intentionally isolates **decision-model comparisons conditional on that compactor** and does not test alternative compactor quality.
- Decision models: `openai/gpt-4.1-mini`, `google/gemini-2.5-flash`, `deepseek/deepseek-chat-v3.1`, `qwen/qwen3-next-80b-a3b-instruct`.
- Generation caps: 600 summary tokens, 200 decision tokens, temperature 0. Calls are serial and individually reserved before the network request.
- Two fixed-seed development episodes × 18 decisions, balanced scenario modes. Five genuine compactions per episode; 4 paid decision arms × 4 model variants per step; one guard derivative per model-case. Planned 586 paid provider calls, maximum reservations 750. No automatic re-sending of uncertain billed requests.
- Reference decisions and future requests **never enter any model or compactor prompts**. Only after inference do evaluator labels meet model answers. The ledger is reconstructed independently from authorised public events; the guard never reads the evaluator's hidden reference policy.
- Each model sees the **same episode, requests and shared summaries**, while ledger conditions deliberately receive extra policy information. That asymmetry is essential to the systems comparison and cannot support an intrinsic-model superiority claim.

## Descriptive endpoints

Primary development description: raw unsafe-approval frequency on reference-REJECT cases **after at least two genuine compactions**, separately per model and condition. The within-model recursive-summary minus pinned-ledger difference is computed at episode level *only when every eligible paired case has valid responses*. Missing rows never disappear from denominators without notice. Other descriptions: false final rejection, invalid JSON, guard overrides, complete case coverage, provider failures, observed token usage and source hashes. No p-values or confidence intervals are confirmatory.

## Evidence and boundaries

Original LongMemEval v2 evidence is independently archived and separate. This synthetic-authority study is **not** LongMemEval, AgentDojo, MemoryAgentBench, a human-adjudicated safety benchmark or a whole-framework Knowledge Triage reproduction. It neither opens a private confirmatory holdout nor changes `protocol/PREREGISTRATION.md`, `protocol/STUDY_PLAN.json`, past v2/v3 observations, or publication gate status. An improvement may reflect privileged policy access or deterministic guard logic, not generalised LLM robustness.

GitHub Actions uses the repository's `OPENROUTER_API_KEY` or `OPENROUTER` secret without printing credentials; see `.github/workflows/openrouter-policy-safety.yml`. A green code CI only supports those tests, not scientific approval.

## Follow-on scientific requirements

Independently sourced naturalistic authority chains, externally adjudicated gold decisions, independently checked original Knowledge Triage baseline and prospective author-frozen confirmation remain outside this development pilot. Publication claims must retain null effects, incomplete provider attempts and the small independent-episode sample.
