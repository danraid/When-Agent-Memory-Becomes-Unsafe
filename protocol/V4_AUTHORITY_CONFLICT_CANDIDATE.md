# WAMBU-001 | v4 authority-conflict development instrument

**Status: IMPLEMENTATION CANDIDATE, NOT FROZEN SCIENCE, NOT CONFIRMATORY.** This document introduces ordinary engineering fixtures and does not amend a scientific preregistration or author lock.

## Motivation and evidence

The [v2 pilot audit](../docs/PILOT_V2_AUDIT_2026-11-14.md) and [recovered v3 real-pilot evidence](../docs/V3_ORIGINAL_ARTIFACT_RECOVERY_2026-11-14.md) show a zero observed contrast in the proposed primary endpoint, including saturated revocation and new-rule probes under v3. This is a negative feasibility finding, not statistical equivalence. [CIKM 2026 Knowledge Triage](../literature/HIGH_OVERLAP_PRIOR_ART_2026-11-14.md) already covers broad safety-rule preservation; [Supersede](https://arxiv.org/abs/2606.27472) addresses temporal memory updates. A mere "safety retention" or "policy revision" novelty claim is unsupported.

## Bounded terminal state

An **offline** family of independently public-seeded simulator cases exists with formal source precedence, valid/invalid revocation, effective-time gating, late-arriving events, actor/category scope, tied-authority conflict, and explicit abstention. Public model inputs contain source events and requests only, not gold action/fixture name. Unit tests verify expected references and split isolation. No GPT calls, human signatures, private seeds or confirmatory datasets are involved.

## Authority semantics (candidate only)

- Three simulator-trusted authorities: `operator < compliance < safety`. Actual organisational authority and cryptographic verification are **not** inferred. The `verified` flag is input metadata for an offline simulator, **not proof of signature verification**.
- An event is applicable only if it has been *observed* and has become effective by the queried decision time. Future or unverified events cannot change the current decision.
- Set events modify a named rule when issued by a source with sufficient authority. Revoke events remove a named rule only if the issuer has at least its active source's rank.
- At evaluation, matching rules are ordered by authority rank and effective time. Equal-rank, equal-time incompatible actions yield `abstain`, rather than arbitrary list-order resolution. If no rule applies, the candidate default is `approve`.
- Scope matching is exact on actor and category, with wildcard `*`. No inferred semantics for natural-language claims. The code has no network, API adaptor, private seed, or confirmatory route.

These semantics are intentionally **not scientific ground truth** beyond the declared simulator. They require human domain/validity review, treatment of real-world source authenticity, and an independently documented annotation protocol before use in a publishable benchmark.

## Fourteen fixture families

Higher-authority allow; blocked lower-authority override; valid revocation; unauthorised revocation; unverified revocation; future restriction not yet effective; future restriction now effective; wrong actor; wrong category; same-rank/same-time conflicting active rules (abstain); valid same-ID replacement; unverified higher-authority allow; late update before arrival; late update after arrival.

A public deterministic seed randomises episode entities and the order of the fourteen cases. Cases remain **templated synthetic development fixtures**; their use cannot establish realistic robustness or eliminate generator artefacts.

## Engineering and scientific exit gates

1. `python -m unittest discover -s tests -v` passes the new `tests/test_authority_v4.py` alongside the existing suite; no provider calls or holdout access.
2. Separate a no-network offline test of reproducibility, public model-input leakage, valid and invalid authority transitions, conflicting-tie abstention, and development/pilot split rejection of `confirmatory`.
3. Broaden cases prospectively with independently authored, naturalistic multi-actor policy messages, varied chronology, equal-information comparator runs and source authenticity metadata. Avoid using deterministic fixture performance as scientific effect-size evidence.
4. **Do not** adapt the v3 confirmatory proposal from these results without prospective scientific-method review. No hypothesis, sample size, multiplicity plan, final journal, or confirmation is frozen by this file.

## Known methodological caveats

Order of events is by observation, while rule selection orders active matching rules by source rank and effective timestamp. This defines one explicit operational semantics but not every possible legal/policy precedence system. Existing rules are stored by rule ID; same-ID lower-rank changes are suppressed. No authenticity cryptography or contested delegation is implemented. Fixture outcomes can be inspected by maintainers, so these are public development cases, not an independent test set.

**Next eligible phase:** verify the offline instrument on CI, separately implement and audit a faithful comparator with identifiable release/license/model/budget settings, then design *new* naturalistic human-reviewed cases. Neither v4 nor adapted v3 should be promoted to a CIKM replication.
