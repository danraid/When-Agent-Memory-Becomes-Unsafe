# R04 | Development instrument design: historical authority, scoped exceptions and revocation

**Bounded terminal state:** A fixed 36-item, two-episode development-only instrument exists, its oracle and prompt partition survive adversarial tests, all three arms receive exactly the same public event source and request, and an independent no-inference audit reproduces whatever real results are observed without case selection.

## Design chosen after repository inspection

The R03 two-episode, same-source pilot returned 36/36 correct in both arms. A larger sample of the same easy items would repeat an instrument with no discrimination. A comparison that deliberately hides essential evidence from one arm would instead invalidate source parity. Therefore this instrument adds **genuine temporal-authority complexity** rather than assigning an expected loser.

Each episode comprises an initial signed authority, role and region amendments effective at different ticks, two tightly scoped signed exceptions with validity intervals, an explicit revocation, a hard critical-risk rule that no exception overrides, and a non-authoritative conflicting team note. Queries request decisions at independently sampled past or present effective times, including dates before and after amendments and exception expiration. Case order is independently shuffled to remove the old step-to-answer correlation. All three arms get the identical signed source record and query: raw source alone, source plus recursive summary, or source plus a deterministic time-aware ledger derived only from the same record. All source timestamps and exception semantics are model-visible; no reference answer or item category is in the prompt.

The deterministic synthetic oracle evaluates the structured original authority events (not model replies). Unit tests separately assert a manually specified expected outcome for each archetype, build-prompt invariance to corrupted oracle fields, source hashes, date validity, balanced source-designed outcomes, and rejection of missing/forged authority. Synthetic oracle labels are **not human or independent field-action gold**.

## Precommitted outcome policy

No method is required to fail and no tasks are excluded after observing model outputs. Report raw decision distribution, invalid replies, paired disagreements, errors by archetype, episodes as the only potentially independent clusters, and input-token differences. **No p-value, causal effect, superiority or equivalence claim** is allowed. If all arms again saturate, the outcome is a valuable negative qualification and the instrument remains scientifically nondiscriminative.

## Execution and boundaries

Protocol: [R04_TEMPORAL_AUTHORITY_STRESS_DEV_V1.json](../protocol/R04_TEMPORAL_AUTHORITY_STRESS_DEV_V1.json). This instrument does not rewrite R03 observations or open confirmation. Original real-world R01 policy action labels remain missing. Do not merge the development results with the protected sample, infer statistical power from two episodes or submit to a journal.

R04 may be marked technically qualified only if **all 108 model decisions, eight compactions, 116 distinct provider IDs**, a full held-out-zero report and independent offline audit exist. Empirical discriminative validity remains a separate verdict.
