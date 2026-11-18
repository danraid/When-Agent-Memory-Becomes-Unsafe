"""Authenticated Octen vendor embedding bridge for the pinned Knowledge Triage encoder.

The source reference uses an OpenAI-compatible embeddings interface while the
official Octen API uses POST /embedding and a different JSON response shape.
This adapter preserves the actual upstream EncoderClassifier calls and changes
only the serving transport. It must NOT be called the authors' original endpoint.

Documentation: https://docs.octen.ai/api-reference/embedding
No API keys, input texts, embeddings, or untrusted response bodies are logged.
"""
from __future__ import annotations

import hashlib
import json
import math
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "octen-embedding-8b"
DIMENSION = 4096
ENDPOINT = "https://api.octen.ai/embedding"


class OctenBridgeError(RuntimeError):
    """Code-only safe error, not a provider body or secret-bearing exception."""


def response_from_vendor(payload: dict, expected: int):
    if payload.get("code") != 0:
        raise OctenBridgeError("OCTEN_NON_SUCCESS_CODE")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise OctenBridgeError("OCTEN_MISSING_DATA")
    if data.get("model") != MODEL:
        raise OctenBridgeError("OCTEN_MODEL_IDENTITY_NOT_CONFIRMED")
    records = data.get("results")
    if not isinstance(records, list) or len(records) != expected:
        raise OctenBridgeError("OCTEN_RESULT_COUNT_MISMATCH")
    by_id = {}
    for item in records:
        idx = item.get("index")
        vector = item.get("embedding")
        if not isinstance(idx, int) or isinstance(idx, bool) or idx in by_id:
            raise OctenBridgeError("OCTEN_RESULT_INDEX_INVALID")
        if idx < 0 or idx >= expected or not isinstance(vector, list):
            raise OctenBridgeError("OCTEN_RESULT_SHAPE_INVALID")
        if len(vector) != DIMENSION:
            raise OctenBridgeError("OCTEN_DIMENSION_MISMATCH")
        if not all(type(v) in (float, int) and math.isfinite(v) for v in vector):
            raise OctenBridgeError("OCTEN_NONFINITE_VECTOR")
        by_id[idx] = SimpleNamespace(index=idx, embedding=vector)
    if len(by_id) != expected:
        raise OctenBridgeError("OCTEN_MISSING_INDEX")
    return SimpleNamespace(model=MODEL, data=[by_id[i] for i in range(expected)])


class OctenVendorEmbeddingClient:
    def __init__(self, api_key: str, transport=None):
        if not isinstance(api_key, str) or not api_key.strip():
            raise OctenBridgeError("OCTEN_API_KEY_REQUIRED")
        self._api_key = api_key
        self._transport = transport
        self.embeddings = self
        self.requests = 0
        self.responses = 0
        self.request_id_hashes: list[str] = []

    def _send(self, body):
        req = Request(ENDPOINT, method="POST",
                      headers={"Authorization": "Bearer " + self._api_key,
                               "Content-Type": "application/json",
                               "User-Agent": "WAMBU-R02-OctenBridge/1"},
                      data=json.dumps(body, separators=(",", ":")).encode("utf-8"))
        try:
            if self._transport is not None:
                return self._transport(req)
            with urlopen(req, timeout=35) as stream:
                return json.load(stream)
        except HTTPError as exc:
            raise OctenBridgeError("OCTEN_HTTP_" + str(exc.code)) from None
        except (URLError, TimeoutError):
            raise OctenBridgeError("OCTEN_TRANSPORT_UNAVAILABLE") from None

    def create(self, *, model: str, input: list[str]):
        # Unmodified upstream code asks for the Octen model under this exact id.
        if model != MODEL:
            raise OctenBridgeError("ORIGINAL_ENCODER_REQUEST_MODEL_DRIFT")
        if not isinstance(input, list) or not 1 <= len(input) <= 1000:
            raise OctenBridgeError("OCTEN_INPUT_BATCH_INVALID")
        if any(not isinstance(t, str) or not t or len(t) > 10000 for t in input):
            raise OctenBridgeError("OCTEN_INPUT_TEXT_INVALID")
        body = {"model": MODEL, "dimension": DIMENSION,
                "input_type": "document", "input": input}
        # 'document' applies no query-instruction prefix; the original source
        # passes unprefixed prototypes and input texts.
        self.requests += 1
        try:
            response = self._send(body)
            result = response_from_vendor(response, len(input))
            self.responses += 1
            rid = response.get("request_id")
            if isinstance(rid, str) and rid:
                self.request_id_hashes.append(hashlib.sha256(rid.encode()).hexdigest())
            return result
        except OctenBridgeError:
            raise
        except (ValueError, TypeError, KeyError):
            raise OctenBridgeError("OCTEN_INVALID_RESPONSE") from None
