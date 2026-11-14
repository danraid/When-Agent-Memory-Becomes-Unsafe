# When Agent Memory Becomes Unsafe

**Constraint Preservation under Repeated Context Compaction**

An independent research repository derived from Agentic Research Hub v0.5.0. It investigates evolving authorised constraints, real GPT recursive summarisation and subsequent synthetic workflow decisions. The article's scientific status is **PROTOCOL DRAFT / INSTRUMENT VALIDATION**, not a confirmed scientific finding or accepted publication.

## Study comparison

| Condition | Context available to the decision agent | Paid model decision |
|---|---|---|
| `full_history` | Full public log of authorised constraints, updates and requests | Yes |
| `recent_window` | Three latest public log entries | Yes |
| `recursive_summary` | Recursive GPT-generated compacted memory plus recent log | Yes |
| `pinned_ledger` | Identical compacted memory plus the current authoritative constraint ledger | Yes |
| `pinned_ledger_guard` | *Same raw model answer as* `pinned_ledger`, then deterministic policy guard | No extra model decision |

Every condition receives identical synthetic requests on an oracle-controlled trajectory. The environment changes a blocked actor/category periodically, and earlier rules are superseded. The fixed trajectory prevents feedback-induced case mismatches but limits external validity. The privileged ledger and guard are systems interventions, not demonstrations of improved model intelligence.

## Replicate the offline checks

```sh
python -m unittest discover -s tests -v
python scripts/run_study.py run --mode mock --split development --episodes 2 --steps 12 --out runs/study-smoke
python scripts/run_study.py verify --directory runs/study-smoke
python scripts/run_study.py freeze-proposal
```

The offline fixture does not call GPT or constitute empirical evidence.

## Real development pilot

Set `OPENAI_API_KEY` in **this repository's** GitHub Actions secrets; the source hub's secret is not shared. Run **Actions > Article 1 | real recursive compaction pilot > Run workflow**. The bounded default is four episodes of twelve steps, four real decision calls at each step, and three genuine GPT summary calls per episode. There is no USD ceiling; model calls, timeout and data volume remain finite. The model defaults to `gpt-6.1-terra`, with an advisory reviewer using `gpt-6-luna`. No secret or provider key is committed.

## Scientific authority

`protocol/STUDY_PLAN.json` and `protocol/PREREGISTRATION.md` are provisional, not frozen. Development and pilot seeds are separate from the private confirmatory seed. A confirmation requires source hashes, exact protocol, model config, privately held seed and separately recorded human author approval. A green CI run alone never promotes a scientific stage.

See `docs/SCIENTIFIC_DESIGN.md`, `docs/IMPLEMENTATION_PLAN.json`, `docs/STATUS.md` and `literature/SCREENING_CANDIDATES.md`. Source discovery is not the same as verified full text. The original hub's technical homologation results do not count as this article's observations.

**Author:** Daniel Raaid. Institutional affiliation, corresponding address, ORCID and target journal remain unset, not invented.
