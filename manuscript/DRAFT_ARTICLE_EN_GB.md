# When Agent Memory Becomes Unsafe: Constraint Preservation under Repeated Context Compaction

**Author:** Daniel Raaid  
**Status:** working, non-confirmatory manuscript; not a submitted or peer-reviewed paper.  
**Study ID:** WAMBU-001 (remediated v2). **Language:** British English.

## Abstract (provisional)

Persistent agent contexts must represent obligations that remain in force even after older observations are compacted. This study develops a reproducible synthetic workflow benchmark for examining how repeated GPT-generated context summaries interact with superseding, authorised constraints. Four GPT decision conditions include full history, short recent context, recursive memory summary and recursive summary with an independently updated policy ledger; a deterministic guard condition is derived without an additional GPT decision. The first development instrument was technically validated using actual provider calls, but its two-episode evidence cannot establish a causal or generalisable safety benefit. We introduce a remediated protocol that randomises scenario ordering, constructs the guard ledger independently of reference labels and plans episode-level paired inference. Confirmatory results are not yet available.

## 1 Introduction

Long-context access is sensitive to placement and distraction in controlled language-model tests [Liu et al., 2024]. Interactive assistant memory benchmarks such as LongMemEval explicitly test knowledge updates and temporal reasoning [Wu et al., 2025]. Agent Context Optimisation (ACON) has explored failure-guided context-compression policies in long-horizon agents [Kang et al., 2026], while CompactionBench evaluates repeated compaction across persistent coding tasks [Liu et al., 2026, preprint]. A recent EMNLP survey already identifies in-compression information loss and post-compaction access failures [Wang et al., 2026]. Thus the broader topics of memory failure and repeated compaction are **prior art**. The narrower open question we investigate is the systems-level change in unsafe raw approvals when current, explicitly authorised policy constraints remain independently accessible after recursive memory summarisation.

## 2 Methods and instrument

Episodes emulate a transaction-approval workflow with a finite balance and periodically superseded actor/category policy constraints. Each full/short/summary/ledger condition receives the same current request and fixed oracle-state history, with case modes randomised and balanced in blocks to avoid a turn-number shortcut. GPT summaries are recursively refreshed before turns 3, 6, 9, 12 and 15 during an 18-turn episode. Gold policy evaluation is separated from prompt preparation. The current ledger is reconstructed exclusively from public authorised events. A guard acts on that ledger and a GPT answer, not on the hidden reference action. The guard is a derived action, not an independent model observation.

The proposed primary estimand is the mean **episode-level** difference in unsafe raw approval rates among reference-reject requests after two or more genuine compactions, comparing summary-only with summary plus current policy ledger. Because the latter has privileged current-policy access, this is an architecture comparison, not an equal-information test of intrinsic LLM memory.

## 3 Historical development result (not pooled with revised instrument)

In a *previous* two-episode, 12-turn v1 development workflow, the GPT provider returned 96 real decision calls and six genuine compaction summaries; two separate low-cost model reviews were collected. The short-window condition made seven errors in 24 paired cases; full history, recursive summary and ledger conditions each recorded 24 correct raw decisions. The primary candidate contrast after two compactions was descriptively zero. The sample and deterministic v1 schedule cannot support statistical inference and **cannot be pooled as v2 confirmation**.

## 4 v2 results (not yet available)

Pending an independent exploratory run with 8 episodes and 18 turns. The dataset, provider response IDs, paired episode-level effects and evidence checks are required before numerical findings can be written in this section. No values may be inferred from simulated fixtures.

## 5 Proposed prospective independent confirmation

Subject to human freeze, 32 independent 18-turn episodes are proposed, with one two-sided paired episode sign-flip test (alpha 0.05) and 95% episode-bootstrap interval. The planning effect 0.10 and SD 0.20 are assumptions; null effects remain reportable. The private confirmation seed, author lock, reviewed design and original code/model hashes must remain protected until the author approves confirmation. No confirmatory inference is currently authorised.

## 6 Limitations and research ethics

Synthetic fixed-oracle trajectories omit state-dependent feedback, and ledger access deliberately differs from context-only baselines. Hosted model versions can change, and source methods/novelty require further independent human audit. Low-cost model-generated methodological reviews are advisory only. No claim of deployed safety, universal superiority, journal acceptance or human peer review is made.

## References: verified publisher metadata, source status not equal to human scientific approval

- Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. *Transactions of the Association for Computational Linguistics*, 12, 157-173. https://doi.org/10.1162/tacl_a_00638
- Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W., & Yu, D. (2025). LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory. *ICLR 2025*. https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html
- Kang, M., Chen, W.-N., Han, D., Inan, H. A., Wutschitz, L., Chen, Y., Sim, R., & Rajmohan, S. (2026). ACON: Optimizing Context Compression for Long-horizon LLM Agents. *Proceedings of Machine Learning Research*, 306, 55321-55375. https://proceedings.mlr.press/v306/kang26b.html
- Liu, B., Qiu, H., Goiri, I., Zhou, J., Fonseca, R., Bianchini, R., Lai, F., & Choukse, E. (2026). Benchmarking Long-Horizon Agent Context Compaction with CompactionBench. *Preprint*. https://www.microsoft.com/en-us/research/wp-content/uploads/2026/10/CompactionBench_preprint.pdf
- Wang, Y., Wang, Z., Shi, Y., Chen, S., Wang, X., Wang, Y., Shen, B., Li, L., Gu, X., McAuley, J., & Zeng, D. D. (2026). Context Compression for LLM Agents: A Survey of Methods, Failure Modes, and Evaluation. *EMNLP 2026*, 54460-54488. https://doi.org/10.18653/2026.emnlp-main.2396
