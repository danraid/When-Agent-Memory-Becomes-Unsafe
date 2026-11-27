# R07 | Literature novelty and overlap: primary-source-limited claim screening

**Date:** 2026-11-18. **Classification:** preliminary scientific citation/claim screening, not full independent peer review or exhaustive full-text method audit. R07 remains `PARTIAL` at most; this document is support for an author-reviewed literature section.

## Screened primary sources and overlapping contributions

| Work | Primary provenance | Author-established contribution or phenomenon | Overlap implication for WAMBU |
|---|---|---|---|
| Zerhoudi, Mitrović, Granitzer, *The Compaction Cliff in Long-Running AI Agent Memory*, CIKM 2026 | [Author GitHub release](https://github.com/searchsim-org/cikm26-knowledge-triage), [arXiv original](https://arxiv.org/abs/2608.22752), DOI 10.1145/3799682.3840567 | Knowledge Triage, TypeCompact, TypeDecompose, TypeRetrieve, semantic constraint preservation, budgets and downstream benchmarks | WAMBU cannot claim first-ever constraint pinning, safety-aware type retention or discovery of unsafe compaction budgets. The R02 reproduction is *another study's method*; source-aligned empirical replications are not a new operator |
| Patel, *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*, 2026 | [arXiv record](https://arxiv.org/abs/2606.27472) | Dynamic fact updates, gap between bounded memory and full-context currency, longitudinal degradation and RL environment | WAMBU cannot claim first demonstration that stale updates cause memory error or that memory upkeep is distinct from reasoning; its under-discriminating synthetic policy probes need to be described as an *instrument limitation* |
| Kang et al., *ACON: Optimizing Context Compression for Long-horizon LLM Agents*, ICML 2026 | [PMLR paper](https://proceedings.mlr.press/v306/kang26b.html), [official code](https://github.com/microsoft/acon) | Compression guideline optimisation driven by failures in long-horizon agent tasks, memory and observation compression | WAMBU cannot claim first systematic evaluation of compression under long trajectories or first failure-driven optimisation |
| Wu et al., *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*, ICLR 2025 | [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html), [official code](https://github.com/xiaowu0162/LongMemEval) | Memory extraction, multi-session reasoning, temporal reasoning, updates and abstention on long histories | WAMBU cannot claim first benchmark for memory updates, temporality or abstention |

## What the new WAMBU evidence actually adds

- Two small GPT pilots (8 and 4 independent episodes) reached a ceiling on explicit policy update probes, while the recent-window control lost information. This is an observed **measurement/instrument diagnosis**, not a positive effect or proof of architectural equivalence.
- A reproducible TypeCompact component feasibility audit exposes original operator statuses `COMPACTION_UNSAFE` at finite ratios and preserves failures; this is a replication/characterisation of existing work.
- Real Octen vendor model-ID execution and public source adversarial screening support a **limited reproducibility appendix** for the Knowledge Triage code. Different provider serving from the original authors is a material deviation.
- R01 contemporary authority sources document selected historical exceptions; correct operational actions are still unqualified, precluding a naturalistic accuracy claim.
- The adverse results (null contrasts, missing case gold, unmatched source information) should remain visible as limitations, not be turned into evidence that a new safety architecture is better.

## Candidate contribution requiring independent verification

**Possible narrowly framed thesis:** *Simple synthetic revocation/enforcement probes can have poor discriminatory validity for comparing long-running agent memory architectures even when baseline control failures occur; evaluation must separately audit source parity, authority, prospective task plausibility and budget infeasibility.* This is the manuscript's candidate measurement contribution, **not yet established as unique relative to all full texts**.

## Not yet completed

1. Passage-level method comparison of every cited source, including full technical appendices and code revisions, not only primary published abstracts/official descriptions.
2. Search and appraisal of newer or uncited 2025–2026 work on context compression, temporal memory, policy authority, and false-positive safety retention.
3. Independently qualified case/provenance review and model-run differences sufficient to evaluate a truly discriminative new instrument.
4. Independent scientific novelty verdict. AI agents can perform specialist source checks, but are not human referees.

**Scientific status:** R07 evidence screening advanced but not eligible for full `COMPLETE` status. **Editorial guard:** do not claim 'first', superiority, treatment-effect causality, full original framework replication, peer review or scientific approval.
