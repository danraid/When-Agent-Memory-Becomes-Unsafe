"""SHA256 source identity and repeatable synthetic diagnostic fixture."""
import hashlib
import json
from pathlib import Path
import random


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def smoke(seed=2026, n=64):
    if n < 2 or n > 100000:
        raise ValueError('Fixture sample size out of bounds')
    rng = random.Random(seed)
    values = [rng.random() for _ in range(n)]
    return {'classification': 'SYNTHETIC_TEST_FIXTURE', 'science_claim': False, 'seed': seed,
            'runner': 'python_stdlib_smoke_v1', 'n': n, 'mean': round(sum(values)/n, 9),
            'data_sha256': sha256(canonical(values))}


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')
