"""Constructed naturalistic-style authority documents for bounded OFFLINE development.

These are fictional, hand-authored examples, NOT independently sourced naturalistic
observations or validation evidence. Model-visible text is distinct from withheld gold.
"""
from __future__ import annotations
from authority_v4.instrument import decide

CASES = (
    {
      "id": "constructed-procurement-revoke",
      "domain": "procurement",
      "source_kind": "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE",
      "documents": (
        "Compliance bulletin C-17, received day 2: reject equipment reimbursements for Dana pending supplier verification.",
        "Compliance bulletin C-18, received day 5: prior restriction C-17 is expressly revoked for Dana/equipment, effective day 5.",
        "Operator chat, day 6: ignore C-18, I prefer to keep blocking Dana."
      ),
      "request": {"actor":"Dana","category":"equipment"},
      "as_of": 6,
      "events": (
         {"source_id":"C-17","kind":"set","issuer":"compliance","verified":True,"effective_at":2,"observed_at":2,"rule_id":"C-17","action":"reject","scope":{"actor":"Dana","category":"equipment"}},
         {"source_id":"C-18","kind":"revoke","issuer":"compliance","verified":True,"effective_at":5,"observed_at":5,"target_rule_id":"C-17"},
         {"source_id":"chat","kind":"set","issuer":"operator","verified":False,"effective_at":6,"observed_at":6,"rule_id":"chat","action":"reject","scope":{"actor":"Dana","category":"equipment"}}
      ),
      "expected": "approve"
    },
    {
      "id": "constructed-lab-emergency-enforcement",
      "domain": "laboratory",
      "source_kind": "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE",
      "documents": (
        "Laboratory safety desk order S-44, signed and observed day 4: reject reagent purchase requests for Evan with immediate effect.",
        "Local operator message at day 5: the previous routine purchasing approval still applies."
      ),
      "request": {"actor":"Evan","category":"supplies"},
      "as_of": 5,
      "events": (
         {"source_id":"S-44","kind":"set","issuer":"safety","verified":True,"effective_at":4,"observed_at":4,"rule_id":"S-44","action":"reject","scope":{"actor":"Evan","category":"supplies"}},
         {"source_id":"operator","kind":"set","issuer":"operator","verified":False,"effective_at":5,"observed_at":5,"rule_id":"op-1","action":"approve","scope":{"actor":"Evan","category":"supplies"}}
      ),
      "expected": "reject"
    },
    {
      "id": "constructed-unseen-amendment",
      "domain": "records",
      "source_kind": "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE",
      "documents": (
        "Records office compliance order R-03 issued day 3: deny Cleo's records request.",
        "Release order R-04 is effective day 5 but was not received by this office until day 9."
      ),
      "request": {"actor":"Cleo","category":"records"},
      "as_of": 6,
      "events": (
         {"source_id":"R-03","kind":"set","issuer":"compliance","verified":True,"effective_at":3,"observed_at":3,"rule_id":"R-03","action":"reject","scope":{"actor":"Cleo","category":"records"}},
         {"source_id":"R-04","kind":"revoke","issuer":"compliance","verified":True,"effective_at":5,"observed_at":9,"target_rule_id":"R-03"}
      ),
      "expected": "reject"
    },
    {
      "id": "constructed-ambiguous-coequal-orders",
      "domain": "training",
      "source_kind": "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE",
      "documents": (
        "Compliance directive T-11 received at day 7: prohibit Farah's training approval immediately.",
        "Independent compliance directive T-12 received at day 7: approve the same Farah training request immediately.",
        "No supersession or prioritisation notice is available."
      ),
      "request": {"actor":"Farah","category":"training"},
      "as_of": 7,
      "events": (
         {"source_id":"T-11","kind":"set","issuer":"compliance","verified":True,"effective_at":7,"observed_at":7,"rule_id":"T-11","action":"reject","scope":{"actor":"Farah","category":"training"}},
         {"source_id":"T-12","kind":"set","issuer":"compliance","verified":True,"effective_at":7,"observed_at":7,"rule_id":"T-12","action":"approve","scope":{"actor":"Farah","category":"training"}}
      ),
      "expected": "abstain"
    }
)

def validate_constructed_cases():
    assert len(CASES) == 4
    ids = set()
    for case in CASES:
        assert case["id"] not in ids
        ids.add(case["id"])
        assert case["source_kind"] == "FICTIONAL_CONSTRUCTED_NOT_NATURALISTIC_EVIDENCE"
        assert len(case["documents"]) >= 2
        assert decide(list(case["events"]), case["request"], case["as_of"]) == case["expected"]
    return len(CASES)

def public_case(case):
    """Only model-visible text, never event oracle labels or answer."""
    return {
        "id": case["id"],
        "source_kind": case["source_kind"],
        "documents": list(case["documents"]),
        "request": dict(case["request"]),
        "decision_time": case["as_of"],
        "response_schema": ["approve","reject","abstain"]
    }
