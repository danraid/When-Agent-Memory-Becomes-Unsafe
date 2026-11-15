# When Temporal Policy Updates Fail to Discriminate Agent Memories: Exploratory GPT Pilots, Compaction Feasibility and a Synthetic Instrument-Repair Audit

**Submission-candidate manuscript, not yet cleared for journal submission.** The public source repository is author-identifying; do not include its URLs or this file in an anonymous submission without a separate blinded supplement. **Research status:** exploratory, not independently reviewed or confirmed.

## Abstract

Evaluations of long-running AI agents often assume that preserving current constraints is sufficient to assess memory safety. We examine a narrower measurement problem: whether simple synthetic policy-supersession probes discriminate between memory strategies after repeated context compaction. Two independently archived GPT development pilots evaluated eight and four synthetic episodes, respectively. In the eight-episode pilot, full history, recursive summarisation and a version-aware ledger each answered 144/144 decisions correctly, compared with 105/144 for a recent-window baseline. In the four-episode temporal pilot, full history, recursive summarisation, an adapted typed archive and a version-aware ledger each answered 72/72 decisions correctly; recent window answered 52/72. Crucially, all conditions answered all 16 revocation and 16 new-restriction probes per arm correctly; the 20 recent-window errors occurred only in controls. The paired candidate ledger-versus-summary differences were zero in the observed episodes. A separate source-pinned component audit exercised the original Knowledge Triage TypeCompact operator on 327 public author sample files at four relative estimated-token budgets, yielding 19, 4, 1 and 0 infeasible files at 25%, 50%, 75% and 100%. These observations identify a measurement ceiling and a budget-feasibility distinction. They do not establish method equivalence, superiority, novel safety mechanisms or full framework replication. We also report the transparent construction and repair of a separate 16-case synthetic development instrument, explicitly excluding it from performance estimation. We derive specific requirements for more discriminative, independently adjudicated policy-update benchmarks.

## 1. Introduction

Long-running agents operate on histories that exceed practical context budgets. Recursive summaries, sliding windows, typed archives and external policy state can retain different information. A key failure mode is not merely losing a prohibition, but retaining a superseded prohibition or failing to apply a newly effective one. These errors have distinct decision consequences.

Prior work limits any broad novelty claim. Knowledge Triage studies type-sensitive preservation, protected constraints and infeasible compaction budgets [1]. Supersede investigates memory updates and documents ceiling effects on clear synthetic timelines [2]. ACON studies long-horizon context optimisation [3]; LongMemEval includes memory update tasks [4]. This article does not propose constraint pinning or memory supersession as first-of-kind concepts.

Our question is an *evaluation question*: did the available synthetic instruments actually discriminate memory approaches on policy revocation and new enforcement? We report the observed null contrasts, control errors, and an upstream component feasibility diagnostic, rather than promoting an unobserved advantage.

## 2. Research questions

**RQ1.** What differences were observed between memory conditions in two archived synthetic development pilots?

**RQ2.** Were the temporal revocation and newly effective restriction probes discriminative, or did all tested conditions saturate?

**RQ3.** How often does the pinned original TypeCompact operator signal an infeasible budget on the original authors' released public sample?

The two pilots are distinct exploratory instruments; they are not pooled or described as independent confirmatory replications.

## 3. Methods

### 3.1. Experimental units and data provenance

The eight-episode pilot used 18 decision turns per episode and four GPT decision arms. A fifth guard was deterministically derived from the ledger output, not separately sampled. The four-episode temporal pilot used 18 turns per episode, five GPT decision arms and a sixth derived guard. Episodes are the independent unit; turns within episodes are repeated observations. Reference actions were computed separately from agent-visible prompts. The original archived artifacts contain response identifiers, prompts and integrity manifests.

The temporal pilot's observed inference model was `gpt-6.1-terra`. The original temporal Actions workflow ended in **failure at the advisory-review stage**; empirical outputs were recovered and independently audited, not recreated by paid inference. Automated advisory calls do not count as human independent review.

### 3.2. Memory conditions

The shared conditions were full history, recent-window context, recursive GPT summary and a version-aware policy ledger. The temporal pilot added a typed-retention **adaptation**, not the original published Knowledge Triage framework. The deterministic guard reused the ledger decision, so it is not an independent GPT comparator.

The ledger received explicit current-policy information; this differs from the context information accessible to the other methods. Therefore the contrasts cannot isolate architecture from source access. We report raw decisions and avoid causal superiority claims.

### 3.3. Outcome definitions

The primary descriptive outcome is raw correct binary decisions per condition. We separately count wrongful approvals when the reference required rejection, wrongful rejections when approval was required, revocation-probe wrongful rejections and missed enforcement of newly active restrictions. For the candidate paired contrast, the independent unit is the episode; observed zero differences are reported without significance or equivalence inference.

### 3.4. Original TypeCompact component diagnostic

We used the original upstream `classify_instruction`, `KnowledgeBase.from_lines` and `type_compact` at Git revision `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`. All 327 files in the public author sample were processed at four article-defined budget ratios, 25%, 50%, 75% and 100% of the original estimated-token size. The operator's `COMPACTION_UNSAFE` status is reported separately; exact retention of native regex-classified constraint rows is a component diagnostic, **not** independent semantic recall. The full published cascade, retrieval benchmarks and downstream model comparisons were not reproduced.

### 3.5. Post-hoc synthetic instrument repair (not a validation sample)

A separate set of 16 AI-authored policy scenarios was prepared as development-only material. Two fictional reviewer-role annotations were generated in the same AI-assisted editorial process; they were not independent human raters, and their 14/16 agreement is not a reliability statistic. Four scenarios (005, 010, 015 and 016) required repairs to policy scope, effective chronology, revocation event separation and authority hierarchy. A versioned v2 casebook retains the original v1 unchanged. These cases were not included in either archived GPT pilot, were not tested on the protected confirmatory split and supply no new performance estimate. The author conditionally approved the development exercise subject to correction, but a new unconditional v2 sign-off has not been recorded.

### 3.6. Public-source provenance

Six pinned source/target document pairs from Python PEP and Rust RFC histories were independently verified at original Git commits and blob identities. They were not converted into labelled decision tasks and cannot substitute for independent case authorship or adjudication.

## 4. Results

### 4.1. Eight-episode development pilot

| Condition | Correct / 144 | Unsafe approvals / 88 reference-rejection opportunities | False rejections |
| --- | ---: | ---: | ---: |
| Full history | 144 | 0 | 0 |
| Recent window | 105 | 25 | 14 |
| Recursive summary | 144 | 0 | 0 |
| Version-aware ledger | 144 | 0 | 0 |
| Ledger guard (derived) | 144 | 0 | 0 |

The candidate unsafe-approval contrast between recursive summary and ledger was zero in each of eight independent episodes. No observed ledger advantage follows.

### 4.2. Four-episode temporal pilot

| Condition | Correct / 72 | Revocation wrongful rejections / 16 | Missed new-rule enforcement / 16 |
| --- | ---: | ---: | ---: |
| Full history | 72 | 0 | 0 |
| Recent window | 52 | 0 | 0 |
| Recursive summary | 72 | 0 | 0 |
| Adapted typed archive | 72 | 0 | 0 |
| Version-aware ledger | 72 | 0 | 0 |
| Ledger guard (derived) | 72 | 0 | 0 |

Every tested condition correctly handled all explicit policy-revocation and new-enforcement probes. All 20 recent-window errors occurred in control tasks. The observed episode-level adapted-archive-versus-ledger contrast for stale-rule rejection after compaction was zero in each of four episodes. The original run's advisory-review failure remains an operational limitation.

### 4.3. Original-source TypeCompact feasibility

| Estimated-token budget | Feasible / 327 | `COMPACTION_UNSAFE` | Feasible files with native regex constraints | Conditional exact retention |
| --- | ---: | ---: | ---: | ---: |
| 25% | 308 | 19 | 210 | 1.000 |
| 50% | 323 | 4 | 224 | 1.000 |
| 75% | 326 | 1 | 227 | 1.000 |
| 100% | 327 | 0 | 228 | 1.000 |

The total is 1,308 file-budget observations. The perfect *conditional* retention is an expected consequence of the original operator's pinning logic, not a novel safety result or proof that the regex identifies every meaningful constraint. Infeasible outputs are not successful safe compression.

### 4.4. Synthetic instrument quality audit

The 16-case development instrument exposed four under-specified or internally inconsistent policy situations, which were repaired in a separately versioned casebook. The earlier two fictional reviewer-role reports described the original v1 cases, not a new independent assessment of v2. No claims of human adjudication, independent validation or prospective confirmatory success arise from this editorial exercise. The casebook is not pooled with the two GPT pilots or the TypeCompact component audit.

## 5. Discussion

The temporal probes showed a complete ceiling effect. The recent-window baseline's control failures indicate that the overall instrument can expose some information-loss errors, but those failures do **not** demonstrate a policy-supersession-specific problem. This distinction matters: reporting aggregate accuracy alone would falsely imply that the temporal hypothesis was tested discriminatively.

The zero ledger-versus-summary contrast is an observed null finding, not evidence that the methods are equivalent. The small independent episode counts, shared synthetic structure and unequal access to current-policy state prevent a causal or confirmatory interpretation.

The original-source TypeCompact check separately illustrates a feasibility boundary. Constraint preservation may exceed a finite compression budget, and the operator can signal this rather than silently discard protected text. This is a diagnostic of an existing method, not an improvement over it.

The source-provenance checks provide a path towards naturalistic policy-update cases but no adjudicated gold actions. A future discriminative evaluation should distinguish publication time, effective time, issuer authority, supersession scope and revocation, with human adjudicators blinded to model outcomes. The methods must have matched evidence and documented context budgets.

## 6. Threats to validity

**Construct:** synthetic transactions and explicit updates may be substantially easier than naturalistic operational policies. The 16 additional development cases were constructed and revised post-hoc and were not evaluated by genuine independent reviewers. **Internal:** unequal policy-state access and an adapted, non-original typed comparator. **Statistical:** only eight and four independent episodes, no preregistered confirmatory contrast, and no justified equivalence test. **Measurement:** regex-classified constraints are not independently labelled semantic safety constraints; unsafe budgets must remain separate. **Operational:** provider/model version changes and a failed advisory stage in the original temporal workflow. **Novelty:** direct prior-art overlap remains and has not been cleared by independent human scientific review.

## 7. Reproducibility and responsible reporting

Original experiments and component outputs were archived with immutable workflow identifiers, response IDs and file hashes. A separate author-identifying provenance ledger is maintained for internal audit. For double-blind review, a future release must provide a genuinely anonymised supplement rather than linking the named public GitHub repository. No real participants or independently human-labelled case decisions are claimed. The author's conditional approval of the synthetic casebook is an editorial development decision, not external validation. No model evaluation was performed on the repaired v2 casebook. Generative AI assisted drafting and automated advisory analysis; no human peer-review endorsement is inferred. No confirmatory holdout was accessed.

## 8. Conclusion

Across two small, provenance-audited synthetic development pilots, explicit policy-update probes did not distinguish memory methods, even though a recent-window baseline failed on controls. A separate pinned TypeCompact component sweep identified budget infeasibility in part of the original authors' public sample. A 16-case synthetic instrument was revised for clarity but has not undergone independent adjudication or confirmatory model evaluation. These are limited descriptive and methodological observations, not evidence of a new superior memory architecture. Future work requires independently adjudicated naturalistic cases, source-matched comparators and a prospective statistical design.

## References

[1] Zerhoudi, S., Mitrović, J. and Granitzer, M. (2026). *The Compaction Cliff in Long-Running AI Agent Memory*. CIKM 2026. DOI: 10.1145/3799682.3840567.

[2] Patel, V. (2026). *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*. Preprint. arXiv:2606.27472.

[3] Kang, M. et al. (2026). *ACON: Optimizing Context Compression for Long-horizon LLM Agents*. PMLR 306, 55321–55375.

[4] Wu, D. et al. (2025). *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. ICLR 2025.

[5] Liu, N. F. et al. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics 12, 157–173.

## Author and ethics declarations (verification pending)

This work reports synthetic agent tasks and software experiments, not recruitment or intervention with human research participants. Whether a formal exemption statement is required depends on the selected journal and institution. AI assistance was used in drafting, case generation and simulated editorial roleplay; all simulated roles are explicitly non-human. Funding, conflicts of interest, affiliation, author identity and contact, data licensing, repository anonymisation and the journal-specific AI disclosure must be confirmed by the author before submission. No independent human review is claimed.

## Submission disclosure

This is a **submission-candidate exploratory scientific article**, not an approved anonymous submission: an author-identifying public repository exists and a complete anonymous evidence supplement, independently verified methods, journal template, disclosures and final author sign-off are outstanding. No scientific acceptance or peer review is claimed.
