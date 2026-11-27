"""Octen official API bridge contract; deterministic, zero external requests."""
from __future__ import annotations
import json
import unittest

from scripts.r02_octen_vendor_embedding_bridge import (
    OctenVendorEmbeddingClient, OctenBridgeError,
    response_from_vendor, MODEL, DIMENSION, ENDPOINT,
)

def payload(model=MODEL, n=1, dim=DIMENSION):
    return {
        "code": 0, "msg": "success", "request_id": "req_test_not_real",
        "data": {
            "model": model,
            "results": [
                {"index": i, "embedding": [0.01] * dim} for i in range(n)
            ],
        },
    }


class OctenBridgeTests(unittest.TestCase):
    def test_exact_model_and_output_dimensionality(self):
        p = payload(n=2)
        result = response_from_vendor(p, 2)
        self.assertEqual(result.model, MODEL)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(len(result.data[1].embedding), 4096)

    def test_rejects_model_substitution_and_bad_dimensions(self):
        with self.assertRaisesRegex(OctenBridgeError, "IDENTITY"):
            response_from_vendor(payload(model="octen-embedding-4b"), 1)
        with self.assertRaisesRegex(OctenBridgeError, "DIMENSION"):
            response_from_vendor(payload(dim=2560), 1)

    def test_rejects_nonfinite_and_missing_indexes(self):
        p = payload(n=2)
        p["data"]["results"][0]["embedding"][8] = float("nan")
        with self.assertRaisesRegex(OctenBridgeError, "NONFINITE"):
            response_from_vendor(p, 2)
        p = payload(n=2)
        p["data"]["results"][1]["index"] = 0
        with self.assertRaisesRegex(OctenBridgeError, "INDEX"):
            response_from_vendor(p, 2)

    def test_authorization_and_original_model_id(self):
        requests = []
        def transport(req):
            requests.append(req)
            return payload()
        client = OctenVendorEmbeddingClient("test-credential-not-real", transport=transport)
        result = client.embeddings.create(model=MODEL, input=["test"])
        self.assertEqual(len(result.data[0].embedding), DIMENSION)
        self.assertEqual(client.requests, 1)
        self.assertEqual(client.responses, 1)
        self.assertEqual(len(client.request_id_hashes), 1)
        self.assertEqual(requests[0].full_url, ENDPOINT)
        self.assertEqual(json.loads(requests[0].data)["input_type"], "document")
        self.assertEqual(json.loads(requests[0].data)["dimension"], DIMENSION)
        self.assertNotIn("test-credential-not-real", str(result))
        with self.assertRaisesRegex(OctenBridgeError, "DRIFT"):
            client.create(model="qwen/qwen3-embedding-8b", input=["test"])

    def test_credentials_required(self):
        with self.assertRaisesRegex(OctenBridgeError, "REQUIRED"):
            OctenVendorEmbeddingClient("")


if __name__ == "__main__":
    unittest.main()
