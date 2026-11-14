# Prospective sensitivity, not retrospective pilot power

Primary unit: one independently seeded 18-step episode. Paired episode risk differences are the observations in the primary test, **not** per-turn outputs. Zero positive effects in a two-episode development sample do not imply an effect SD of zero or that any null has been established.

The normal approximation for a two-sided paired mean uses n approximately ((z_0.975+z_0.80)*sigma/delta)^2. If the target detectable absolute difference is delta=0.10, the assumed episode-level SD is sigma=0.20 and alpha=0.05, n is about 31.4; propose **32 episodes** (80% approximate power). No empirical guarantee or exact power for the nonparametric sign-flip test is claimed.

| Assumed paired SD | Approximate n at 80% nominal power | At n=32 |
|---|---:|---|
| 0.15 | 18 | More than 80% nominal power |
| 0.20 | 32 | About 80% nominal power |
| 0.25 | 50 | Underpowered at n=32 |

The estimated 32*(4*18+5)=2,464 paid decision/compaction calls plus two advisory reviews is below the finite 2,500-call cap. There is **no USD cap**; the call cap is an operational safeguard and must not be modified in response to an observed finding. N=32 is a proposed feasible sample. If independent pilot analysis or reviewer diagnosis invalidates the effect-size/variance or design assumptions, a new prospective protocol revision is required before author freeze, not an after-the-fact test change.
