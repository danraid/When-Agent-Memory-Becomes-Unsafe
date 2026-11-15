# P07b independent case intake | development-only

**Status: validator implemented; zero authentic human case adjudications recorded.**

This tool validates the structure of separately authored development cases and their independent adjudications. It does not authenticate real identities, verify source licences, assess correctness of policy interpretations or certify peer review.

## Two-file intake contract

The casebook contains a `cases` array. Each case needs a stable ID, `split: development`, author ID and independence declaration, at least one source with URL/revision/SHA-256/licence, policy events with issuer/issue time/effective time/scope/rule/supersedes, decision time and a request. **Never place `gold_action`, `expected_action` or `adjudicated_action` in the model-visible casebook.**

A separate review document contains an `adjudications` array. Each review needs matching case ID, an adjudicator ID distinct from the case writer, independence declarations, approve/reject/abstain, reason, source event citations and review time. Abstentions require a concrete ambiguity basis.

Run:

```bash
python scripts/validate_independent_case_intake.py --cases /path/to/development_cases.json --reviews /path/to/independent_adjudications.json
python -m unittest tests.test_independent_case_intake -v
```

**A structural PASS is not an authenticity PASS.** Qualified humans must independently author, adjudicate and review the real source-policy semantics; their provenance and conflicts must be checked outside this schema. No sample identity, adjudication count or acceptance status may be invented.

The tool rejects non-development split cases and any casebook containing embedded reference actions. The private confirmatory split must remain uncreated/unopened by this workflow. No paid GPT calls occur.

**Next gate:** obtain authentic independently authored and adjudicated development cases, verify source rights and semantic validity, then assess whether the resulting instrument discriminates without tuning on the confirmatory holdout.
