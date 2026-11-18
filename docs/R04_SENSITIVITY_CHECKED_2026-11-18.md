# R04 | Prospective episode-level sensitivity verification (development only)

**Date:** 2026-11-18. **Source assumptions:** [SAMPLE_SIZE_JUSTIFICATION.md](../protocol/SAMPLE_SIZE_JUSTIFICATION.md). **Execution:** [GitHub Actions #44396641396](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396641396), [artifact #14469961799](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396641396/artifacts/14469961799), SHA-256 `a289416907e35bc02c9c22b9c0e50ff372dec59d586056d1bf1d277f0fe84c8c`.

## Verified mathematics, not an empirical power study

The independent experimental unit must be a paired, independently seeded 18-step episode. **Do not treat per-turn outcomes as independent**. The existing dev pilots include only eight and four episodes and have saturated all explicit temporal-policy probes; no measured episode-level variance supporting an effect was established.

Normal-approximation exploratory sensitivity, for hypothesised effect `delta=0.10`, two-sided alpha 0.05, nominal power 0.80:

| Assumed paired episode-level SD | Approximate independent episodes | Estimated calls at 77 per episode | Fits current 2,500-call limit? |
|---|---:|---:|---|
| 0.15 | 18 | 1,386 | Yes |
| 0.20 | 32 | 2,464 | Yes |
| 0.25 | 50 | 3,850 | No |

The 2,464 calls at 32 episodes leave 36 calls before the operational cap, which may be insufficient for external diagnostics. These counts are **scenario sensitivity assumptions**, not a freezeable sample-size justification without independent evidence of the true effect/variance and discriminative probes. There is no guarantee of 80% actual power or validity of a sign-flip test from this normal approximation.

## Audited implementation and next scientific requirement

[`scripts/r04_episode_sensitivity.py`](../scripts/r04_episode_sensitivity.py) preserves the assumed-vs-observed distinction and emits a structured no-call report. The verified [CI](../.github/workflows/r04-episode-sensitivity.yml) rejects calculations that pretend the hypothetical sample is already approved or uses the protected sample.

**R04 remains PARTIAL**: sample-size mathematics is checked, but non-ceiling independently sourced development episodes and an author-frozen estimand, missingness rules, multiplicity, validated variance and episode-level sensitivity are still required before any confirmatory stage.

**No paid provider requests, confirmatory access, author protocol approval or external journal submission were performed.**
