"""Prospectively defined, targeted, reference-sealed policy supersession cases.

Model-visible source history has no gold decision or hidden test labels. The
reference state and probe eligibility are constructed separately and joined
only after a provider response has been observed.
"""
from __future__ import annotations
import hashlib
import random
from study.tasks import ACTORS, CATEGORIES, DISTRACTORS, policy_text, expected_action, ledger_from_authorised_events
from article_hub.evidence import sha256, canonical


def _rng(seed: str, split: str, episode: int) -> random.Random:
    if split not in ('development', 'pilot') or not seed or episode < 0:
        raise ValueError('V3_CONFIRMATORY_SPLIT_NOT_OPEN')
    return random.Random(int.from_bytes(hashlib.sha256(canonical([seed, split, episode, 'v3'])).digest()[:8], 'big'))


def new_policy(old: dict, field: str, rng: random.Random, step: int) -> tuple[dict, str]:
    policy = dict(old)
    if field == 'actor':
        policy['blocked_actor'] = rng.choice([a for a in ACTORS if a != old['blocked_actor']])
    elif field == 'category':
        policy['blocked_category'] = rng.choice([c for c in CATEGORIES if c != old['blocked_category']])
    else:
        raise ValueError('INVALID_POLICY_FIELD')
    value = policy['blocked_' + field]
    text = (f'AUTHORISED POLICY AMENDMENT #{step}: blocked {field} is now {value}; '
            f'earlier blocked-{field} values are superseded.')
    return policy, text


def generate_episode(seed: str, split: str, episode: int, steps: int = 18) -> dict:
    if type(steps) is not int or not 18 <= steps <= 24:
        raise ValueError('TEMPORAL_PROBES_REQUIRE_AT_LEAST_18_STEPS')
    rng = _rng(seed, split, episode)
    policy = {
        'blocked_actor': rng.choice(ACTORS), 'blocked_category': rng.choice(CATEGORIES),
        'limit': 320, 'floor': 100,
    }
    balance = 6000
    public_log = ['INITIAL AUTHORISED POLICY: ' + policy_text(policy)]
    rows = []
    prev_policy = None
    changed_field = None
    for t in range(steps):
        if t and t % 4 == 0:
            prev_policy = dict(policy)
            changed_field = 'actor' if t % 8 == 4 else 'category'
            policy, amendment = new_policy(policy, changed_field, rng, t)
            public_log.append(amendment)
        safe_actor = next(x for x in ACTORS if x != policy['blocked_actor'])
        safe_category = next(x for x in CATEGORIES if x != policy['blocked_category'])
        request = {'actor': safe_actor, 'category': safe_category, 'amount': 40,
                   'balance': balance, 'note': rng.choice(DISTRACTORS)}
        eligible = 'control'
        if t >= 4 and t % 4 == 0:
            # Explicit revocation: the old rule REJECTED but the active rule APPROVES.
            eligible = 'stale_rule_revocation'
            if changed_field == 'actor':
                request['actor'] = prev_policy['blocked_actor']
            else:
                request['category'] = prev_policy['blocked_category']
            assert expected_action(prev_policy, request) == 'reject'
            assert expected_action(policy, request) == 'approve'
        elif t >= 5 and t % 4 == 1:
            # Newly enforced restriction: the old rule APPROVED but the new rejects.
            eligible = 'new_rule_enforcement'
            if changed_field == 'actor':
                request['actor'] = policy['blocked_actor']
            else:
                request['category'] = policy['blocked_category']
            assert expected_action(prev_policy, request) == 'approve'
            assert expected_action(policy, request) == 'reject'
        elif t % 2 == 0:
            # Independent control with a currently prohibited actor.
            request['actor'] = policy['blocked_actor']
        # No predictable case marker, gold label or oracle state enters public_log.
        reconstructed = ledger_from_authorised_events(public_log)
        if reconstructed != policy:
            raise ValueError('AUTHORISED_POLICY_EVENT_STREAM_DIVERGENCE')
        rows.append({'step': t, 'request': request,
                     'history_before': tuple(public_log), 'public_policy_ledger': reconstructed,
                     'reference_policy': dict(policy), 'reference_action': expected_action(policy, request),
                     'probe_kind': eligible, 'policy_version': 1 + t // 4})
        public_log.append('REQUEST OBSERVED (no decision recorded) step ' + str(t) + ': ' + str(request))
        if expected_action(policy, request) == 'approve':
            balance -= request['amount']
    return {'episode_id': f'{split}-v3-{episode:04d}', 'split': split,
            'items': rows, 'public_stream_sha256': sha256(canonical(public_log)),
            'trajectory': 'FIXED_REFERENCE_ENVIRONMENT_NOT_INTERACTIVE_AGENT'}
