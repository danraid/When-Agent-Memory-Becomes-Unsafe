# WAMBU-001 | New high-overlap prior art / novelty gate
Date: 14 November 2026

## DECISION: BLOCK CONFIRMATORY FREEZE / JOURNAL NOVELTY CLAIMS
This is a science-validity gate, not a CI or Python error. The v2 real pilot remains **exploratory engineering evidence** and may finish normally. No author approval or private confirmatory seed is touched. Do not label the existing draft novel or publication-ready.

### Major overlapping peer-reviewed work (missed in initial five-source screen)
Zerhoudi, S., Mitrovic, J., & Granitzer, M. (2026). *The Compaction Cliff in Long-Running AI Agent Memory*. **Proceedings of the 35th ACM International Conference on Information and Knowledge Management (CIKM 2026)**, Rome, Italy, 7-11 November 2026. DOI: [10.1145/3799682.3840567](https://doi.org/10.1145/3799682.3840567).
- [Full author version](https://arxiv.org/abs/2608.22752)
- [Open implementation](https://github.com/searchsim-org/cikm26-knowledge-triage)
- [ACM reference text and bibliography](https://github.com/searchsim-org/cikm26-knowledge-triage#readme)

The paper empirically studies retention of exact safety rules over **five consecutive compaction rounds**, including downstream behavioural outcomes. It introduces *Knowledge Triage* with type-aware compaction, decomposition and retrieval, a verifier, and constraints pinned ahead of relevance. It already makes the broad claim that uniform compaction can lose safety-critical instructions and typed retention can protect them. Merely showing that a pinned external ledger outperforms a lossy summary would be **substantially overlapping**, not an adequate novelty claim.

### Other adjacent work
- Kang et al., ACON (ICML 2026), optimises context compression for long-horizon agents: https://proceedings.mlr.press/v306/kang26b.html
- Sun et al., *Scaling Long-Horizon Agent via Context Folding* (ICML 2026), studies agent context folding: https://proceedings.mlr.press/v306/sun26x.html
- Wu et al., *LongMemEval* (ICLR 2025), includes knowledge updates: https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html
- Wang et al., EMNLP 2026 survey, already documents failure categories: https://aclanthology.org/2026.emnlp-main.2396/

### Potentially distinct, still unproven contribution
Measure *temporal policy supersession* rather than static safety-rule retention: whether an authorised revocation, replacement or scope change takes effect at the correct time under repeated recursive compaction, without causing obsolete restrictions to persist. An experimental design would need:
1. A task corpus with both **enforcement of newly active** and **revocation of previously active** constraints, including ambiguous/conflicting-order cases.
2. A **genuine Knowledge Triage reproduction** (pinned code and version), or an independently implemented *clearly labelled simplified typed-retention comparator* if exact reproduction cannot be achieved, plus full history, recent window, recursive summary and authoritative policy ledger.
3. Equalised token-budget and policy-source-provenance comparisons **as secondary ablations**, in addition to the original systems-level contrast.
4. A preregistered primary estimand on *temporally correct action* after supersession, with episode-level independence and locked outcome rules.
5. An explicit prior-art/novelty comparison matrix and human methods review before changing the current 32-episode proposal from draft to frozen.

### Status and invalidation boundaries
- The already initiated v2 eight-episode pilot at [run 43624782133](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133) can serve as feasibility only.
- **Scientific confirmatory plan remains DRAFT and BLOCKED ON NOVELTY/METHOD REVISION.**
- Do not adapt the v2 confirmatory hypothesis after inspecting any confirmatory sample, do not fabricate a human signature, do not mislabel model review as peer review.
- The separate private confirmatory seed is untouched.
