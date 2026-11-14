"""Small deterministic statistical helpers for pipeline verification, not inference advice."""
from __future__ import annotations
import math


def paired_difference(control, treatment):
    if len(control) != len(treatment) or len(control) < 2:
        raise ValueError('Two equal nonempty paired groups of at least 2 required')
    if any(type(v) is not bool for v in [*control, *treatment]):
        raise ValueError('Paired outcomes must be booleans')
    n = len(control)
    diffs = [int(a) - int(b) for a, b in zip(control, treatment)]
    effect = sum(diffs) / n
    variance = sum((d - effect) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(variance / n)
    return {
        'pairs': n,
        'risk_control': sum(control) / n,
        'risk_treatment': sum(treatment) / n,
        'risk_difference': effect,
        'standard_error': se,
        'ci_95_normal_approx': [max(-1.0, effect - 1.96 * se), min(1.0, effect + 1.96 * se)],
        'ci_method': 'normal_approximation_for_paired_risk_difference',
    }


def cluster_bootstrap_difference(paired_units, *, draws=2000, seed=2026):
    """Paired episode-level bootstrap of *treatment minus control* means.

    Input is (control_episode_mean, intervention_episode_mean) per episode.
    The CI is a predeclared descriptive percentile interval and cannot replace
    prospective sample-size justification or external validity checks.
    """
    import random
    if not 2 <= len(paired_units) <= 100000 or type(draws) is not int or not 100 <= draws <= 10000:
        raise ValueError('Insufficient independent episodes or invalid draws')
    if any(len(p) != 2 or not all(0 <= v <= 1 for v in p) for p in paired_units):
        raise ValueError('Rates must be valid paired episode means')
    diffs = [b-a for a,b in paired_units]
    observed = sum(diffs)/len(diffs)
    random_gen = random.Random(seed)
    samples = []
    n=len(diffs)
    for _ in range(draws):
        samples.append(sum(diffs[random_gen.randrange(n)] for __ in range(n))/n)
    samples.sort()
    return {
        'independent_episodes': n, 'observed_treatment_minus_control': observed,
        'ci_95_percentile_cluster_bootstrap': [samples[int(.025*(draws-1))], samples[int(.975*(draws-1))]],
        'bootstrap_draws': draws, 'bootstrap_seed': seed,
        'method': 'paired_episode_cluster_bootstrap_percentile_descriptive',
    }
