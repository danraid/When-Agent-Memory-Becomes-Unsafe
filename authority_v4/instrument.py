"""Bounded OFFLINE authority-conflict fixtures; never a confirmatory or live instrument.

This intentionally models simulator-trusted source flags rather than verifying a
real digital signature. Events and source identifiers are model-visible, while
reference decisions and fixture families remain evaluator-only metadata.
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any

AUTHORITY_RANK = {"operator": 1, "compliance": 2, "safety": 3}
VALID_ACTIONS = {"approve", "reject", "abstain"}
SCENARIO_SCHEMA = "WAMBU-001-AUTHORITY-V4-DEV-FIXTURES-V1"


def _rank(issuer: str) -> int:
    return AUTHORITY_RANK.get(issuer, 0)


def _matches(scope: dict[str, str], request: dict[str, str]) -> bool:
    return all(scope[k] == "*" or scope[k] == request[k] for k in ("actor", "category"))


def decide(events: list[dict[str, Any]], request: dict[str, str], as_of: int) -> str:
    """Resolve known, verified, effective authorised events available at as_of.

    Higher authority wins. Within the same rank, later effective time wins.
    Conflicting top-ranked events effective at the same time are ambiguous and
    explicitly abstained; they are not silently broken by list order.
    """
    if type(as_of) is not int or as_of < 0:
        raise ValueError("INVALID_DECISION_TIME")
    rules: dict[str, dict[str, Any]] = {}
    ordered = sorted(enumerate(events), key=lambda x: (x[1]["observed_at"], x[0]))
    for _, event in ordered:
        issuer = event.get("issuer")
        if _rank(issuer) == 0:
            continue
        if not event.get("verified") or event["observed_at"] > as_of or event["effective_at"] > as_of:
            continue
        kind = event.get("kind")
        if kind == "set":
            if event.get("action") not in {"approve", "reject"}:
                raise ValueError("INVALID_SET_ACTION")
            rule_id = event["rule_id"]
            prior = rules.get(rule_id)
            if prior is None or _rank(issuer) >= _rank(prior["issuer"]):
                rules[rule_id] = event
        elif kind == "revoke":
            prior = rules.get(event["target_rule_id"])
            if prior is not None and _rank(issuer) >= _rank(prior["issuer"]):
                del rules[event["target_rule_id"]]
        else:
            raise ValueError("UNKNOWN_EVENT_KIND")
    matching = [x for x in rules.values() if _matches(x["scope"], request)]
    if not matching:
        return "approve"
    priority = max((_rank(x["issuer"]), x["effective_at"]) for x in matching)
    top_actions = {x["action"] for x in matching
                   if (_rank(x["issuer"]), x["effective_at"]) == priority}
    return next(iter(top_actions)) if len(top_actions) == 1 else "abstain"


def _event(source: str, *, kind: str = "set", issuer: str = "compliance",
           action: str = "reject", rule: str = "r1", actor: str = "*",
           category: str = "*", effective: int = 1, observed: int = 1,
           verified: bool = True, target_rule: str = "r1") -> dict[str, Any]:
    result = {"source_id": source, "kind": kind, "issuer": issuer,
              "verified": verified, "effective_at": effective, "observed_at": observed}
    if kind == "set":
        result.update({"rule_id": rule, "action": action,
                       "scope": {"actor": actor, "category": category}})
    elif kind == "revoke":
        result["target_rule_id"] = target_rule
    else:
        raise ValueError("UNKNOWN_EVENT_KIND")
    return result


def _fixtures(actor: str, category: str, other_actor: str, other_category: str):
    D = lambda source, **kw: _event(source, actor=actor, category=category, **kw)
    return [
        ("higher_authority_allow", [D("h1"), D("h2", issuer="safety", action="approve", rule="r2", effective=2)], 4),
        ("lower_authority_override", [D("l1", issuer="safety"), D("l2", issuer="operator", action="approve", rule="r2", effective=2)], 4),
        ("authorised_revocation", [D("a1"), _event("a2", kind="revoke", issuer="compliance", effective=2)], 4),
        ("unauthorised_revocation", [D("u1", issuer="safety"), _event("u2", kind="revoke", issuer="operator", effective=2)], 4),
        ("unverified_revocation", [D("v1", issuer="safety"), _event("v2", kind="revoke", issuer="safety", verified=False, effective=2)], 4),
        ("future_effect_not_yet_active", [D("f1", effective=8)], 4),
        ("future_effect_now_active", [D("f2", effective=8)], 9),
        ("different_actor_scope", [_event("s1", actor=other_actor, category=category)], 4),
        ("different_category_scope", [_event("s2", actor=actor, category=other_category)], 4),
        ("same_rank_same_time_conflict", [D("c1"), D("c2", action="approve", rule="r2")], 4),
        ("same_id_authorised_replacement", [D("r1"), D("r2", action="approve", effective=2)], 4),
        ("unverified_high_authority_allow", [D("q1", issuer="safety"), D("q2", issuer="safety", action="approve", rule="r2", effective=2, verified=False)], 4),
        ("late_arrival_before_visibility", [D("t1"), D("t2", issuer="safety", action="approve", rule="r2", effective=2, observed=9)], 4),
        ("late_arrival_after_visibility", [D("t1"), D("t2", issuer="safety", action="approve", rule="r2", effective=2, observed=9)], 10),
    ]


def make_development_episodes(seed: str, *, split: str = "development",
                              episodes: int = 2) -> list[list[dict[str, Any]]]:
    """Public-seeded offline fixtures only; rejects confirmatory and unbounded calls."""
    if split not in {"development", "pilot"}:
        raise ValueError("CONFIRMATORY_NOT_AUTHORISED")
    if not isinstance(seed, str) or len(seed) < 12 or type(episodes) is not int or not 1 <= episodes <= 12:
        raise ValueError("INVALID_OFFLINE_FIXTURE_CONFIGURATION")
    output = []
    names = ["Ada", "Boris", "Cleo", "Dara", "Evan", "Farah", "Gita"]
    categories = ["travel", "supplies", "equipment", "training", "records"]
    for ep_no in range(episodes):
        material = json.dumps([SCENARIO_SCHEMA, seed, split, ep_no], sort_keys=True)
        rng = random.Random(int(hashlib.sha256(material.encode()).hexdigest()[:16], 16))
        actor, other_actor = rng.sample(names, 2)
        category, other_category = rng.sample(categories, 2)
        request = {"actor": actor, "category": category}
        scenarios = _fixtures(actor, category, other_actor, other_category)
        rng.shuffle(scenarios)
        rows = []
        for ordinal, (family, events, as_of) in enumerate(scenarios):
            gold = decide(events, request, as_of)
            rows.append({"case_id": f"{split}-v4-{ep_no:04d}-{ordinal:02d}",
                         "episode_id": f"{split}-v4-{ep_no:04d}",
                         "fixture_family": family, "public_events": events,
                         "public_request": request.copy(),
                         "public_decision_time": as_of,
                         "reference_action": gold, "split": split})
        output.append(rows)
    return output


def model_input(case: dict[str, Any]) -> str:
    """Serialize only observations, not fixture family, split or gold labels."""
    visible = {"authority_rank": AUTHORITY_RANK,
               "event_trust_note": "verified is simulator-trusted source metadata, not a cryptographic signature",
               "events": case["public_events"],
               "request": case["public_request"],
               "decision_time": case["public_decision_time"],
               "action_schema": ["approve", "reject", "abstain"]}
    return json.dumps(visible, ensure_ascii=False, sort_keys=True)
