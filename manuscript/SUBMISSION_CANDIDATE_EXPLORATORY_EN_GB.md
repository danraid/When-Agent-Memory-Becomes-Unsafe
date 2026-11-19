# When Temporal Policy Updates Fail to Discriminate Agent Memories: Exploratory GPT Pilots, Compaction Feasibility and a Synthetic Instrument-Repair Audit

**Author-requested major revision (GitHub issue #50), not cleared for journal submission.** The public source repository is author-identifying; do not include its URLs or this file in an anonymous submission without a separate blinded supplement. **Research status:** exploratory, not independently reviewed or confirmed.

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

### 3.7. Evidence qualification and AI-review missingness (post-pilot; no new performance claims)

Eight public CPython/Rust code-change cases were subsequently assembled for methodological screening. The P07f v2 AI-only board produced 24 first-round model responses with 22 strict-schema/evidence-linkage valid outputs and six valid same-case adversarial syntheses from eight attempted cases. The two first-round failures comprised invalid JSON and a non-existent case-specific evidence identifier; two cases lacked a valid synthesis. All six valid syntheses requested additional contemporaneous authority or exception sources. These are counts of format and source-linkage validity, **not** independent scientific agreement, action correctness, or policy gold. Roles were simulated by models, not qualified human adjudicators. The original P07f v2 paid workflow ended with a detached-auditor implementation failure; its unchanged provider outputs were subsequently replayed successfully without new inference. The P10 scientific advisory's four strict-invalid initial reviews and schema-invalid chair response are retained as dissenting, nonbinding critique, not approval.

The historical GitHub state of a code-change request (merged or closed) cannot be used as normative authorisation truth. The current corpus does not establish the applicable event-time policy/exception/actor action for every case. Consequently none of the eight cases is admitted to an operational agent-memory-safety accuracy denominator. These later screens were not part of either archived pilot and did not touch the confirmatory holdout.

### 3.8. Matched-information requirement and prospective design boundary

The current-policy ledger, full history, recent window, recursive summary and adapted typed archive are **systems conditions with non-equivalent information access**. Existing descriptive differences cannot identify a memory-compression-specific treatment effect. A future architecture-specific comparison must explicitly audit per-turn authorised source visibility, source revision/effective date, token budgets, identical base model/settings, and evaluator-only outcome isolation before predeclaring any causal estimand. No such matched-information empirical comparison is claimed here. Prospective independent episode counts, uncertainty intervals, missing-data rules, and multiplicity must be fixed before accessing a holdout. Zero differences across eight/four development episodes do not justify equivalence or non-inferiority.

### 3.9. Post-pilot source-aligned Knowledge Triage phrasing diagnostic (exploratory)

After the archived development pilots, the exact original source release at `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4` supplied a 200-item, author-constructed adversarial safety-rule corpus (50 base rules expressed imperatively, declaratively, conditionally and passively). We executed the original source-defined regex classifier, the unchanged original cascade with live vendor `octen-embedding-8b` embeddings and OpenAI `gpt-5.4-mini` adjudication, and the unchanged original `SafetyMargin` method. A 40-item development subset and the disjoint remaining 160 items were separately archived and reconstructed under a no-call source-identity audit, which passed for all 200 items with zero missing or duplicate source IDs. All 160 additional method calls completed without recorded case failures. The vendor API is **not proven identical to the authors' experimental endpoint**, and this study does not reproduce the publication's other corpora, retrieval/compaction budgets or downstream benchmarks.

These labels were deliberately constructed by the original authors as safety-rule examples, rather than independently validated action-correctness gold for real agents. Consequently we report source-defined category retention as a descriptive classifier diagnostic only; it does not enter the agent-memory safety results, estimate causal risk, or qualify R01 real-case decisions.

### 3.10. Common-authority-source development experiment (post-pilot R03)

We conducted a subsequent development-only comparison using two independently seeded, eighteen-step policy-update episodes. On every paired decision, the recursive-summary and version-aware-ledger arms received the **identical complete set of public authoritative source events and the identical request**. The summary arm additionally had a recursive compressed representation; the ledger arm received a deterministic policy state derived only from those same model-visible events. The gold action remained separate from both prompts and was evaluated after each response. A detached replay verified original source packet hashes, complete pairing and unique provider response identities. The design addresses the earlier *unequal source-access* confound but not unequal computation, memory representation, source interpretation or input token budgets. It is not a valid isolated causal test of memory architecture.

### 3.11. Prospective development-only temporal-authority stress instrument

To investigate repeated ceiling effects, we separately predeclared a development instrument with two independently seeded 18-question episodes, nine synthetic oracle approvals and nine rejections per episode, and three source-matched arms: a common original signed event packet only; the same packet plus recursive summary; and the same packet plus a deterministic time-aware ledger. Questions covered authorised policy supersession, limited-time exceptions, revocation, historical effective-time decisions, critical-risk precedence and unauthorised messages. Case presentation order was shuffled before model inference. Reference actions were withheld from prompts and evaluated after responses. The comparison matched *source availability*, not model-side computation, context representation or token budgets. Synthetic signatures and oracle actions are not naturalistic institutional evidence.

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

### 4.5. Original public 200-item phrasing diagnostic (source-defined categories only)

| Phrasing (50 each) | Source-defined constraint retained by regex | Original cascade (Octen + GPT) | Original SafetyMargin |
| --- | ---: | ---: | ---: |
| Imperative | 50/50 | 50/50 | 49/50 |
| Declarative | 0/50 | 20/50 | 46/50 |
| Conditional | 19/50 | 50/50 | 48/50 |
| Passive | 40/50 | 48/50 | 50/50 |
| **Total / 200** | **109/200** | **168/200** | **193/200** |

The 40-item stratified pilot had suggested 60% declarative retention by the cascade; the complete original public 200-item corpus yields 40%. SafetyMargin retained 92% of source-defined declarative rules. These fractions concern researcher-authored class labels, not adjudicated downstream agent decisions, and do not justify a superiority or equivalence inference. The exact results, original source hashes, provider model identifiers, immutable GitHub Actions runs, detached 40+160 audit, and item-level discrepancies are recorded in the separately audited R02 appendix. The full Knowledge Triage paper's published behavioral benchmarks remain unreproduced.

### 4.6. Shared-source development comparison: accuracy ceiling persisted

Each arm produced 36/36 correct raw decisions, including eight correct revocation cases and eight correct newly enforced restrictions, with no invalid responses. The 82 provider calls comprised 72 decisions and ten shared recursive compactions. Decision-call input token usage was **14,218** for recursive summary with the common authority packet and **8,542** for the derived-ledger arm with the identical packet, demonstrating that the available context budgets were not matched. An offline no-provider-call audit confirmed the paired source and evaluator separation. This is a further **negative discriminability** observation, not proof of memory-method equivalence or superiority; only two episodes were studied.

### 4.7. Prospective temporal-authority development stress: a second accuracy ceiling

The bounded live development run completed **116 real provider calls** (108 decisions and eight compactions), with no provider errors. All three arms returned **36/36 correct raw actions**, no invalid outputs and zero paired disagreements. Recorded decision-call input tokens were **10,810** for the source-only arm, **19,342** for recursive summary and **12,054** for the derived temporal ledger. An independent zero-inference replay of the original questions, event-source hashes, oracle sidecar, response IDs and usage passed without missing evidence. No model advantage can be inferred from the identical binary results. The new scenario complexity did not generate an observable discriminative signal, and this must be reported as a negative instrument-qualification result rather than a positive safety finding. The real-world R01 qualification and scientific comparison remain incomplete.

## 5. Discussion

The temporal probes showed a complete ceiling effect. The recent-window baseline's control failures indicate that the overall instrument can expose some information-loss errors, but those failures do **not** demonstrate a policy-supersession-specific problem. This distinction matters: reporting aggregate accuracy alone would falsely imply that the temporal hypothesis was tested discriminatively.

The zero ledger-versus-summary contrast is an observed null finding, not evidence that the methods are equivalent. The small independent episode counts, shared synthetic structure and unequal access to current-policy state prevent a causal or confirmatory interpretation.

The original-source TypeCompact check separately illustrates a feasibility boundary. Constraint preservation may exceed a finite compression budget, and the operator can signal this rather than silently discard protected text. This is a diagnostic of an existing method, not an improvement over it.

The source-provenance checks provide a path towards naturalistic policy-update cases but no adjudicated gold actions. A future discriminative evaluation should distinguish publication time, effective time, issuer authority, supersession scope and revocation, with event-time source provenance and independently justified action labels assessed without access to model outcomes. The author has elected to use AI-only specialist simulations during development; these cannot be presented as human adjudication or third-party peer review. The methods must have matched evidence and documented context budgets.

## 6. Threats to validity

**Construct:** synthetic transactions and explicit updates may be substantially easier than naturalistic operational policies. The 16 additional development cases were constructed and revised post-hoc and were not evaluated by genuine independent reviewers. **Internal:** original pilots used unequal policy-state access and an adapted, non-original typed comparator. The follow-up R03 study repaired unequal *source* access but retained unequal derived computation, representations and token budgets. **Statistical:** only eight and four independent episodes, no preregistered confirmatory contrast, and no justified equivalence test. **Measurement:** regex-classified constraints are not independently labelled semantic safety constraints; unsafe budgets must remain separate. The additional 200 author-authored phrasings measure type-retention relative to source-designed examples, not independent normative safety. Differences in the Octen vendor serving environment from the original authors' endpoint remain unquantified. **Operational:** provider/model version changes and a failed advisory stage in the original temporal workflow. **Novelty:** direct prior-art overlap remains and has not been cleared by independent human scientific review.

## 7. Reproducibility and responsible reporting

Original experiments and component outputs were archived with immutable workflow identifiers, response IDs and file hashes. A separate author-identifying provenance ledger is maintained for internal audit. For double-blind review, a future release must provide a genuinely anonymised supplement rather than linking the named public GitHub repository. No real participants or independently human-labelled case decisions are claimed. The author's conditional approval of the synthetic casebook is an editorial development decision, not external validation. No model evaluation was performed on the repaired v2 casebook. Generative AI assisted drafting and automated advisory analysis; no human peer-review endorsement is inferred. No confirmatory holdout was accessed.

## 8. Conclusion

Across two small, provenance-audited synthetic development pilots, explicit policy-update probes did not distinguish memory methods, even though a recent-window baseline failed on controls. A separate pinned TypeCompact component sweep identified budget infeasibility in part of the original authors' public sample. A 16-case synthetic instrument was revised for clarity but has not undergone independent adjudication or confirmatory model evaluation. These are limited descriptive and methodological observations, not evidence of a new superior memory architecture. Future work requires source-qualified naturalistic cases with defensible event-time action labels, source-matched comparators and a prospective statistical design. AI-only specialist role simulations can support screening but cannot independently establish human expert ground truth.

## References

[1] Zerhoudi, S., Mitrović, J. and Granitzer, M. (2026). *The Compaction Cliff in Long-Running AI Agent Memory*. CIKM 2026. DOI: 10.1145/3799682.3840567.

[2] Patel, V. (2026). *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*. Preprint. arXiv:2606.27472.

[3] Kang, M. et al. (2026). *ACON: Optimizing Context Compression for Long-horizon LLM Agents*. PMLR 306, 55321–55375.

[4] Wu, D. et al. (2025). *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. ICLR 2025.

[5] Liu, N. F. et al. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics 12, 157–173.

## Author and ethics declarations (verification pending)

This work reports synthetic agent tasks and software experiments, not recruitment or intervention with human research participants. Whether a formal exemption statement is required depends on the selected journal and institution. AI assistance was used in drafting, case generation and simulated editorial roleplay; all simulated roles are explicitly non-human. Funding, conflicts of interest, affiliation, author identity and contact, data licensing, repository anonymisation and the journal-specific AI disclosure must be confirmed by the author before submission. No independent human review is claimed.

## Author-directed major revision and outstanding objections

The author requested major corrections on 17 November 2026 (issue #50), without authorising either confirmatory release or external submission. The machine-readable R01–R08 evidence-status ledger records outstanding qualifications on event-time policy labels, faithful comparator replication, information-parity analysis, discriminative power, provider failure/missingness, temporal source provenance, novelty, and editorial disclosures. The R01–R08 ledger is a **repair-tracking artifact**, not independent validation. The manuscript is not an accepted, approved, or confirmatory result, and no automatic AI panel or CI success changes that.

## Submission disclosure

This is a **submission-candidate exploratory scientific article**, not an approved anonymous submission: an author-identifying public repository exists and a complete anonymous evidence supplement, independently verified methods, journal template, disclosures and final author sign-off are outstanding. No scientific acceptance or peer review is claimed.
