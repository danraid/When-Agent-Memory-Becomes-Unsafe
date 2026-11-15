# Fictional policy-update roleplay | development fixtures only

**Eight fictional cases and eight fictional labels. ZERO real human participants, ZERO independent human adjudications.**

These are synthetic examples produced by an AI assistant in one session to test the case intake and temporal-policy task design. The case-writer and adjudicator role identifiers are **fictional labels**, not people. The labels were generated together with the cases and are therefore **not independent scientific ground truth**. The sample URLs under `example.org`, zero SHA-256 placeholders and synthetic licences are intentionally not external provenance.

Files:
- [Model-visible fictional cases](../fixtures/fictional_development_casebook.json) contain no expected action.
- [Separate fictional roleplay labels](../fixtures/fictional_development_roleplay_labels.json) contain generated reference actions and reasons.

Families: valid revocation; future-effective restriction; not-yet-effective restriction; unauthorised override; scope mismatch; revoked delegation; equal-authority conflict requiring abstention; stale quotation.

**Important:** These are demonstrations, not a consistent legally or operationally verified authority model. Some cases (especially delegation and simultaneous equal-rank conflict) require a more explicit rule hierarchy before they can be used as scored benchmarks. Do not treat the simulated labels as adjudicated gold.

Validate structural compatibility in explicitly fictional mode:

```bash
python scripts/validate_independent_case_intake.py \
  --cases fixtures/fictional_development_casebook.json \
  --reviews fixtures/fictional_development_roleplay_labels.json \
  --allow-simulation
```

Running the same command **without** `--allow-simulation` must reject fictional data for genuine independent-human intake.

This work does not satisfy P07b's independent human-review gate, does not provide a naturalistic test set, does not establish novelty, and cannot be used as confirmatory or journal-validating evidence. Private holdout remains untouched. No paid GPT calls were made.
