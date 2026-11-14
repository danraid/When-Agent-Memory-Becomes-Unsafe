"""Explicitly fictional test experiment for proving the research pipeline can execute."""
from __future__ import annotations
import random
from .evidence import canonical, sha256
from .statistics import paired_difference


def synthetic_paired_demo(*, seed=2026, n=400, control_rate=0.20, intervention_rate=0.12):
    if type(seed) is not int or type(n) is not int or not 20 <= n <= 100000:
        raise ValueError('Invalid seed or sample size')
    if not (0 <= intervention_rate <= 1 and 0 <= control_rate <= 1):
        raise ValueError('Rates must be probabilities')
    rng = random.Random(seed)
    draws = [rng.random() for _ in range(n)]
    control = [v < control_rate for v in draws]
    intervention = [v < intervention_rate for v in draws]
    stats = paired_difference(control, intervention)
    return {
        'classification': 'SYNTHETIC_METHODS_DEMONSTRATION',
        'scientific_evidence': False,
        'claim_about_real_agents': False,
        'seed': seed,
        'n': n,
        'assumed_parameters': {'control_rate': control_rate, 'intervention_rate': intervention_rate},
        'design': 'paired_common_random_numbers_toy_model',
        'outcomes_sha256': sha256(canonical({'control': control, 'intervention': intervention})),
        'analysis': stats,
        'limitations': 'Fictional Bernoulli assumptions; no real-agent measurements, causal evidence or article result.',
    }
