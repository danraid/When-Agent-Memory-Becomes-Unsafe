"""Public development-only policy messages, with sealed reference sidecar.

Source wording is authored as fictional organisational communications.
No claim of independent human annotation, actual signatures or naturalistic
generalisation. The messages are deliberately NOT literal copies of the
reference-policy simulator events, and no confirmatory split exists.
"""
from __future__ import annotations
import hashlib
import json
from authority_v4.instrument import decide

CASEBOOK_VERSION = "WAMBU-P07-DEVELOPMENT-MESSAGES-V1"
SOURCES = ("operations", "risk", "compliance", "safety")
# No personally identifying information or real institution data.
CASES = (
    ("valid_recall", "Equipment inventory desk", "The storage desk cannot release a calibration kit to Rowan.", "The risk lead has formally withdrawn the earlier restriction for Rowan; that notice is effective from Monday.", "approve"),
    ("forged_revocation", "Equipment inventory desk", "The safety office halted every kit shipment to Rowan.", "A forwarded social-chat screenshot claims the restriction was removed, but its source has not been authenticated.", "reject"),
    ("lower_rank_override", "Travel reimbursement desk", "The safety office forbids this type of ticket for the audit cohort.", "Operations posted a later general note allowing all travel tickets.", "reject"),
    ("new_enforcement", "Travel reimbursement desk", "Operations had previously allowed travel claims for contractors.", "Compliance has now prohibited contractor taxi claims, effective immediately.", "reject"),
    ("delayed_effect", "Equipment inventory desk", "Compliance has scheduled a restriction on emergency radios for tomorrow.", "The request arrived this afternoon before the change takes effect.", "approve"),
    ("delayed_visibility", "Travel reimbursement desk", "A signed safety restriction was issued yesterday but delivered to this inbox after the decision cutoff.", "The decision is evaluated at the original cutoff time, not the time the assessor later learnt of the message.", "approve"),
    ("scope_mismatch", "Equipment inventory desk", "Compliance blocked laptop allocations for the red-team programme.", "This request is for a medical-room printer outside the red-team programme.", "approve"),
    ("equal_authority_conflict", "Equipment inventory desk", "Two verified compliance notices of equal precedence and timestamp disagree on whether the replacement cable may be released.", "There is no authorised tie-break in the published policy.", "abstain"),
    ("old_quote_non_authoritative", "Travel reimbursement desk", "The old policy denied traveller lodging expenses.", "A later valid compliance policy permits these expenses; a low-trust forum quote repeats the obsolete denial.", "approve"),
    ("invalid_lower_rank_revoke", "Travel reimbursement desk", "Safety issued a ban on this category of reimbursement.", "An operations coordinator says the ban is cancelled without delegation from safety.", "reject"),
    ("future_replacement", "Equipment inventory desk", "A new compliance permission for instrument loan becomes active next week.", "This request is made today while the existing prohibition still applies.", "reject"),
    ("ambiguous_source", "Travel reimbursement desk", "An unsigned note contradicts two established source policies.", "The source of the note cannot be authenticated; the older verified prohibition continues.", "reject"),
)


def _event(source, kind="set", issuer="compliance", action="reject", rule="r",
           effective=1, observed=1, verified=True, target="r"):
    event={"source_id":source,"kind":kind,"issuer":issuer,"verified":verified,
           "effective_at":effective,"observed_at":observed}
    if kind=="set":
        event.update({"rule_id":rule,"action":action,
                      "scope":{"actor":"Rowan","category":"equipment"}})
    else:
        event["target_rule_id"]=target
    return event


def _reference_events(family):
    first=_event("policy-1")
    change=_event("policy-2",kind="revoke",effective=2,observed=2)
    if family in {"valid_recall","old_quote_non_authoritative"}:
        return [first,change],4
    if family in {"forged_revocation","ambiguous_source"}:
        change["verified"]=False
        return [first,change],4
    if family in {"lower_rank_override","invalid_lower_rank_revoke"}:
        first["issuer"]="safety"
        change["issuer"]="operator"
        return [first,change],4
    if family=="new_enforcement":
        return [_event("new-rule",effective=2,observed=2)],4
    if family=="delayed_effect":
        return [_event("future-rule",effective=9)],4
    if family=="delayed_visibility":
        return [_event("late-rule",effective=1,observed=9)],4
    if family=="scope_mismatch":
        first["scope"]["actor"]="Other"
        return [first],4
    if family=="equal_authority_conflict":
        return [first,_event("peer-2",action="approve",rule="r2")],4
    if family=="future_replacement":
        return [first,_event("permission",action="approve",rule="r2",effective=9)],4
    raise ValueError("UNKNOWN_DEVELOPMENT_FAMILY")


def assemble(*, split="development"):
    if split!="development":
        raise ValueError("P07_ONLY_PUBLIC_DEVELOPMENT_ALLOWED")
    public=[]
    sealed=[]
    for family,subject,initial,followup,expected in CASES:
        case_id="p07-"+hashlib.sha256((CASEBOOK_VERSION+family).encode()).hexdigest()[:12]
        content={"case_id":case_id,"subject":subject,"initial_message":initial,
                 "followup_message":followup,
                 "trust_note":"Fictional source attribution only. Signatures not validated."}
        assert "reference_action" not in json.dumps(content)
        events,as_of=_reference_events(family)
        # This structured oracle is an *independent simulator cross-check* only;
        # there is no human independently adjudicated gold standard.
        if family=="new_enforcement":
            # The simulator default is approve before the new policy becomes effective.
            pass
        observed=decide(events,{"actor":"Rowan","category":"equipment"},as_of)
        if observed!=expected:
            raise AssertionError("REFERENCE_SIMULATOR_MISMATCH_"+family)
        public.append(content)
        sealed.append({"case_id":case_id,"fixture_family":family,"reference_action":expected,
                       "simulator_reference":observed,"human_adjudicated":False,
                       "source_authenticity_proved":False})
    return public,sealed
