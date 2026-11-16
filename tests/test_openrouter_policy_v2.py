"""Offline tests for v2 safety pilot. No real API calls or holdout access."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from study.openrouter_comparison import BenchmarkError
from study.openrouter_policy_safety_v2 import (
    PacedTransport, load_config, run, SafetyPilotError,
)


class _FakeTime:
    def __init__(self):
        self.t = 0.
        self.slept = []

    def clock(self):
        return self.t

    def sleep(self, delay):
        self.slept.append(delay)
        self.t += delay


class PolicyV2Tests(unittest.TestCase):
    def test_predeclared_new_dev_sample_finite(self):
        config, hash_ = load_config(Path("study/openrouter_policy_v2_models.json"))
        self.assertEqual(config["schema_version"], 2)
        self.assertEqual(config["episodes"], 4)
        self.assertEqual(len(config["decision_models"]), 4)
        self.assertEqual(len(hash_), 64)
        self.assertNotIn("V1-PUBLIC", config["development_seed"])
        self.assertFalse(config["confirmatory_allowed"])
        self.assertEqual(4 * (5 + 18 * 16), 1172)
        self.assertLessEqual(1172, config["max_calls"])

    def test_pacing_is_scoped_to_model_and_never_retries_429(self):
        t = _FakeTime()
        called = Counter()

        def endpoint(key, payload):
            model = payload["model"]
            called[model] += 1
            if model == "provider/gemini" and called[model] == 1:
                raise BenchmarkError("OPENROUTER_HTTP_429")
            return {"id": "ok", "choices": [{"message": {"content": "ok"}}]}

        p = PacedTransport(model_intervals={"provider/gemini": 2., "provider/other": 0.},
                           cooldown_429=30., transport=endpoint,
                           clock=t.clock, sleeper=t.sleep)
        with self.assertRaisesRegex(BenchmarkError, "429"):
            p("test", {"model": "provider/gemini"})
        self.assertEqual(called["provider/gemini"], 1)
        p("test", {"model": "provider/other"})
        self.assertEqual(t.t, 0.)
        p("test", {"model": "provider/gemini"})
        self.assertEqual(called["provider/gemini"], 2)
        self.assertEqual(t.t, 30.)
        self.assertEqual(p.rate_limit_events["provider/gemini"], 1)

    def test_offline_complete_paired_episodes_mocked_transport(self):
        config = json.loads(Path("study/openrouter_policy_v2_models.json").read_text())
        config["episodes"] = 1
        config["steps"] = 18
        config["max_calls"] = 350
        config["model_min_interval_seconds"] = {
            model: 0. for model in config["model_min_interval_seconds"]
        }
        config["cooldown_after_429_seconds"] = 0.
        ids = []
        def endpoint(key, payload):
            new_id = "mock-offline-id-" + str(len(ids))
            ids.append(new_id)
            prompt = payload["messages"][0]["content"]
            value = "Summary of authorised events" if "UPDATED COMPACTED MEMORY:" in prompt else '{"action":"reject"}'
            return {"id": new_id, "model": payload["model"],
                    "choices": [{"message": {"content": value}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 25, "completion_tokens": 10}}
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)/"config.json"
            cfg.write_text(json.dumps(config))
            result = run(cfg, Path(tmp)/"artifact", "fake-key", transport=endpoint)
            self.assertEqual(result["status"], "EXPLORATORY_FULLY_SCORED_NOT_SCIENTIFICALLY_APPROVED")
            self.assertEqual(result["expected_evaluable_rows"], 360)
            self.assertEqual(result["evaluable_rows"], 360)
            self.assertEqual(result["provider_calls_reserved"], 293)
            self.assertEqual(result["observed_compactions"], 5)
            self.assertFalse(result["holdout_touched"])
            self.assertEqual(len(set(ids)), 293)
            metadata = json.loads((Path(tmp)/"artifact/run_metadata.json").read_text())
            self.assertTrue(metadata["model_role_effect"].startswith("DECISION_MODELS"))
            self.assertEqual(metadata["split"], "development")

    def test_invalid_pacing_policy_is_rejected(self):
        config = json.loads(Path("study/openrouter_policy_v2_models.json").read_text())
        config["model_min_interval_seconds"].pop("google/gemini-2.5-flash")
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.json"
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(SafetyPilotError, "RATE_POLICY"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
