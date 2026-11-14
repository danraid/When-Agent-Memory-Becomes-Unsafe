"""Conservative, evidence-driven research lifecycle planner."""
from __future__ import annotations
from dataclasses import dataclass

DEPS = {
    'discovery': (),
    'evidence_audit': ('discovery',),
    'hypotheses': ('evidence_audit',),
    'preregistration': ('hypotheses',),
    'pilot': ('preregistration',),
    'independent_validation': ('pilot',),
    'confirmatory': ('independent_validation',),
    'analysis': ('confirmatory',),
    'manuscript': ('analysis',),
    'independent_review': ('manuscript',),
    'submission': ('independent_review',),
}
SUCCESS = {'TECHNICAL_PASS', 'AUTHOR_APPROVED'}
VALID = {'NOT_STARTED', 'IN_PROGRESS', 'BLOCKED'} | SUCCESS

@dataclass(frozen=True)
class Decision:
    stage: str
    status: str
    ready: bool
    reason: str


def validate(state):
    statuses = state.get('stages', {})
    gates = state.get('human_gates', {})
    if not isinstance(statuses, dict) or (set(statuses)-set(DEPS)):
        raise ValueError('Unknown or malformed research stages')
    for key, status in statuses.items():
        if status not in VALID:
            raise ValueError(f'Invalid state: {key}={status}')
    for key in ('preregistration_locked','confirmatory_release_approved','submission_authorized'):
        if type(gates.get(key, False)) is not bool:
            raise ValueError('Human gate must be boolean')
    if statuses.get('confirmatory') in SUCCESS and not (gates.get('preregistration_locked') and gates.get('confirmatory_release_approved')):
        raise ValueError('Invalid confirmatory result without preregistration lock and author approval')
    if statuses.get('submission') in SUCCESS and not gates.get('submission_authorized'):
        raise ValueError('Invalid submission state without author approval')
    for stage, parents in DEPS.items():
        if statuses.get(stage) in SUCCESS and any(statuses.get(p) not in SUCCESS for p in parents):
            raise ValueError(f'Stage {stage} has unqualified dependency')


def plan(state, implemented=None):
    validate(state)
    implemented = set() if implemented is None else set(implemented)
    if implemented-set(DEPS):
        raise ValueError('Unknown implemented stage')
    statuses = state.get('stages', {})
    gates = state.get('human_gates', {})
    result = []
    for stage, parents in DEPS.items():
        status = statuses.get(stage, 'NOT_STARTED')
        if status in SUCCESS:
            reason = 'RECORDED_NOT_INDEPENDENTLY_REVALIDATED'
        elif stage not in implemented:
            reason = 'RUNNER_NOT_IMPLEMENTED'
        elif any(statuses.get(p) not in SUCCESS for p in parents):
            reason = 'DEPENDENCY_NOT_VERIFIED'
        elif stage == 'confirmatory' and not (gates.get('preregistration_locked') and gates.get('confirmatory_release_approved')):
            reason = 'HUMAN_CONFIRMATORY_GATE_CLOSED'
        elif stage == 'submission' and not gates.get('submission_authorized'):
            reason = 'HUMAN_SUBMISSION_GATE_CLOSED'
        else:
            reason = 'ELIGIBLE_TO_ATTEMPT_NOT_COMPLETED'
        result.append(Decision(stage, status, reason == 'ELIGIBLE_TO_ATTEMPT_NOT_COMPLETED', reason))
    return result
