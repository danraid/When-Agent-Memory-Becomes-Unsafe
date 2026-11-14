"""Opt-in OpenAI Responses advisory adapter with fail-closed per-job budget ledger.

Never treats an LLM review as independent scientific assessment. The ledger is
local to one serial GitHub Actions job, not a cross-job/global billing oracle.
"""
from __future__ import annotations
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from .budget import permit
from .evidence import sha256, write_json

ENDPOINT = 'https://api.openai.com/v1/responses'


class AdvisoryError(RuntimeError):
    pass


def _price(max_input_tokens, max_output_tokens, rates):
    try:
        i = Decimal(str(rates['input_usd_per_million']))
        o = Decimal(str(rates['output_usd_per_million']))
        if not i.is_finite() or not o.is_finite() or min(i, o) < 0:
            raise ValueError('rates must be finite and nonnegative')
        return (i * max_input_tokens + o * max_output_tokens) / Decimal('1000000')
    except (KeyError, ValueError, ArithmeticError) as exc:
        raise AdvisoryError('Explicit valid model pricing must be configured') from exc


def _reserve(ledger, config, input_bound, max_output):
    """Retains worst-case reservation, including on unknown API failures."""
    ledger = Path(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    usd = _price(input_bound, max_output, config.get('pricing', {}))
    # Locks only within one runner filesystem. Workflow concurrency protects jobs.
    with open(str(ledger) + '.lock', 'a+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            previous = json.loads(ledger.read_text()) if ledger.exists() else {
                'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'usd': '0'}
            approved, reason = permit(config['budget'], previous, calls=1,
                                      input_tokens=input_bound, output_tokens=max_output, usd=str(usd))
            if not approved:
                raise AdvisoryError('PRE_FLIGHT_BUDGET_BLOCKED: ' + reason)
            previous['calls'] += 1
            previous['input_tokens'] += input_bound
            previous['output_tokens'] += max_output
            previous['usd'] = str(Decimal(str(previous['usd'])) + usd)
            previous['accounting'] = 'CONSERVATIVE_RESERVED_NOT_PROVIDER_BILLING'
            write_json(ledger, previous)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return str(usd)


def _post_response(key, payload, timeout):
    request = urllib.request.Request(ENDPOINT, method='POST',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        raise AdvisoryError('OPENAI_HTTP_' + str(exc.code)) from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise AdvisoryError('OPENAI_TRANSPORT_UNAVAILABLE') from None


def _extract_text(response):
    pieces = []
    for part in response.get('output') or []:
        if isinstance(part, dict) and part.get('type') == 'message':
            for item in part.get('content') or []:
                if isinstance(item, dict) and item.get('type') == 'output_text':
                    pieces.append(str(item.get('text', '')))
    return '\n'.join(pieces).strip()


def request_advisory(prompt, config, ledger, *, key=None, transport=None):
    if not config.get('enabled', False):
        raise AdvisoryError('OPENAI_ADVISORY_DISABLED_BY_DEFAULT')
    model = config.get('model')
    if not isinstance(model, str) or not model.strip():
        raise AdvisoryError('Explicit OpenAI model required')
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode('utf-8')) > 50000:
        raise AdvisoryError('Prompt missing or too long')
    max_output = config.get('max_output_tokens', 256)
    if type(max_output) is not int or not 32 <= max_output <= 4096:
        raise AdvisoryError('max_output_tokens out of bounds')
    key = key or os.environ.get(config.get('secret_env', 'OPENAI_API_KEY'))
    if not key:
        raise AdvisoryError('OPENAI_API_KEY_NOT_CONFIGURED')
    # Conservative upper bound includes a fixed allowance for request overhead.
    input_bound = len(prompt.encode('utf-8')) + 2048
    reservation = _reserve(ledger, config, input_bound, max_output)
    transport = transport or _post_response
    payload = {'model': model, 'input': [{'role': 'user', 'content': prompt}],
               'max_output_tokens': max_output, 'store': False}
    try:
        response = transport(key, payload, 50)
    except AdvisoryError:
        raise
    except Exception:
        raise AdvisoryError('UNKNOWN_PROVIDER_OUTCOME_RESERVATION_RETAINED') from None
    if not isinstance(response, dict):
        raise AdvisoryError('PROVIDER_RESPONSE_INVALID_RESERVATION_RETAINED')
    usage = response.get('usage') or {}
    text = _extract_text(response)
    if not text:
        raise AdvisoryError('EMPTY_ADVISORY_NO_APPROVAL')
    return {
        'classification': 'AI_ADVISORY_NOT_INDEPENDENT_REVIEW',
        'scientific_approval': False,
        'submission_authorized': False,
        'model': model,
        'prompt_sha256': sha256(prompt.encode('utf-8')),
        'advisory_text': text,
        'provider_response_id': response.get('id'),
        'observed_usage': {
            'input_tokens': usage.get('input_tokens'),
            'output_tokens': usage.get('output_tokens'),
            'status': 'REPORTED' if isinstance(usage.get('input_tokens'), int) and isinstance(usage.get('output_tokens'), int) else 'UNKNOWN',
        },
        'conservative_reserved_usd': reservation,
    }
