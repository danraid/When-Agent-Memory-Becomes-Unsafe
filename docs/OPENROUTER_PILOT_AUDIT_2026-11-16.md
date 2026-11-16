# WAMBU-001 | Original OpenRouter LongMemEval-S development pilot audit

**Evidence cutoff:** 2026-11-16. **Status:** `PARTIAL_EMPIRICAL_DEVELOPMENT`, NOT confirmatory or submission-ready. This is a non-promoting factual audit of original, immutable evidence.

## Provenance

- GitHub Actions [run 43800537863](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43800537863), **completed/failure**, not PASS.
- Original [artifact 14196748345](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43800537863/artifacts/14196748345); artifact ZIP SHA-256 as reported by GitHub Actions: `0a18f33662bca0d6a29e1d73018bdc2e7269d72d0336b32e39e5558071b1fad2`.
- Independently downloaded and extracted the original ZIP for this audit. All **17/17** `manifest.json.files_sha256` entries matched the extracted file bytes. Underlying `run_metadata.json` records official LongMemEval-S cleaned dataset SHA-256 `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`; the original dataset was not embedded in the artifact.
- The runtime preflight confirmed a nonempty OpenRouter secret without displaying it. 114 offline tests passed (one skipped); official 500-question JSON was loaded and structurally validated.
- Source, model matrix, prompts, random question selection and evaluation criteria are those in the **original run**. Any future source or model change is a different exploratory experiment and may not silently reclassify these observations.

## Descriptive results, six deterministically selected benchmark questions

All models were assessed on the same six question IDs, three memory arms each. The scores below are judge verdicts, **not human-adjudicated ground truth**. Each cell reports correct / six expected; `Qwen3 32B` is partially missing.

| Requested model | Full history | Last 8 sessions | Recursive summary | Scored answers / expected |
| --- | ---: | ---: | ---: | ---: |
| openai/gpt-4.1-mini | 3/6 | 1/6 | 0/6 | 18/18 |
| google/gemini-2.5-flash | 3/6 | 1/6 | 0/6 | 18/18 |
| deepseek/deepseek-chat-v3.1 | 5/6 | 1/6 | 1/6 | 18/18 |
| qwen/qwen3-32b | 0/6 (0 scored) | 1/6 (3 scored) | 0/6 (3 scored) | 6/18 |

**Total:** 60 / 72 expected answers were scored; 276 provider-call reservations (not necessarily completed or billed calls). This is **83.33% coverage**, not 83.33% accuracy. Never treat unscored Qwen answers as known incorrect model responses.

## Failure taxonomy based on original per-question evidence

Twelve Qwen arms were not scored:

- Six `ANSWER_FAILED:OPENROUTER_HTTP_429` (all full-history).
- Four `ANSWER_FAILED:EMPTY_PROVIDER_CONTENT` (three recent-window, one recursive-summary).
- Two `COMPACTION_FAILED:EMPTY_PROVIDER_CONTENT` (two recursive-summary).

OpenRouter documentation explains that `finish_reason=length` and an empty answer may occur when reasoning consumes the completion-token budget; the original code did not retain finish-reason/usage metadata on empty responses, so this is a **plausible explanation, not a confirmed root cause**. HTTP 429 denotes rate limiting; do not silently retry possibly billed attempts. The Qwen3 32B model's 131K context window may also make full-history cases more fragile, but the original artifact does **not** prove a context-limit error. Future profiles should use a documented long-context, non-thinking model or isolate a prospective reasoning-mode intervention.

## Scientific boundary

- `LongMemEval` tests memory-related question answering, knowledge updates, abstention and temporal reasoning, **not unsafe authorisation events**. It is a complementary benchmark, not evidence for the primary WAMBU-001 unsafe-approval estimand.
- Six selected questions are only a connectivity/methods pilot, with no prospective inferential power, no independent human adjudication and no completed Qwen coverage. No model ranking or superiority claim is warranted.
- The full-history baseline receives more information than compacted and recent-window arms. This is a **systems architecture** comparison and cannot isolate intrinsic LLM memory capacity.
- Development-only results; protocol remains unfrozen, private confirmation holdout was not touched, no independent scientific approval or submission authorisation.

## Next eligible bounded work package

Retain the original failed run and artifact. Create an **amended prospective development pilot** with (i) explicit model ID substitution documented before execution, (ii) metadata on empty completions and 429s, (iii) finite attempts without automatic re-submission, (iv) all-arm paired case IDs and conservative missingness, (v) hash-verified artifacts and a complete status gate. Do not upgrade past observations or open a confirmatory split.

### Relevant external source records

- Official LongMemEval repository: https://github.com/xiaowu0162/LongMemEval
- OpenRouter reasoning budget guidance: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
- OpenRouter provider errors: https://openrouter.ai/docs/api-reference/errors-and-debugging
- Alternative, explicitly different non-thinking Qwen model: https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct
