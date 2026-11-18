"""R02 live Knowledge Triage cascade on public *development-only* test text.

Uses pinned upstream CascadeClassifier / EncoderClassifier without source edits.
Run the original author providers when the exact secrets are available; otherwise
use separately labelled REAL, ADAPTED OpenRouter embedding and LLM providers.

Never reads protected casebooks, scores against gold, or submits to a journal.
Failure reports do not contain URLs, keys, headers, full exception messages or PII.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

PIN = "a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4"
ORIGINAL_EMBEDDING = "octen-embedding-8b"
ORIGINAL_LLM = "gpt-5.4-mini"
ADAPTED_EMBEDDING = "qwen/qwen3-embedding-8b"
ADAPTED_LLM = "openai/gpt-4.1-mini"
EXAMPLES = (
    ("regex", "Never commit secrets to version control."),
    ("encoder", "A catalog contains a blue widget."),
    ("uncertain", "A catalog contains a green widget."),
)
MIN_EXPECTED_REAL_PROVIDER_REQUESTS = 2


def provider_error(exc: Exception) -> dict:
    """Scrub secrets/URLs/response bodies from errors."""
    return {"type": type(exc).__name__,
            "http_status": getattr(exc, "status_code", None) if isinstance(
                getattr(exc, "status_code", None), int) else None}


def credentials(environ: dict) -> dict:
    return {
        "octen_vendor_secret": bool(environ.get("OCTEN_API_KEY")),
        "original_embedding_secret": bool(environ.get("CUSTOM_LLM_API_KEY")),
        "original_embedding_endpoint": bool(environ.get("CUSTOM_LLM_ENDPOINT")),
        "original_llm_secret": bool(environ.get("OPENAI_API_KEY")),
        "openrouter_secret": bool(environ.get("OPENROUTER_API_KEY") or environ.get("OPENROUTER")),
    }


class AdaptedEmbeddings:
    def __init__(self, real_client):
        self.real_client = real_client
        self.embeddings = self
        self.requests = 0
        self.model_seen = None

    def create(self, *, model: str, input: list[str]):
        # The original encoder requests octen-embedding-8b. This explicit
        # *method substitution* is recorded and never called original parity.
        if model != ORIGINAL_EMBEDDING:
            raise ValueError("ORIGINAL_ENCODER_REQUEST_CONTRACT_DRIFT")
        response = self.real_client.embeddings.create(model=ADAPTED_EMBEDDING, input=input)
        self.requests += 1
        self.model_seen = getattr(response, "model", ADAPTED_EMBEDDING)
        return response


class AdaptedAdjudicator:
    def __init__(self, real_client):
        self.real_client = real_client
        self.requests = 0
        self.last_id = None
        self.last_model = None

    def complete(self, messages, *, max_tokens=512, temperature=0.0,
                 purpose="", cap_usd=5.0, **kwargs):
        if purpose != "classifier_adjudicator":
            raise ValueError("UNEXPECTED_ADJUDICATOR_CALL")
        response = self.real_client.chat.completions.create(
            model=ADAPTED_LLM, messages=messages,
            max_tokens=min(512, max_tokens), temperature=temperature)
        self.requests += 1
        self.last_id = getattr(response, "id", None)
        self.last_model = getattr(response, "model", ADAPTED_LLM)
        return type("LiveResult", (), {"text": response.choices[0].message.content or ""})()


def original_providers():
    from openai import OpenAI
    from knowledge_triage.clients import get_client
    # The SDK will never log its bearer token in this script.
    embed = OpenAI(api_key=os.environ["CUSTOM_LLM_API_KEY"],
                   base_url=os.environ["CUSTOM_LLM_ENDPOINT"].rstrip("/") + "/v1",
                   timeout=22, max_retries=0)
    # Preserve the exact original model selection through the upstream factory.
    adjudicator = get_client("openai:gpt-5.4-mini")
    return embed, adjudicator


def octen_vendor_providers():
    from knowledge_triage.clients import get_client
    from scripts.r02_octen_vendor_embedding_bridge import OctenVendorEmbeddingClient
    embed = OctenVendorEmbeddingClient(os.environ["OCTEN_API_KEY"])
    adjudicator = get_client("openai:gpt-5.4-mini")
    return embed, adjudicator


def adapted_providers():
    from openai import OpenAI
    token = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER")
    sdk = OpenAI(api_key=token, base_url="https://openrouter.ai/api/v1",
                 timeout=22, max_retries=0)
    return AdaptedEmbeddings(sdk), AdaptedAdjudicator(sdk)


def execute_one(mode, CascadeClassifier, EncoderClassifier, K):
    """Exactly one live provider lane. On failure, preserve its failure record."""
    from knowledge_triage.classifier_cascade import PROTOTYPES
    provider_count = 0
    if mode == "ORIGINAL":
        embed, adjudicator = original_providers()
        actual_embedding = ORIGINAL_EMBEDDING
        actual_adjudicator = ORIGINAL_LLM
        # One small real request first; avoid an upstream five-retry train loop
        # on a missing proprietary endpoint.
        check = embed.embeddings.create(
            model=ORIGINAL_EMBEDDING,
            input=[PROTOTYPES[K.CONSTRAINT][0]])
        if not check.data or not check.data[0].embedding:
            raise ValueError("ORIGINAL_EMBEDDING_EMPTY")
        provider_count += 1
    elif mode == "OCTEN_VENDOR_AND_ORIGINAL_LLM":
        embed, adjudicator = octen_vendor_providers()
        actual_embedding = ORIGINAL_EMBEDDING
        actual_adjudicator = ORIGINAL_LLM
        check = embed.embeddings.create(
            model=ORIGINAL_EMBEDDING,
            input=[PROTOTYPES[K.CONSTRAINT][0]])
        if not check.data or not check.data[0].embedding:
            raise ValueError("OCTEN_VENDOR_EMBEDDING_EMPTY")
        provider_count += 1
    elif mode == "ADAPTED_OPENROUTER":
        embed, adjudicator = adapted_providers()
        actual_embedding = ADAPTED_EMBEDDING
        actual_adjudicator = ADAPTED_LLM
        check = embed.embeddings.create(
            model=ORIGINAL_EMBEDDING,
            input=[PROTOTYPES[K.CONSTRAINT][0]])
        if not check.data or not check.data[0].embedding:
            raise ValueError("ADAPTED_EMBEDDING_EMPTY")
        provider_count += 1
    else:
        raise ValueError("INVALID_LANE")

    # These fit and predict calls execute the exact original EncoderClassifier,
    # with a real provider. In the adapted lane, only the service is substituted.
    encoder = EncoderClassifier()
    encoder.fit(embed)
    ordinary = CascadeClassifier(encoder=encoder, llm_client=adjudicator,
                                 use_llm=True)
    out = []
    for label, item in EXAMPLES:
        pred = ordinary.predict(item)
        out.append({
            "test_id": label, "item_sha256": hashlib.sha256(item.encode()).hexdigest(),
            "type": pred.type.value, "decided_by": pred.decided_by,
            "confidence": round(float(pred.confidence), 6),
            "abstained": bool(pred.abstained),
        })
    # A deliberate DIAGNOSTIC with threshold 1.01 forces the original
    # LLM-adjudication code path, if the unmodified default did not reach it.
    # This overrides a parameter for coverage, NOT a published-method trial.
    changed_threshold = False
    if not any(x["decided_by"] == "llm" for x in out):
        diagnostic = CascadeClassifier(
            encoder=encoder, llm_client=adjudicator,
            encoder_threshold=1.01, use_llm=True)
        pred = diagnostic.predict("A catalog contains a gold widget.")
        changed_threshold = True
        out.append({
            "test_id": "forced_escalation_diagnostic",
            "item_sha256": hashlib.sha256(
                b"A catalog contains a gold widget.").hexdigest(),
            "type": pred.type.value, "decided_by": pred.decided_by,
            "confidence": round(float(pred.confidence), 6),
            "abstained": bool(pred.abstained),
        })
    if isinstance(embed, AdaptedEmbeddings):
        provider_count += embed.requests
    elif mode == "OCTEN_VENDOR_AND_ORIGINAL_LLM":
        provider_count += embed.requests
    # Original mode provider count is lower bound: 1 probe + 5 prototype
    # batches + per-case embeddings; no response count is fabricated.
    else:
        provider_count += 5 + sum(x["decided_by"] != "regex" for x in out)
    llm_observed = any(x["decided_by"] == "llm" for x in out)
    return {
        "lane": mode, "status": "LIVE_PROVIDERS_EXECUTED",
        "source_is_original_unmodified": True,
        "embedding_model_requested": actual_embedding,
        "adjudicator_model_requested": actual_adjudicator,
        "classification_results": out,
        "original_default_cascade_runs": len(EXAMPLES),
        "forced_escalation_parameter_changed": changed_threshold,
        "llm_decision_observed": llm_observed,
        "provider_request_lower_bound": provider_count,
        "original_models_executed": mode == "ORIGINAL",
        "vendor_original_model_pair_used": mode == "OCTEN_VENDOR_AND_ORIGINAL_LLM",
        "original_author_endpoint_proven": mode == "ORIGINAL",
        "adapted_models_executed": mode == "ADAPTED_OPENROUTER",
        "published_benchmark_reproduced": False,
        "source_vs_method_parity": ("ORIGINAL_CLASSIFIER_RUNTIME_NOT_PAPER_BENCHMARK"
                                    if mode == "ORIGINAL"
                                    else "ORIGINAL_MODEL_IDS_VENDOR_ENDPOINT_NOT_AUTHOR_ENDPOINT"
                                    if mode == "OCTEN_VENDOR_AND_ORIGINAL_LLM"
                                    else "ADAPTED_SERVICE_MODELS_NOT_ORIGINAL"),
    }


def run(upstream: Path, environ: dict):
    upstream = upstream.resolve()
    sha = subprocess.run(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"],
        text=True, capture_output=True, check=True).stdout.strip()
    if sha != PIN:
        raise ValueError("ORIGINAL_COMMIT_MISMATCH")
    if not environ.get("R02_ALLOW_LIVE_CALLS") == "true":
        raise ValueError("NO_EXPLICIT_LIVE_PILOT_SCOPE")
    sys.path.insert(0, str(upstream))
    from knowledge_triage.classifier_cascade import CascadeClassifier, EncoderClassifier
    from knowledge_triage.classifier import KnowledgeType as K

    caps = credentials(environ)
    complete_original = all(caps[k] for k in (
        "original_embedding_secret", "original_embedding_endpoint",
        "original_llm_secret"))
    attempts = []
    # Priority: original author services, original model IDs via Octen vendor,
    # then transparently adapted OpenRouter models. No implied endpoint parity.
    lanes = []
    if complete_original:
        lanes.append("ORIGINAL")
    if caps["octen_vendor_secret"] and caps["original_llm_secret"]:
        lanes.append("OCTEN_VENDOR_AND_ORIGINAL_LLM")
    if caps["openrouter_secret"]:
        lanes.append("ADAPTED_OPENROUTER")
    completed = None
    for mode in lanes:
        try:
            outcome = execute_one(mode, CascadeClassifier, EncoderClassifier, K)
            attempts.append({"lane": mode, "status": "SUCCESS"})
            completed = outcome
            break
        except Exception as exc:
            attempts.append({"lane": mode, "status": "FAILED",
                             "error": provider_error(exc)})
    return {
        "schema": "WAMBU-R02-LIVE-CASCADE-DEVELOPMENT-PILOT-V1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": sha,
        "source_classifier_sha256": hashlib.sha256(
            (upstream/"knowledge_triage/classifier_cascade.py").read_bytes()).hexdigest(),
        "provider_capabilities_present_without_values": caps,
        "status": ("REAL_CASCADE_COMPLETE" if completed else
                   "BLOCKED_NO_ACCESSIBLE_LIVE_CASCADE"),
        "attempts": attempts,
        "result": completed,
        "octen_vendor_endpoint_not_author_endpoint": True,
        "original_source_unchanged": True,
        "gold_labels": 0,
        "human_adjudications": 0,
        "protected_holdout_access": False,
        "confirmatory_protocol_frozen": False,
        "author_approval": False,
        "external_journal_submission": False,
        "full_original_knowledge_triage_replication": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run(args.upstream, os.environ)
    except Exception as exc:
        # No exception text with possible secret-bearing HTTP URLs.
        report = {"schema": "WAMBU-R02-LIVE-CASCADE-DEVELOPMENT-PILOT-V1",
                  "status": "PRECONDITION_FAILED",
                  "error": provider_error(exc),
                  "full_original_knowledge_triage_replication": False,
                  "external_journal_submission": False,
                  "protected_holdout_access": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "lanes": [a["lane"] + ":" + a["status"] for a in report.get("attempts", [])],
        "original_paper_replication": False,
    }))
    return 0  # Genuine runtime access failure is preserved as BLOCKED evidence.


if __name__ == "__main__":
    raise SystemExit(main())
