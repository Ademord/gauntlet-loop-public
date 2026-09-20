"""Deterministic transcript measurements; no model calls or inferred reviewer roles.

Token fields describe the CLI fields we observed, not an inferred lead/subagent
split. Missing modelUsage never silently falls back to result.usage as a total.
"""
import hashlib
import json
import math
from pathlib import Path

MEASUREMENT_SCHEMA_VERSION = 2
MODEL_TOKEN_KEYS = ('inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheCreationInputTokens')
RESULT_TOKEN_KEYS = ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_identity(path):
    path = Path(path)
    return {'name': path.name, 'sha256': sha256_bytes(path.read_bytes())}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def _token_sum(usage, keys):
    if not isinstance(usage, dict) or not all(isinstance(usage.get(k), int) and not isinstance(usage[k], bool)
                                               and usage[k] >= 0 for k in keys):
        return None
    return sum(usage[k] for k in keys)


def measure_result(result):
    """Use complete modelUsage token categories and separately reconcile its cost.

    A cost mismatch is exposed, not silently repaired or used to rescale tokens.
    The actual billed subscription charge is not available in this event.
    """
    result = result if isinstance(result, dict) else {}
    models = result.get('modelUsage')
    entries = list(models.values()) if isinstance(models, dict) and models else []
    counts = [_token_sum(entry, MODEL_TOKEN_KEYS) for entry in entries]
    total = sum(counts) if counts and all(n is not None for n in counts) else None
    costs = [entry.get('costUSD') if isinstance(entry, dict) else None for entry in entries]
    model_cost = sum(costs) if costs and all(_number(c) for c in costs) else None
    event_cost = result.get('total_cost_usd')
    event_cost = event_cost if _number(event_cost) else None
    reconciles = (math.isclose(model_cost, event_cost, rel_tol=1e-9, abs_tol=1e-8)
                  if model_cost is not None and event_cost is not None else None)
    return {
        'measurement_schema_version': MEASUREMENT_SCHEMA_VERSION,
        'total_tokens': total,
        'total_tokens_source': 'result.modelUsage' if total is not None else 'unknown',
        'total_tokens_status': 'complete_categories' if total is not None else 'missing_or_incomplete_modelUsage',
        'total_tokens_categories': list(MODEL_TOKEN_KEYS),
        'result_usage_tokens': _token_sum(result.get('usage'), RESULT_TOKEN_KEYS),
        'result_usage_tokens_source': 'result.usage',
        'cost_usd': event_cost,
        'cost_usd_source': 'result.total_cost_usd' if event_cost is not None else 'unknown',
        'model_usage_cost_usd': model_cost,
        'cost_reconciles': reconciles,
        'cost_reconciliation_status': 'unknown' if reconciles is None else ('matched' if reconciles else 'mismatch'),
    }


def parse_stream(text):
    """Return final result, unique top-level Agent/Task calls, and tool counts.

    Dispatches are attempted calls, not proof of completion, reviewer identity,
    a verdict, or a revision. Repeated streamed blocks with one id count once.
    """
    result, dispatches, tools, seen = None, 0, {}, set()
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get('type') == 'result':
            result = event
        if event.get('type') != 'assistant' or event.get('parent_tool_use_id') is not None:
            continue
        message = event.get('message')
        content = message.get('content', []) if isinstance(message, dict) else []
        for item in content if isinstance(content, list) else []:
            if not isinstance(item, dict) or item.get('type') != 'tool_use':
                continue
            identity = item.get('id')
            if identity is not None and identity in seen:
                continue
            if identity is not None:
                seen.add(identity)
            name = item.get('name')
            tools[name] = tools.get(name, 0) + 1
            if name in ('Agent', 'Task'):
                dispatches += 1
    return result, dispatches, tools


def canonical_prompt(text):
    """Match make_arms: normalize file line endings, remove ONE added newline.

    Do not strip arbitrary whitespace: an extra newline or trailing space is an
    edit and must fail the committed arm_prompt_sha256 check.
    """
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if not text.endswith('\n'):
        raise ValueError('generated prompt is missing its file-appended newline')
    return text[:-1]


def validate_arm_prompts(pair, manifest):
    """Validate every arm before login preflight; return identities and frozen text."""
    hashes = manifest.get('arm_prompt_sha256')
    order = manifest.get('order')
    if not isinstance(hashes, dict) or not isinstance(order, list) or not order or set(order) != set(hashes):
        raise ValueError('manifest must bind exactly its ordered arm prompts')
    if len(order) != len(set(order)) or any(arm not in ('A', 'B') for arm in order):
        raise ValueError('manifest has duplicate or unsupported arms')
    verified = {}
    for arm in order:
        path = Path(pair) / f'arm{arm}.prompt.md'
        data = path.read_bytes()
        text = data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
        canonical_hash = sha256_bytes(canonical_prompt(text).encode('utf-8'))
        if canonical_hash != hashes[arm]:
            raise ValueError(f'arm {arm} prompt changed since generation')
        verified[arm] = {'text': text, 'canonical_sha256': canonical_hash,
                         'file_sha256': sha256_bytes(data),
                         'submitted_sha256': sha256_bytes(text.encode('utf-8'))}
    return verified


def accepted_checks(checks):
    """Unknown/missing held-out status cannot count as a passing check."""
    held = checks.get('held_out_passed')
    return checks.get('suite_rc') == 0 and not checks.get('out_of_scope') and (held is True or held == 'not applicable')
