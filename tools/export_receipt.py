"""Check a trusted export's process result and current input/output binding.

This extracts the P008 controller's receipt check, including JSON-lines mixed-log
compatibility, and makes its surrounding nonzero-exit rejection explicit.
It only reads the caller-selected target. It never starts a process or writes a
file. A matching receipt proves neither fresh execution nor valid/readable PDF,
correct content, visual approval, or a filesystem/security boundary. Callers
retain raw results and run their independent artifact checks before acceptance.
"""
import hashlib
import json
import math
from pathlib import Path


def _json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def constant(value):
        raise ValueError('Nonfinite JSON constant')

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def _same_json(left, right):
    """Compare JSON values, without Python's True == 1 and False == 0 aliases."""
    if type(left) in (int, float) and type(right) in (int, float):
        return (not isinstance(left, float) or math.isfinite(left)) and (
            not isinstance(right, float) or math.isfinite(right)) and left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same_json(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_json(a, b) for a, b in zip(left, right))
    return type(left) in (str, bool, type(None)) and left == right


def check_export_receipt(returncode: int, stdout: bytes | str, target: Path,
                         html_raw: bytes, options: dict) -> dict:
    """Return the sole matching receipt, or raise ValueError for a failed check.

    Stdout may be one JSON document or mixed logs with complete JSON records on
    individual lines. Nonreceipt log records are ignored. All matching receipts
    count, so duplicate matches are rejected. Matching uses current artifact
    bytes, input bytes and JSON option values; JSON numbers 1 and 1.0 compare
    equally, while booleans never equal numbers. Extra receipt metadata is kept.
    Filesystem read errors propagate; the caller must also treat them as failure.
    """
    if type(returncode) is not int or returncode != 0:
        raise ValueError('Export process did not exit successfully: %r' % returncode)
    if not isinstance(html_raw, bytes) or not isinstance(options, dict):
        raise ValueError('Expected raw input bytes and an options object')
    if isinstance(stdout, bytes):
        text = stdout.decode('utf-8-sig').strip()
    elif isinstance(stdout, str):
        text = stdout.removeprefix('\ufeff').strip()
    else:
        raise ValueError('Expected byte or text stdout')
    if not text:
        raise ValueError('Export returned no receipt; exit zero alone is insufficient')
    if not target.is_file():
        raise ValueError('Expected export artifact is missing or is not a file')
    artifact_raw = target.read_bytes()
    if not artifact_raw:
        raise ValueError('Expected export artifact is empty')
    try:
        records = [_json(text)]
    except ValueError:
        records = []
        for line in text.splitlines():
            try:
                records.append(_json(line))
            except ValueError:
                continue
    input_hash = hashlib.sha256(html_raw).hexdigest()
    artifact_hash = hashlib.sha256(artifact_raw).hexdigest()
    matches = [r for r in records if isinstance(r, dict)
               and r.get('html_sha256') == input_hash
               and type(r.get('html_utf8_bytes')) is int
               and r['html_utf8_bytes'] == len(html_raw)
               and r.get('pdf_sha256') == artifact_hash
               and type(r.get('pdf_bytes')) is int
               and r['pdf_bytes'] == len(artifact_raw)
               and _same_json(r.get('pdf_options_python'), options)]
    if len(matches) != 1:
        raise ValueError('Expected exactly one receipt bound to current input, artifact and options; found %d'
                         % len(matches))
    return matches[0]
