# When Agent Memory Becomes Unsafe: Temporal Policy Supersession After Repeated Context Compaction

**Status:** Research manuscript in progress. **NOT a submitted, preregistered or independently peer-reviewed article.** Results marked “pending” must not be filled with predicted model behaviour.

## Abstract (working)

Persistent agents must distinguish restrictions that remain effective from those formally replaced or revoked. We develop a paired synthetic workflow benchmark comparing full histories, short recent context, recursive GPT summarisation, an adapted type-aware constraint archive, and a version-aware external policy ledger. A previous eight-episode technical pilot achieved 100% raw accuracy with full history, recursive summarisation and an explicit policy ledger; short-window context achieved 72.9% raw accuracy. Thus, no superiority of the policy ledger over recursive summarisation was observed in the initial exploratory experiment. We propose a revised temporal-supersession instrument that separates wrongful persistence of revoked constraints from failure to enforce newly active rules. The design incorporates source-derived policy ledgers, unchanged model responses for post-processing guards, episode-level independence and blinded advisory review. A forthcoming independent pilot will assess the feasibility and discrimination of the revised cases. The results do not yet establish novelty, generalisability or a confirmatory effect.

## 1. Introduction

Long-horizon language-model agents increasingly compress observations and histories to remain within context limits. This creates a conflict between lossy episodic summarisation and exact retention of operational constraints. However, retaining a rule is not always enough: a once-authoritative rule may become invalid after a later authenticated policy amendment. Reliable agency therefore requires both faithful enforcement of current restrictions and timely cessation of obsolete restrictions.

Substantial prior work addresses these problems. *Knowledge Triage* (Zerhoudi et al., 2026) formalises type-aware preservation, verification and retrieval of safety constraints. *Supersede* (Patel, 2026, preprint) studies the memory-update gap and warns that clear templated supersession timelines may saturate frontier models. ACON (Kang et al., 2026) optimises long-horizon agent context compression more broadly. LongMemEval (Wu et al., 2025) explicitly includes knowledge updates. Consequently, our contribution cannot be the generic assertion that pinned constraints survive compaction or that stale memories exist; it must be a supported comparison of precise authority and action semantics.

## 2. Research questions and hypotheses

RQ1 (exploratory): Under repeated GPT compaction, do different systems distinguish a formally **revoked** policy from a currently active restriction when making consequential binary decisions?

RQ2 (exploratory): Is an external current-policy ledger more reliable than an *adapted typed-retention* baseline at accepting actions that an old rule would wrongly reject, while retaining enforcement of newly active rules?

RQ3: What are the costs in input tokens and additional compactor work, and what changes when a deterministic policy guard acts on the same raw GPT response?

The formal estimand and power assumptions remain **proposals**, not preregistered, and no hypothesis is presumed true.

## 3. Methods

### 3.1 Historical v2 pilot

Eight independent seeded episodes each supplied 18 synthetic policy-request turns. Four actual GPT decision arms were paired with a fifth deterministic guard derived from the ledger arm, plus five genuine GPT recursive compactions per episode and two advisory model reviews overall. The oracle reference trajectory was held constant between arms. The gate checked real provider IDs and usage, split isolation and SHA-256 evidence hashes. All eight independent episode-level differences between the recursive summary and pinned-ledger arms were zero on the proposed unsafe-approval contrast.

### 3.2 Proposed v3 supersession pilot

For each independent episode, authorised actor and category restrictions change at turns 4, 8, 12 and 16, following a canonical event stream. Newly changed actions are deliberately tested in two causal directions: requests that would have violated a revoked restriction but now must be approved; requests newly restricted by a policy update that must be rejected. An independently constructed reference policy is only accessible to the post-response evaluator. Model inputs contain authorised source events, scenario requests and distractors but no expected answers or probe labels.

The five paid inference arms are full history, recent window, recursive summary, adapted type-aware constraint archive, and version-aware external ledger. A sixth derived guard is applied to the ledger arm's **same** raw GPT response. Compactions occur every three turns; prompt length and usage are logged. The type-aware comparator preserves authorised constraint events but **does not reproduce** the complete official Knowledge Triage implementation, which includes classification, additional context-management operators and a verifier.

### 3.3 Analysis

Episode is the independent unit. The candidate primary endpoint is the per-episode frequency of wrongful rejections of genuinely revoked restrictions following at least two compactions. A secondary endpoint is the frequency of approvals in violation of newly active restrictions. We report actual denominators and raw model accuracy by arm and avoid treating 18 within-episode turns as independent trials. A confirmatory test requires a separately locked protocol, a suitable independent sample-size justification and an untouched holdout.

## 4. Results

### 4.1 Historical v2 exploratory observations (8 episodes; 144 scored turns per arm)

| Condition | Raw accuracy | Unsafe approvals / 88 opportunities | False rejections |
| --- | ---: | ---: | ---: |
| Full authorised history | 100% | 0 | 0 |
| Short recent window | 72.9% | 25 | 14 |
| Recursive GPT summary | 100% | 0 | 0 |
| External current-policy ledger | 100% | 0 | 0 |
| Ledger plus derived guard | 100% | 0 | 0 |

The 25 short-window unsafe approvals occurred on a total of 88 rejection-eligible steps. No raw model improvement is attributable to the guard because the underlying ledger response was reused. **The candidate primary difference between recursive summary and ledger was zero** across all eight paired independent episodes. These results cannot establish superiority or equivalence.

### 4.2 Temporal v3 independent pilot

**PENDING DATA.** Insert only verified model observations from the v3 GitHub Actions artifact after the run completes. If ceiling performance persists across arms, describe that null finding and redesign the evidence question before confirmation. Never substitute simulated results.

## 5. Discussion and limitations

The v2 ceiling result is informative mainly about the *instrument*: explicit templated policy updates may be unchallenging for the GPT model used. Its outcomes do not establish a safety advantage for external memory over successful recursive summarisation. The v3 design deliberately measures both false rejection due to an obsolete policy and approval contrary to a new policy, but remains synthetic, uses fixed reference trajectories and differs in the amount of authoritative information exposed across arms. Its adapted typed archive is **not** a faithful official Knowledge Triage reproduction. Independent naturalistic cases, an official implementation comparator and stronger statistical replication are needed before strong causal or practical claims.

## 6. Reproducibility, provenance and ethical considerations

All API calls require positive opt-in and finite execution bounds; cost reporting is explanatory, not an official API invoice. Prompts never contain hidden policy labels. Original response IDs, token accounting and SHA-256 evidence identities are stored in GitHub Actions artefacts, with original files retained subject to platform expiration. All policies, actors and scenarios are synthetic. Human approval of a frozen statistical protocol and scientific interpretation is separate from LLM-generated advisory reviews. This work has no human subject data in its current pilot, and it must not be framed as real-world safety assurance.

## References (verified primary records)

1. Zerhoudi, S., Mitrović, J., & Granitzer, M. (2026). *The Compaction Cliff in Long-Running AI Agent Memory*. Proceedings of CIKM 2026. DOI: 10.1145/3799682.3840567. https://arxiv.org/html/2608.22752 (full text audited for methods).
2. Patel, V. (2026). *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*. arXiv:2606.27472v1. https://arxiv.org/html/2606.27472 (full text audited for methods; preprint).
3. Kang, M., Chen, W.-N., Han, D., et al. (2026). *ACON: Optimizing Context Compression for Long-horizon LLM Agents*. ICML, PMLR 306, 55321–55375. https://proceedings.mlr.press/v306/kang26b.html (published metadata/abstract verified).
4. Wu, et al. (2025). *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. ICLR 2025. https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html (metadata/abstract verified; full method not yet audited).

## Preparation for journal review

**Target under consideration:** Transactions on Machine Learning Research (TMLR), not yet selected or submitted. The authors must prepare the mandatory anonymised official TMLR LaTeX template, ensure OpenReview profiles, conflicts/ethics declarations and an AI-assistance disclosure footnote, and verify the evidence against the claims. See `manuscript/TMLR_READINESS.md`.
