# P07c: eight authentic public governance events and three AI-simulated specialist reviews

**Evidence cutoff:** 16 November 2026. **Scientific status:** exploratory retrospective case intake; **partial** original AI-output validity, **completed** separate detached evidence audit, **zero** genuine human expert adjudications. Not a P07b naturalistic *agent-authorisation* corpus, not a confirmatory study, not a complete Knowledge Triage replication.

## Reproducible original evidence

- [Merged PR #37](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/pull/37), source/workflow commit `a931e93d66c551208b53187afdbf53832ddf52e1`.
- [Original OpenRouter real-data workflow #43976232478](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43976232478) **FAILED** overall due to 7 strict simulated-AI output-validation errors, not failed public-source retrieval.
- [Original full public-source evidence artifact #14280444058](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43976232478/artifacts/14280444058): 8 public pull-request metadata snapshots, timestamped public issue comments, factual outcome sidecar and source/evidence checksums. Models saw only the separate [blind-input artifact #14280598708](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43976232478/artifacts/14280598708), not outcome sidecar.
- [Original AI-only response archive #14281156451](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43976232478/artifacts/14281156451): 24/24 provider response IDs, exactly 24 paid-call reservations (not necessarily a billing count), original raw content, schema failures and model metadata retained.
- [Zero-new-call detached audit #14280817916](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43976232478/artifacts/14280817916): standalone audit job **SUCCESS**; source and review hashes verified (7 source/reviewer files in total), source/response prompt pairing checked, original public PR outcomes reconstructed and summaries independently recomputed.

## Real historical outcomes and AI observations

The eight cases are actual Python PEP and Rust RFC governance decisions, publicly authored and ultimately closed. **Five were merged** (Python/peps PRs 4032, 4156, 3990 and 3525; rust-lang/rfcs PR 2972), **three were closed without merge** (Rust PRs 2774, 3223 and 3251). Their factual dispositions were documented directly in the public PR API, including immutable snapshot-file digests in the collected artifact. Source PR metadata may have been edited after closure: this is a retrospective record, **not** a guaranteed point-in-time predecision corpus.

Three distinct OpenRouter AI models were asked to simulate a governance maintainer, temporal-process expert and adversarial methodologist; no role was an actual human. The predeclared strict JSON/quote parser accepted **17/24** votes: **11/17** matched the actual public merge-versus-no-merge disposition; the remaining **6** were explicit `insufficient_evidence` abstentions rather than wrong numeric classes. **Seven invalid votes** remain excluded: five referenced text that was not an exact substring of the model-visible case, and two generated valid-looking fenced JSON with additional prose instead of one permissible JSON envelope. Do not silently repair those texts or count them as evidence meeting the predeclared strict output criterion.

| Case ID | Public real source | Historical GitHub disposition | Strict-valid votes | Votes matching observed outcome | Valid abstentions |
| --- | --- | --- | ---: | ---: | ---: |
| P07C-GOV-001 | [Python PEP 291](https://github.com/python/peps/pull/4032) | merged | 1/3 | 1 | 0 |
| P07C-GOV-002 | [Python PEP 387](https://github.com/python/peps/pull/4156) | merged | 3/3 | 3 | 0 |
| P07C-GOV-003 | [Python PEP 735](https://github.com/python/peps/pull/3990) | merged | 2/3 | 2 | 0 |
| P07C-GOV-004 | [Python PEP 702/387](https://github.com/python/peps/pull/3525) | merged | 1/3 | 1 | 0 |
| P07C-GOV-005 | [Rust constrained naked functions](https://github.com/rust-lang/rfcs/pull/2972) | merged | 2/3 | 2 | 0 |
| P07C-GOV-006 | [Rust RFC 1201 amendments](https://github.com/rust-lang/rfcs/pull/2774) | closed without merge | 3/3 | 0 | 3 |
| P07C-GOV-007 | [Rust RFC 1201 supersession update](https://github.com/rust-lang/rfcs/pull/3223) | closed without merge | 2/3 | 2 | 0 |
| P07C-GOV-008 | [Rust multiple crate versions](https://github.com/rust-lang/rfcs/pull/3251) | closed without merge | 3/3 | 0 | 3 |

Exactly **3/8** cases had three strict-valid unanimous AI votes (one merged prediction and two unanimous abstentions). This is **not** a human inter-rater agreement score. Overall source/review checks passed, but original paid role-panel step failed its full-coverage acceptance gate and must remain classified as partial.

## Scientific relevance and explicit limitations

- **Positive evidence:** real external dated PR dispositions, source documentation, pre-closure dated comments, isolated outcome sidecar, three separately executed model vendor roles and an independently executed source/response audit.
- **Critical limitation 1:** PR `merged` versus `closed_without_merge` is a factual workflow outcome, **not a normative policy-authorisation gold decision** and not evidence that the action was correct. It cannot be substituted into WAMBU's primary unsafe-action reference outcome.
- **Critical limitation 2:** GitHub returns present-day PR title/body, possibly edited post-decision. Only individually timestamped comments were filtered to before closure. A pretrained model might already know these historical PR outcomes.
- **Critical limitation 3:** Models see different information from a realistic long-running memory harness. This experiment studies limited public-governance reading and uncertain-outcome estimation; it does not manipulate memory compaction, authoritative ledgers or Knowledge Triage over equal-information, equal-budget conditions.
- **Critical limitation 4:** There are **zero** actually independent qualified human participants in this panel; all reviewer identities are simulated model roles. No blind real human adjudication or consensus qualification has occurred.
- **Critical limitation 5:** 17 strict-valid role outputs cannot be compared for model superiority; small cases and nonrandom missingness prevent inference. No confirmatory holdout, journal review or paper acceptance.

## Terminal status and next scientifically eligible work

`REAL_HISTORICAL_GOVERNANCE_SOURCE_INTAKE_COMPLETE`, `AI_SPECIALIST_SIMULATION_PARTIAL_17_OF_24`, `DETACHED_EVIDENCE_AUDIT_COMPLETE`, `P07B_NATURALISTIC_AUTHORISED_ACTION_GOLD_NOT_SATISFIED`, `P08_FULL_ORIGINAL_KT_NOT_REPRODUCED`. The next relevant step for the article is a **source-authenticated collection of real operational decisions made under competing authority/timing/scope constraints**, together with an independent, qualified human case writer and blind adjudicator. Another AI-only round can be exploratory but can never be reported as human external validation.
