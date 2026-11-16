# WAMBU-001 | OpenRouter cross-model policy-safety development v2: independently reproducible evidence

**As of:** 16 November 2026. **Scientific status:** `EXPLORATORY_PARTIAL_PROVIDER_OR_COMPACTION_FAILURE`. This report documents original immutable outcomes. **No scientific approval, frozen confirmatory protocol, human case adjudication or journal-submission clearance is implied.**

## Evidence provenance and verification

| Artifact | Verified reference |
|---|---|
| Original paid run | [GitHub Actions #43869990582](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43869990582), original status **failure** |
| Original data | [Artifact #14229215515](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43869990582/artifacts/14229215515), ZIP SHA-256 `c707c20caba5c2430edba1395e098a64321165f20ac78c2b3957840165d3a479` |
| Original run code | `02ea0ce4f2b4648e11ae143ea5e53215a8889039` |
| Original config SHA-256 | `2155ac708f62f2280f595518ab6eddbc6a905a8bb1848dee11b1d1d61f6b33bb` |
| Detached audit implementation | [PR #29](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/pull/29) and [invocation correction PR #30](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/pull/30) |
| Detached, zero-provider-call reproducibility audit | [Successful GitHub Actions #43899734220](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43899734220) and [artifact #14241011793](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43899734220/artifacts/14241011793) |

The detached auditor verified **5/5** original evidence digests *before* parsing source data, checked the SHA-256 digests of all version-pinned original study modules against the original artefact metadata, reconstructed all four development episodes and all 20 compacted-memory prompts from the predeclared seed, independently recomputed agent-decision evaluations, verified the 1,440 exact model/episode/condition keys and all available non-duplicate paid response IDs, and checked all guard derivatives against their parent model response. The detached workflow executed **zero** additional LLM calls.

The paid experiment reserved **1,172** API calls, produced **1,168** unique provider response IDs, and obtained **1,433/1,440** scored model-condition rows (**99.51% coverage**). The 20 required compacted-memory responses were present. Four Gemini 2.5 Flash requests returned HTTP 429; three unavailable policy-ledger outputs also invalidated the three derived guard rows. All missing cases are retained as unscored, not wrongly predicted.

## Overall descriptive safety outcomes

`unsafe/n` denotes raw unauthorised approvals among evaluated reference-REJECT cases. `guard` reports the **final** post-guard unsafe approvals, not zero underlying raw errors. The four-episode design has 40 reject opportunities per subject model and memory condition; some Gemini denominators are smaller due to missing calls.

| Decision model | Full history | Recent window | Recursive summary | Current authorised ledger | Deterministic guard final |
|---|---:|---:|---:|---:|---:|
| GPT-4.1 Mini | 2/40 | 9/40 | 1/40 | 1/40 | 0/40 |
| Gemini 2.5 Flash | 0/39 | 16/40 | 3/40 | 1/38 | 0/38 |
| DeepSeek Chat V3.1 | 0/40 | 2/40 | 0/40 | 0/40 | 0/40 |
| Qwen3 Next 80B A3B Instruct | 0/40 | 8/40 | 1/40 | 1/40 | 0/40 |

The paired **post-two-compaction exploratory primary contrast**, raw unsafe rate in `recursive_summary` minus rate in `pinned_ledger`, is the mean of **independent episode-level** differences, not the row-wise pooled difference:

- GPT-4.1 Mini: `0.0000`; four complete episode contrasts `[0, 0, 0, 0]`.
- Gemini 2.5 Flash: `null`; two of four episodes have incomplete eligible model pairs, so **no complete mean** exists.
- DeepSeek Chat V3.1: `0.0000`; four complete episode contrasts `[0, 0, 0, 0]`.
- Qwen3 Next 80B: `-0.0357142857`; four episode contrasts `[0, -0.1428571429, 0, 0]` (no general superiority claim).

These are **negative/null results for a general claim that external ledger improves raw unauthorised-approval risk** in this sample. Descriptively, the last-three-event baseline showed substantially more unsafe approvals, but it had less authoritative information and therefore is not an equal-information causal comparator.

## Utility and false rejection trade-off

Among 32 reference-APPROVE tasks per model/condition, the `recursive_summary` condition had false rejections: GPT-4.1 Mini **6**, Gemini **3**, DeepSeek **15**, Qwen3 Next **10**. In the ledger condition, false rejections were GPT-4.1 Mini **5**, Gemini **1/31 scored**, DeepSeek **14**, Qwen3 Next **5**. Thus, simply maximising rejection can hide material utility loss. No utility result is a scientific ranking with N=4 independent episodes.

The deterministic policy guard eliminated observed *final* unsafe approvals in its evaluated cases and did not turn raw model mistakes into correctness evidence. This is by-design override on the same raw model responses; it is neither an independent LLM baseline nor evidence of guaranteed real-world safety.

## Reliability and reproducibility status

- **Original live execution:** `PARTIAL` / GitHub Actions failed, with all original errors and missing rows preserved.
- **Offline source-pinned computational audit:** `COMPLETE` / GitHub Actions succeeded.
- **Semantic ground-truth validity:** `NOT VALIDATED INDEPENDENTLY`; the reference comes from the same synthetic task generator and deterministic rules, not independent domain adjudicators.
- **Original full Knowledge Triage framework comparator:** `PARTIAL`, not end-to-end reproduced with model/budget/cascade parity.
- **Naturalistic external authority-case corpus:** `PARTIAL`; six independently published PEP/RFC source pairs have provenance, but no qualified independently adjudicated decision dataset.
- **Frozen confirmatory protocol / protected holdout / peer review / journal submission:** `NOT STARTED` or **BLOCKED by scientific gates**.

## Single next eligible scientific milestone

Resolve the **P07b naturalistic policy-authority corpus validity gate** rather than repeating paid synthetic trials until they yield a preferred effect. Use the existing externally authored PEP/RFC supersession source candidates only where scope, version, timestamp and issuer are defensible. Collect blind decisions from authentic independent expert adjudicators with source evidence, licence/privacy review and documented disagreements. The casebook must exclude gold/reference labels from model-visible inputs. Only once qualified naturalistic development labels exist, assess discrimination against source-faithful baselines and seek content-specific author review of a prospective confirmatory plan.

**Publication implication:** this run supports a transparent exploratory *negative/mixed findings* appendix. It does not support a publication claim of model superiority, generalised memory safety, a successful official Knowledge Triage replication, a statistically significant positive effect, or any human peer-review acceptance.
