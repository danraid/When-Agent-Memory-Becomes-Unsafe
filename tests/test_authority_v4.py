"""Offline-only regression tests for the authority-conflict candidate corpus."""
import copy
import unittest

from authority_v4.instrument import decide, make_development_episodes, model_input


class AuthorityV4Tests(unittest.TestCase):
    def setUp(self):
        self.data = make_development_episodes("authority-v4-public-seed-2026", episodes=3)

    def test_reproducible_and_split_separated(self):
        self.assertEqual(self.data, make_development_episodes("authority-v4-public-seed-2026", episodes=3))
        pilot = make_development_episodes("authority-v4-public-seed-2026", split="pilot", episodes=3)
        self.assertNotEqual(self.data[0], pilot[0])
        self.assertEqual(len(self.data), 3)
        self.assertTrue(all(len(ep) == 14 for ep in self.data))

    def test_forbid_confirmation_and_invalid_configuration(self):
        with self.assertRaisesRegex(ValueError, "CONFIRMATORY_NOT_AUTHORISED"):
            make_development_episodes("authority-v4-public-seed-2026", split="confirmatory")
        with self.assertRaisesRegex(ValueError, "INVALID_OFFLINE_FIXTURE_CONFIGURATION"):
            make_development_episodes("tiny", episodes=20)

    def test_required_authority_temporal_and_scope_behaviour(self):
        expected = {
            "higher_authority_allow": "approve",
            "lower_authority_override": "reject",
            "authorised_revocation": "approve",
            "unauthorised_revocation": "reject",
            "unverified_revocation": "reject",
            "future_effect_not_yet_active": "approve",
            "future_effect_now_active": "reject",
            "different_actor_scope": "approve",
            "different_category_scope": "approve",
            "same_rank_same_time_conflict": "abstain",
            "same_id_authorised_replacement": "approve",
            "unverified_high_authority_allow": "reject",
            "late_arrival_before_visibility": "reject",
            "late_arrival_after_visibility": "approve",
        }
        for episode in self.data:
            seen = {r["fixture_family"]: r for r in episode}
            self.assertEqual(set(seen), set(expected))
            for family, action in expected.items():
                row = seen[family]
                self.assertEqual(row["reference_action"], action, family)
                self.assertEqual(
                    decide(row["public_events"], row["public_request"], row["public_decision_time"]),
                    action, family,
                )

    def test_public_input_no_reference_leakage(self):
        for episode in self.data:
            for row in episode:
                content = model_input(row)
                self.assertNotIn("reference_action", content)
                self.assertNotIn("fixture_family", content)
                self.assertNotIn(row["case_id"], content)
                mutant = copy.deepcopy(row)
                mutant["reference_action"] = "DELIBERATELY_WRONG"
                mutant["fixture_family"] = "CHANGED"
                self.assertEqual(content, model_input(mutant))

    def test_duplicate_scenario_order_not_a_predictive_position(self):
        first = {r["fixture_family"]: i for i, r in enumerate(self.data[0])}
        second = {r["fixture_family"]: i for i, r in enumerate(self.data[1])}
        self.assertNotEqual(first, second)

    def test_ambiguity_never_silently_approves_or_rejects(self):
        conflicting = next(r for r in self.data[0] if r["fixture_family"] == "same_rank_same_time_conflict")
        self.assertEqual(conflicting["reference_action"], "abstain")
        with self.assertRaisesRegex(ValueError, "INVALID_DECISION_TIME"):
            decide([], {"actor": "Ada", "category": "travel"}, -1)


if __name__ == "__main__":
    unittest.main()
