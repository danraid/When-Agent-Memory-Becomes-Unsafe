# WAMBU-001 | Real Knowledge Triage cascade development execution

**Evidence date:** 2026-11-18 03:13:42 UTC (17 November local).
**Source:** GitHub Actions [run #44228839055](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44228839055), archived [artifact #14393708518](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44228839055/artifacts/14393708518).
**Authorisation:** exploratory development only, issue #50.

## Outcome

**REAL_CASCADE_COMPLETE on ADAPTED_OPENROUTER providers.** Upstream classifier source is unchanged and pinned to commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`, classifier SHA-256 `ab2f236cbede0b1b4b69be07ec4a3519de1603f2a3041919563aea2b410b8b52`.

The original embedding service (`CUSTOM_LLM_API_KEY` and `CUSTOM_LLM_ENDPOINT`) was **not configured**. The original OpenAI API key was present, but this alone cannot satisfy the original embedding dependency. The live run therefore used a clearly **adapted** API route, with:
- OpenRouter embeddings model `qwen/qwen3-embedding-8b`;
- OpenRouter LLM adjudicator `openai/gpt-4.1-mini`;
- unmodified upstream Python `CascadeClassifier.predict` and `EncoderClassifier.fit/predict`.

No mock responses were used for embeddings or LLM in this run. Earlier stub tests remain separately archived and must not be conflated with this live execution.

## Observed decisions

| Development input | Original classifier routing | Predicted type | Confidence | Abstained |
|---|---|---|---:|---|
| `regex` | `regex` | `constraint` | 0.950000 | No |
| `encoder` | `llm` | `belief` | 0.551984 | No |
| `uncertain` | `llm` | `belief` | 0.556278 | No |

The `encoder` test ID is the **intended stimulus label**, not a claim that the encoder decided; the actual observed decision lane was `llm`. Two of the three inputs genuinely reached an LLM. No forced-threshold intervention was needed. The recorded provider request lower bound is 9. This is not an exact total call counter or a formal cost report.

## Scientific limits and reviewer-facing claims

1. The model pair differs from the original required `octen-embedding-8b` and `gpt-5.4-mini` and is **NOT** the original Knowledge Triage cascade configuration.
2. Three small artificial development inputs are not the original benchmark corpus, and no independent action labels or holdout episodes were scored. **No accuracy, memory-safety benefit, parity or statistical inference may be claimed.**
3. This live result verifies functional connection through regex, embedding and LLM routes of unmodified original cascade code under *adapted providers*. It does not demonstrate the SafetyMargin method or whole original framework.
4. Provider credentials are recorded only as present/absent flags. Original embedding endpoint: absent; original embedding key: absent; original OpenAI API key: present; OpenRouter key: present.
5. `full_original_knowledge_triage_replication=false`; `gold_labels=0`; `protected_holdout_access=false`; `confirmatory_protocol_frozen=false`; `author_approval=false`; `external_journal_submission=false`.

**Scientific status:** R02 remains **PARTIAL** (real adapted cascade executed, original exact model pairing and full benchmark not reproduced). R01 remains pending for evidence-qualified action gold.

## Reproduction

The implementation is [`scripts/r02_execute_live_cascade.py`](../scripts/r02_execute_live_cascade.py), with one-shot [Actions workflow](../.github/workflows/r02-live-cascade-development.yml). The archived report is the source of actual observed class predictions; do not replace it with unexecuted expectations or repository checks.

The next R02 eligibility test is to obtain the exact original `octen-embedding-8b` endpoint/key, confirm runtime identity and rerun unchanged original providers with a separately authorised bounded development fixture. Only then can original-classifier-runtime identity be claimed; whole-paper replication would still require corpus, budget, SafetyMargin and downstream experimental parity.
