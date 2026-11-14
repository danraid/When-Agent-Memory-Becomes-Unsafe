# WAMBU-001 | Independent v2 evidence audit

**GitHub run:** https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133

**Original artifact:** https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133/artifacts/14125784623 (90-day retention; downloaded for audit).

The `empirical/manifest.json` listed 4 files and `advisory/manifest.json` listed 1. Each file's SHA-256 and size matched the downloaded bytes. This is an audit of **observed technical evidence**, not an independent replication of the GPT model behaviour. The author-approved confirmatory holdout was never accessed.

## Observed counts

- 8 independent pilot episodes, 18 turns each.
- 576 genuine model decision calls across 4 paid conditions, 40 genuine recursive compaction calls and 2 advisory review calls.
- 616 study calls (decision + compaction) before reviews; the analysis contains 720 **scored** decisions, including 144 guard derivatives from previously recorded raw decisions. The 144 guards are **not separate independent GPT responses**.
- Full history: 144/144 correct; 0 unsafe approvals out of 88 reference rejects.
- Short recent window: 105/144 correct (72.9%); 25 unsafe approvals out of 88 rejects, plus 14 false rejections.
- Recursive GPT summary: 144/144 correct; 0 unsafe approvals out of 88 rejects.
- External pinned ledger: 144/144 correct; 0 unsafe approvals out of 88 rejects.
- Pinned ledger plus derived deterministic guard: 144/144 correct; no raw GPT skill improvement can be claimed from this post-processing arm.
- Paired episode-average candidate contrast, recursive summary minus pinned ledger after two or more compactions: **0.0000**. Eight episode-level differences were exactly zero.

## Interpretation and scientific validity

The v2 result cannot establish any superiority of the pinned-ledger intervention against recursive summary. Repeated decisions within eight episodes are correlated. All cases use synthetic, explicitly stated policies and a reference trajectory held fixed by the oracle. Full history, summary, and external ledger differ in informational privilege and token usage. The resulting 100% performance in multiple conditions indicates **ceiling effects** and limited discrimination, also cautioned by Patel (2026) on templated supersession timelines.

The 2 model-generated reviewer notes are consultative and do not constitute independent peer review. A separate reviewer noted unequal sources across baselines and case dependence. The review sampling manifest says it was depth-stratified and paired, while one reviewer described lexicographic selection: the discrepancy should be treated as unreliable model commentary, not ground truth about the actual code path. No manuscript should cite model commentary as observed methods.

**Status: V2_TECHNICAL_PILOT_COMPLETE; SCIENTIFIC_SUPERIORITY_NOT_DEMONSTRATED; CONFIRMATION_NOT_RUN.**
