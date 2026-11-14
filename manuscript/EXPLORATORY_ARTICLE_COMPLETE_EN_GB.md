# When Agent Memory Becomes Unsafe: Exploratory Evidence on Temporal Policy Supersession and Repeated Context Compaction

**Daniel Raaid**

**Manuscript version:** 14 November 2026. **Article type:** completed *exploratory research report* based on archived development observations. **Not a confirmatory study, independently peer-reviewed paper, accepted publication, or submitted manuscript.** Language: British English.

## Abstract

**Background.** Long-running language-model agents compress their histories, yet a reliable memory must both retain active constraints and stop enforcing restrictions that have been legitimately superseded. The latter question overlaps with existing work on typed constraint preservation and memory updating, so novelty cannot be assumed. **Methods.** We report two provenance-audited, synthetic, paired development pilots using real GPT responses, with four and eight independent episodes respectively, plus a source-faithful offline component audit of the original Knowledge Triage TypeCompact implementation on its authors' 327-file public sample. The later temporal pilot used five GPT decision arms and one derived deterministic guard. **Results.** In the eight-episode pilot, full history, recursive summarisation and a version-aware ledger each answered 144/144 decisions correctly, while a recent-window condition answered 105/144. In the separate four-episode temporal pilot, full history, recursive summarisation, an adapted typed archive and a version-aware ledger each answered 72/72; the recent-window condition answered 52/72. All arms had zero observed errors on the temporal pilot's 16 revocation and 16 new-restriction probes per arm; its 20 recent-window errors occurred on controls. The temporal pilot's original workflow failed during advisory review, although the original observation artifact was independently recovered and verified. The upstream TypeCompact component was exercised in 1,308 public-sample configurations; 19, 4, 1 and 0 files respectively returned `COMPACTION_UNSAFE` at 25%, 50%, 75% and 100% estimated-token budgets. **Interpretation.** The experiments demonstrate technical feasibility and important instrument ceiling effects, but **do not establish a benefit of the ledger over recursive summarisation, causal superiority over Knowledge Triage, safety assurance or a confirmatory effect**. Independently adjudicated real-world cases and a full original-framework comparator remain necessary.

**Keywords:** agent memory; context compaction; policy supersession; constraint retention; evaluation provenance; negative findings.

## 1. Introduction

Persistent AI agents depend on summaries, retrieved memories and external state to make decisions after a long sequence of events. The standard intuition that safety-critical instructions should be preserved verbatim is incomplete when those instructions can be validly revoked, replaced, narrowed or scoped by later authoritative events. A stale prohibition can create a false rejection; losing a newly active prohibition can create an unsafe approval. Both are errors, but they have different causal pathways and must not be conflated.

This study is positioned against direct prior art. Zerhoudi, Mitrović and Granitzer's *The Compaction Cliff in Long-Running AI Agent Memory* (CIKM 2026) introduces Knowledge Triage, a framework for type-sensitive constraint preservation, decomposition and retrieval. Patel's *Supersede* (2026, preprint) addresses the memory-update gap. LongMemEval evaluates knowledge updates in conversational memory, while ACON considers optimisation of long-horizon agent context compression. Consequently, neither retaining constraints nor remembering supersessions is presented here as a new discovery. The remaining open methodological question is whether authenticated authority, temporal validity and source access can be tested in a sufficiently discriminative, comparable agent-decision setting.

We therefore report **what the available experiments actually show**, including null contrasts, failed review automation and infeasible compaction states. This report does not claim a novel validated method.

## 2. Questions and study status

**RQ1.** Can a controlled synthetic workflow expose decision failures after repeated GPT compaction, particularly failures to honour policy supersession?

**RQ2.** In the available development episodes, how do full history, recent-window memory, recursive summaries, an adapted typed archive and a version-aware ledger behave?

**RQ3.** Does a pinned original TypeCompact implementation reveal feasibility limits on a public sample when constraints must be retained under finite budgets?

These are exploratory descriptive questions. No confirmatory primary estimand was prospectively frozen for these observations; the eight-episode and four-episode pilots are separate instruments and **are not pooled**.

## 3. Methods

### 3.1 Experimental environments and units

Both development instruments simulated transaction-approval tasks with authorised policy events and binary approve/reject decisions. Each episode was an independent seeded sequence; turns within an episode were repeated observations, not independent samples. The eight-episode v2 pilot contained 18 turns per episode, 144 decisions per arm, four GPT decision arms and a fifth derived guard. The temporal v3 pilot contained four episodes with 18 turns each, five paid GPT decision arms and a sixth derived guard. Genuine GPT compaction calls were made during both pilots. The reference decision was computed separately from the model's input.

The temporal v3 instrument tested supersession in two directions: *stale-rule revocation* (the old restriction should no longer block an action) and *new-rule enforcement* (a newly valid restriction should block an action). Source events, episode prompts and observed responses were recorded with identifiers and integrity hashes. The policy ledger used explicit current-state information; comparisons with a summary-only context therefore conflate memory architecture with available policy information.

### 3.2 Arms and comparators

The shared arms were **full history**, **recent window**, **recursive GPT summary** and **version-aware current-policy ledger**. The temporal pilot additionally used **typed_retention_adapted**, an explicitly adapted constraint archive that retained source-labelled authorised policy events. This adaptation **is not** the original Knowledge Triage classifier/cascade/TypeDecompose/TypeRetrieve framework. The **ledger guard** reused the same GPT ledger response and applied a deterministic post-processing rule. It was a derived score, not an independent GPT decision or a new independent experimental arm.

The actual inference model recorded for the temporal pilot was `gpt-6.1-terra`. The v2 audit also verified genuine provider decision and compaction IDs. Low-cost model-generated advisory responses are method suggestions, not independent human scientific review.

### 3.3 Evidence and outcome rules

The original GitHub Actions artifacts were checked against ZIP digests, internal manifest hashes and prompt SHA-256 identities. The v3 archive yielded 432 scored observations, 360 genuine model decision responses and 20 genuine recursive compaction responses. Its guard contributed 72 derived decisions. The recorded 381-call provider ledger exceeds the 380 verified empirical response IDs by one; this extra accounting entry is **not evidence of a successful reviewer**. The original v3 workflow ended in `failure` when advisory review returned `EMPTY_ADVISORY_NO_APPROVAL`. Offline recovery did not retroactively change that workflow outcome.

Descriptive raw accuracy was calculated per arm. Temporal errors were separately grouped into revoked-rule wrongful rejections and newly active-rule missed enforcement. The candidate post-compaction paired contrast is reported only as the observed episode-level difference, without inferential tests. Zero errors are not evidence of equivalence.

### 3.4 Public-source and original-component checks

To investigate ecological provenance, a separate source-only check verified six publicly authored supersession pairs from pinned Python PEP and Rust RFC revisions, including their Git blob identities. These **are not human-adjudicated agent tasks**; no task-level gold labels or source-author participation were inferred.

For the upstream Knowledge Triage component, we used the authors' original `classify_instruction`, `KnowledgeBase.from_lines` and `type_compact` at source commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`. The released 327-file public sample was processed at four article-authored budget ratios (25%, 50%, 75%, 100%), using the upstream estimated-token heuristic. We counted `COMPACTION_UNSAFE` separately from feasible outputs. Exact retention of rows that the original regex itself classified as constraints is **not an independent semantic safety metric**. The experiment does not reproduce the paper's full cascade, published model comparisons or downstream benchmarks.

## 4. Results

### 4.1 Eight-episode v2 development pilot

| Condition | Correct / 144 | Raw accuracy | Unsafe approvals / 88 rejection opportunities | False rejections |
| --- | ---: | ---: | ---: | ---: |
| Full history | 144 | 100.0% | 0 | 0 |
| Recent window | 105 | 72.9% | 25 | 14 |
| Recursive GPT summary | 144 | 100.0% | 0 | 0 |
| Version-aware policy ledger | 144 | 100.0% | 0 | 0 |
| Ledger guard (derived) | 144 | 100.0% | 0 | 0 |

The candidate unsafe-approval episode-level contrast between recursive summary and ledger was **0.0000 in all eight episodes**. The experiment produced no observed advantage of the ledger over recursive summarisation.

### 4.2 Four-episode temporal v3 development pilot

| Condition | Correct / 72 | Raw accuracy | Stale-rule wrongful rejections / 16 | Missed new-rule enforcement / 16 |
| --- | ---: | ---: | ---: | ---: |
| Full history | 72 | 100.0% | 0 | 0 |
| Recent window | 52 | 72.2% | 0 | 0 |
| Recursive GPT summary | 72 | 100.0% | 0 | 0 |
| Adapted typed archive | 72 | 100.0% | 0 | 0 |
| Version-aware policy ledger | 72 | 100.0% | 0 | 0 |
| Ledger guard (derived) | 72 | 100.0% | 0 | 0 |

Each model arm contained 16 stale-revocation and 16 new-rule-enforcement probes; 12 revocation probes per arm occurred after at least two compactions. All 20 recent-window errors occurred in **control** cases, not the two policy-supersession probe categories. The four candidate episode-level differences between adapted typed retention and the ledger on post-compaction stale-rule rejection were **0, 0, 0, 0**. The original Actions run was **completed/failure** because its advisory stage failed, despite complete verified model observations. The separate recovery is evidence of observations, not of successful original review.

### 4.3 Original Knowledge Triage public-sample component sweep

| Estimated-token budget / original size | Feasible files / 327 | `COMPACTION_UNSAFE` | Feasible constraint-positive files | Conditional exact native-regex retention |
| --- | ---: | ---: | ---: | ---: |
| 25% | 308 | 19 | 210 | 1.000 |
| 50% | 323 | 4 | 224 | 1.000 |
| 75% | 326 | 1 | 227 | 1.000 |
| 100% | 327 | 0 | 228 | 1.000 |

These are 1,308 file-by-budget observations. The perfect **conditional** exact-text retention is consistent with TypeCompact's pinning design and only applies to feasible files with at least one regex-classified constraint. It cannot validate semantic safety or the regex classifier. The 19 infeasible files at 25% must not be counted as successful safe compressions.

### 4.4 Source provenance

Six external Python/Rust document pairs with explicit supersession relationships passed exact-commit and source/target blob verification. This establishes independent **document authorship and provenance**, not independent **experimental task construction, human action adjudication, or temporal authority semantics**.

## 5. Discussion

The dominant observation is a **ceiling effect** in the questions the temporal pilot was designed to discriminate. Every tested model condition handled all explicit temporal supersession probes correctly. The recent-window arm failed on controls, showing that short context can impair decisions in this synthetic workflow, but not demonstrating that it fails at policy revocation specifically. The adapted typed archive and version-aware ledger were indistinguishable in the observed temporal probes. The derived guard made no additional model calls and contributed no independent causal evidence.

These findings limit rather than confirm the proposed mechanism. Clear, template-like updates, fixed-oracle state transitions, explicit event authority and small numbers of episodes may make supersession too easy for the tested model. Moreover, the ledger's explicit access to current policy is not matched against the context-only arms. A future causal comparison would need equal source access, equal or justified context budgets, authority ambiguity, delayed and conflicting evidence, and independent human-labelled reference decisions. A full Knowledge Triage reproduction would require the original classification cascade and downstream benchmarks, not merely the pinned TypeCompact component.

The public sample sweep provides an independently executable diagnostic about feasibility. It demonstrates that hard constraint preservation can exceed a requested budget and that the upstream operator exposes this as `COMPACTION_UNSAFE`. It does **not** test the behaviour of downstream agents using these summaries and does not establish a novel improvement over the authors' published method.

## 6. Limitations and threats to validity

**Construct validity:** synthetic approvals and explicit updates are not authenticated organisational policies; the six public supersession documents have not been converted into independently adjudicated agent tasks. **Internal validity:** the policy ledger has unequal current-state information, the adapted typed comparator is not the original framework, and model conditions share episode trajectories. **Statistical validity:** four and eight independent episodes are insufficient for meaningful confirmation, and saturated zero-error contrasts do not support equivalence. **Operational validity:** hosted model and API versions may change; the v3 advisory stage failed and two completed independent reviewers are absent. **Measurement validity:** regex-derived constraint retention is circular as a classifier evaluation, and `COMPACTION_UNSAFE` is not a feasible safe result. **Novelty:** direct overlap with Knowledge Triage and Supersede remains unresolved. No real-world safety guarantee follows.

## 7. Reproducibility, ethics and provenance

The original v2 run [43624782133](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133) and its [original artifact](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133/artifacts/14125784623) were audited independently. The original v3 run [43640571248](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248) **failed**; its [original archived artifact](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248/artifacts/14131424960) and [offline recovery](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43643292807) preserve the factual evidence without re-running paid calls. The [public-source verification](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43652578796) and [original-component sweep](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43652663710) were no-cost offline checks. The latter artifact has SHA-256 `67720e90a5128bef7e113a9f3d0d55b9b0d4ff156de0c2ce3a48d792233ce362`.

All reported model decisions arise from synthetic tasks. No participant study or real personal data collection is claimed. The project used AI assistance for drafting and advisory methods; the named author remains responsible for checking source accuracy, originality and all claims. No external human peer review has been completed. The private confirmatory holdout was not opened by these activities.

## 8. Conclusion

Two audited GPT development pilots and an original-source component sweep establish a reproducible **exploratory negative/ceiling finding**: in the tested explicit synthetic supersession cases, neither a version-aware policy ledger nor an adapted typed archive improved on recursive GPT summarisation, and the proposed temporal error probes did not discriminate between systems. Original TypeCompact also returned infeasible statuses at aggressive budgets on its authors' public sample. The work supports further instrument design and open methodological discussion, **not a claim of safety superiority, scientific novelty, confirmatory validation or journal readiness**.

## References

1. Zerhoudi, S., Mitrović, J., & Granitzer, M. (2026). *The Compaction Cliff in Long-Running AI Agent Memory*. CIKM 2026. https://doi.org/10.1145/3799682.3840567
2. Patel, V. (2026). *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*. Preprint, arXiv:2606.27472. https://arxiv.org/abs/2606.27472
3. Kang, M., Chen, W.-N., Han, D., et al. (2026). *ACON: Optimizing Context Compression for Long-horizon LLM Agents*. PMLR 306, 55321–55375. https://proceedings.mlr.press/v306/kang26b.html
4. Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W., & Yu, D. (2025). *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. ICLR 2025. https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html
5. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL 12, 157–173. https://doi.org/10.1162/tacl_a_00638

## Editorial and scientific declaration

**Manuscript text completed as an exploratory report; publication scientific validation incomplete.** No human peer-review endorsements, prospective preregistration, confirmatory significance tests, novelty certification or journal submission are asserted. Any later manuscript claiming confirmatory effects requires a new independently justified protocol and genuinely separate evidence.
