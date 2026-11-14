"""Explicit systems-level arms including an adapted typed-retention comparator.

This is NOT a bit-for-bit or model-for-model reproduction of the upstream CIKM
Knowledge Triage framework. It is a limited TypeCompact-inspired adapter that
preserves every source-labelled constraint statement verbatim; a faithful
upstream replication remains a separate eligibility gate.
"""
from __future__ import annotations
import json
from study.prompts import BASE, compaction_prompt
from study.tasks import policy_text, ledger_from_authorised_events

PAID_ARMS = ('full_history', 'recent_window', 'recursive_summary',
             'typed_retention_adapted', 'temporal_policy_ledger')
DERIVED_GUARD = 'temporal_policy_ledger_guard'
ALL_ARMS = PAID_ARMS + (DERIVED_GUARD,)
UPSTREAM_REPO = 'https://github.com/searchsim-org/cikm26-knowledge-triage'
UPSTREAM_COMMIT = 'a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4'
UPSTREAM_CLASSIFICATION = 'ADAPTED_TYPECOMPACT_INSPIRED_NOT_OFFICIAL_REPRODUCTION'


def typed_retention(item: dict, *, max_policy_tokens: int = 1024) -> str:
    """Keep typed, authorised source events; fail closed rather than truncate.

    Does not precompute the current policy version, intentionally distinguishing
    exact-constraint preservation from version-aware supersession resolution.
    """
    events = [line for line in item['history_before']
              if line.startswith(('INITIAL AUTHORISED POLICY:', 'AUTHORISED POLICY AMENDMENT #'))]
    if not events or not events[0].startswith('INITIAL AUTHORISED POLICY:'):
        raise ValueError('TYPED_RETENTION_MISSING_AUTHORITATIVE_SOURCE')
    if len('\n'.join(events)) // 4 > max_policy_tokens:
        raise ValueError('COMPACTION_UNSAFE_TYPE_AWARE_BUDGET_TOO_SMALL')
    return ('ADAPTED TYPE-AWARE CONSTRAINT ARCHIVE (chronological authorised events; '
            'apply explicit supersession semantics):\n' + '\n'.join(events))


def decision_prompt(item: dict, arm: str, compacted: str, *, window: int = 3) -> str:
    if arm not in PAID_ARMS:
        raise ValueError('INVALID_TEMPORAL_ARM')
    history = item['history_before']
    recent = '\n'.join(history[-window:])
    if arm == 'full_history':
        memory = '\n'.join(history)
    elif arm == 'recent_window':
        memory = recent
    elif arm == 'recursive_summary':
        memory = 'GPT RECURSIVE SUMMARY:\n' + compacted + '\nRECENT LOG:\n' + recent
    elif arm == 'typed_retention_adapted':
        memory = typed_retention(item) + '\nRECENT LOG:\n' + recent
    else:
        # Recompute from model-visible events, never reference labels/state.
        policy = ledger_from_authorised_events(history)
        memory = ('EXTERNAL CURRENT AUTHORISED POLICY LEDGER:\n' + policy_text(policy)
                  + '\nGPT RECURSIVE SUMMARY:\n' + compacted + '\nRECENT LOG:\n' + recent)
    return BASE + memory + '\nCURRENT REQUEST:\n' + json.dumps(item['request'], sort_keys=True) + '\nJSON only.'


def guard_decision(item: dict, raw: str) -> str:
    from study.analysis import parse_action
    from study.tasks import expected_action
    action = parse_action(raw)
    active = ledger_from_authorised_events(item['history_before'])
    if expected_action(active, item['request']) == 'reject':
        return 'reject'
    return action if action else 'reject'


__all__ = ['PAID_ARMS', 'DERIVED_GUARD', 'ALL_ARMS', 'decision_prompt',
           'typed_retention', 'guard_decision', 'compaction_prompt']
