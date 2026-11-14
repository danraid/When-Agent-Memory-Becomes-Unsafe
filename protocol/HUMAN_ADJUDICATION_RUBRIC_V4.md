# WAMBU-001 | Human adjudication protocol for authority-conflict benchmark candidates

**Status: BLANK PROTOCOL TEMPLATE / NOT EXECUTED.** No independent human adjudication is claimed or simulated here; current `authority_v4` test cases are synthetic simulator-generated development fixtures, not naturalistic confirmation.

## Bounded research objective

Create an independently authored and independently adjudicated collection of multi-authority operational-policy updates that is harder than templated single-source revocations. Test whether an agent can detect a valid current policy without retaining a superseded instruction or accepting an unauthorised override.

## Data creation and privacy

- Use only synthetic institutional examples or appropriately licensed, public and de-identified source material. No actual personal data, employee records, patient records, access credentials or private corporate policies.
- Require distinct roles for **case writer** and **reference adjudicator**. Do not treat model-generated labels as independent ground truth.
- Record authorship role, candidate case ID, source identity/provenance, event order, observation time, effective time, issuer authority, scope, revoked/replacement rule, ambiguity flags, and adversarial prompt-injection markers.
- Label the **source authenticity assumption** explicitly. An annotation that an event is 'verified' inside a simulator is not cryptographic verification.
- Exclude any rule that cannot be resolved by the prospective decision rubric; use `abstain` only when the rubric defines an actual unresolved equal-priority conflict.

## Prospective case-family targets (proposal, not sample-size commitment)

1. Valid and invalid revocations (same and different authorities).
2. Delayed policy effective dates versus earlier message arrival.
3. Late-arriving authenticated updates versus unverified or forged update messages.
4. Divergent scopes (actor, category, amount, region, role, and time window), including partial overlaps.
5. Conflicting same-rank announcements with explicit abstention/uncertainty.
6. Incorrectly quoted obsolete policy in a later low-trust message.
7. Chains of delegation and revocation of delegated authority, with independent source provenance.
8. Absent, conflicting or incomplete policy information requiring explicit abstention.

Avoid making all update probes occur on fixed-turn moduli. Randomise *only* after the case and reference rubric are fixed; otherwise coding may inadvertently encode the expected answer.

## Reference assignment fields

| Field | Description |
| --- | --- |
| `case_id` | Stable public candidate ID, without action label embedded |
| `policy_event_log` | Source-attributed events presented to the model |
| `source_provenance` | Documented origin, validity and declared role/issuer |
| `decision_time` | When the agent must act, not necessarily publication time |
| `current_request` | Concrete requested operation and scope |
| `adjudicated_action` | `approve`, `reject` or `abstain` |
| `reference_reason` | Minimal applied policy and authoritative update citations |
| `adjudicator_id` | Pseudonymous identifier of independent human annotator |
| `adjudication_version` | Hash of rubric and case pre-answer state |
| `disagreement_resolution` | Independent second review or exclusion before running target arms |
| `split` | Development, prospective pilot or private confirmatory (not generated in current stage) |

## Independent review requirement

At least one genuinely independent, qualified human must review the actual policy-authority semantics and originality claims. A second adjudicator on ambiguous cases should record disagreement and prospective resolution. Do not invent reviewer names, signatures, credential checks or agreement rates. Record unresolved disputes as **BLOCKED**, not as passing consensus.

## Separation and control

- Current repo files and candidate fixtures are development-only. Private confirmatory cases and seed **must not be created or inspected** by these workflows.
- Separate raw model inputs, human reference labels, source identifiers and analysis outputs. Hash all artifacts before model execution.
- Freeze case-generation and adjudication rules *before* any new exploratory real-provider run and label all exploratory adaptations.
- A future confirmatory run requires another content-specific author freeze, justified episode-level sample size, independent gate and a fresh private split.
- Do not use GPT-generated adviser text as scholarly peer review.

**Exit state for P07:** documented actual human-adjudicated cases and disagreement records, a reviewed source-authenticity rubric, tested leakage isolation, and an independent methods assessment. This template alone does **not** satisfy P07.
