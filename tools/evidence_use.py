"""Compare caller-selected evidence conditions; never establish their truth.

``assess_use(evidence, proposed_use, current_context)`` is a read-only, no-model
helper. A trusted host selects material conditions and independently supplies
their expected values. A condition's source is either ``evidence`` (recorded
bindings) or ``context`` (current host observations). In particular, a receipt's
self-description does not establish current permission or independent review.

Example request for the JSON-on-stdin CLI::

    {"evidence": {"id": "E1", "bindings": {"artifact": "a1"}},
     "proposed_use": {"kind": "current_acceptance", "claim": "local check",
                      "material_conditions": {"artifact": "evidence",
                                              "review": "context"}},
     "current_context": {"expected_conditions": {"artifact": "a1",
                                                   "review": "verified"},
                         "observed_conditions": {"review": "verified"}}}

All selected conditions must match; absent or null values mean unknown. Other
fields never become implicit gates. Historical reporting uses the caller's
historical expectations, not automatically today's lifecycle. To additionally
assess an earlier claim, provide ``historical_expectations`` in the context;
these compare only recorded evidence bindings. No date parsing or truth oracle
is implied. ``eligible`` means only that these supplied conditions match; it is
not authorization, independent review, execution, or full task acceptance.

Lineage retains root observation IDs and derivation IDs. When independent
support is selected, count distinct roots also present in the host's
``verified_observation_ids``. IDs alone cannot prove real independence; the host
must establish that relation. Copies must retain the same root IDs. Missing
lineage stays unknown, rather than manufacturing independent observations.

CLI exit: 0 eligible, 1 ineligible, 2 unknown (including malformed input). Reads
at most 64 KiB from stdin and writes only a JSON result to stdout. No files,
processes, network, code evaluation, model calls, ranking, or state mutation.
JSON decimal tokens are compared exactly (at most 256 coefficient digits and
an exponent of magnitude at most 1024); unsupported values return unknown.
Direct Python callers can pass Decimal for the same semantics. Already-rounded
Python floats carry only their existing binary value; lost source precision
cannot be recovered or certified by this helper.
"""

from decimal import Decimal, InvalidOperation
import json
import math
import re
import sys


MAX_BYTES = 65536
MAX_DEPTH = 8
MAX_NODES = 4096
MAX_ITEMS = 64
MAX_STRING = 4096
KINDS = frozenset({"historical_report", "investigation", "current_acceptance",
                   "consequential_action"})
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,79}\Z")
_MISSING = object()


def _valid_decimal(value):
    return (value.is_finite() and len(value.as_tuple().digits) <= 256
            and abs(value.as_tuple().exponent) <= 1024)


def _bounded(value, depth=0, counter=None):
    counter = [0] if counter is None else counter
    counter[0] += 1
    if depth > MAX_DEPTH or counter[0] > MAX_NODES:
        raise ValueError("input exceeds structural limit")
    kind = type(value)
    if kind is str:
        if len(value) > MAX_STRING:
            raise ValueError("string exceeds limit")
    elif kind in (bool, type(None)):
        pass
    elif kind in (int, float):
        if (kind is float and not math.isfinite(value)) or (kind is int and value.bit_length() > 1024):
            raise ValueError("invalid or oversized number")
    elif kind is Decimal:
        if not _valid_decimal(value):
            raise ValueError("unsupported decimal precision or exponent")
    elif kind in (dict, list):
        if len(value) > MAX_ITEMS:
            raise ValueError("collection exceeds limit")
        if kind is dict:
            for key, item in value.items():
                if type(key) is not str or len(key) > 80:
                    raise ValueError("invalid object key")
                _bounded(item, depth + 1, counter)
        else:
            for item in value:
                _bounded(item, depth + 1, counter)
    else:
        raise ValueError("input must contain only JSON values")


def _object(value, allowed, required=()):
    if type(value) is not dict or set(value) - allowed or not set(required) <= set(value):
        raise ValueError("missing or unsupported fields")


def _identifier(value):
    if (type(value) is not str or not value.strip() or len(value) > 128
            or any(ord(c) < 32 for c in value)):
        raise ValueError("invalid identifier")


def _names(value):
    if type(value) is not dict or any(not _NAME.fullmatch(k) for k in value):
        raise ValueError("invalid condition names")


def _ids(value):
    if type(value) is not list:
        raise ValueError("observation IDs must be a list")
    for item in value:
        _identifier(item)
    return sorted(set(value))


def _same(left, right):
    # True/1 and False/0 must not satisfy each other's contracts.
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def _conditions(selected, expected, bindings, observations):
    unmet = []
    for name, source in selected.items():
        wanted = expected.get(name, _MISSING)
        actual = (bindings if source == "evidence" else observations).get(name, _MISSING)
        if wanted is _MISSING or wanted is None or actual is _MISSING or actual is None:
            unmet.append({"condition": name, "reason": "unknown_material_value"})
        elif not _same(actual, wanted):
            unmet.append({"condition": name, "reason": "condition_mismatch"})
    return unmet


def _status(unmet):
    if any(x["reason"] in {"condition_mismatch", "insufficient_independent_support"} for x in unmet):
        return "ineligible"
    return "unknown" if unmet else "eligible"


def _unknown(detail):
    return {"status": "unknown", "historical_validity": "unknown",
            "material_unmet": [{"condition": "input", "reason": "invalid_input", "detail": detail}],
            "lineage": {"root_observation_ids": [], "derived_from": [],
                        "verified_root_observation_ids": []},
            "next_observations": [], "can_investigate": False}


def assess_use(evidence, proposed_use, current_context):
    """Return condition eligibility, preserving uncertainty and supplied lineage.

    No input is modified. Malformed inputs return unknown. A known failed
    material condition makes the use ineligible even if another is unknown;
    missing knowledge never cancels a known contradiction.
    """
    try:
        _bounded([evidence, proposed_use, current_context])
        _object(evidence, {"id", "bindings", "lineage"}, {"id"})
        _identifier(evidence["id"])
        bindings = evidence.get("bindings", {})
        _names(bindings)
        _object(proposed_use, {"kind", "claim", "material_conditions",
                               "minimum_independent_observations"},
                {"kind", "claim", "material_conditions"})
        if proposed_use["kind"] not in KINDS:
            raise ValueError("unsupported use kind")
        _identifier(proposed_use["claim"])
        selected = proposed_use["material_conditions"]
        _names(selected)
        if len(selected) > 32 or any(type(v) is not str or v not in {"evidence", "context"} for v in selected.values()):
            raise ValueError("invalid material condition source")
        minimum = proposed_use.get("minimum_independent_observations", 0)
        if type(minimum) is not int or not 0 <= minimum <= MAX_ITEMS:
            raise ValueError("invalid independent support requirement")
        _object(current_context, {"expected_conditions", "observed_conditions",
                                  "historical_expectations", "verified_observation_ids",
                                  "investigation_authorized", "investigation_read_only"},
                {"expected_conditions"})
        expected = current_context["expected_conditions"]
        observed = current_context.get("observed_conditions", {})
        historical = current_context.get("historical_expectations", {})
        for values in (expected, observed, historical):
            _names(values)
        for name in ("investigation_authorized", "investigation_read_only"):
            if name in current_context and type(current_context[name]) is not bool:
                raise ValueError("investigation flags must be booleans")
        lineage = evidence.get("lineage", {})
        _object(lineage, {"root_observation_ids", "derived_from"})
        roots = _ids(lineage.get("root_observation_ids", []))
        parents = _ids(lineage.get("derived_from", []))
        verified = _ids(current_context.get("verified_observation_ids", []))
        corroborated = sorted(set(roots).intersection(verified))
        unmet = _conditions(selected, expected, bindings, observed)
        if not selected:
            unmet.append({"condition": "material_conditions", "reason": "no_material_conditions_selected"})
        if minimum and len(corroborated) < minimum:
            known = bool(roots) and "verified_observation_ids" in current_context
            unmet.append({"condition": "independent_support", "reason":
                          "insufficient_independent_support" if known else "unknown_material_value"})
        historical_status = "unknown"
        if historical:
            historical_status = _status(_conditions({k: "evidence" for k in historical}, historical, bindings, {}))
        elif proposed_use["kind"] == "historical_report":
            historical_status = _status(unmet)
        return {"status": _status(unmet), "evidence_id": evidence["id"],
                "use_kind": proposed_use["kind"], "claim": proposed_use["claim"],
                "historical_validity": historical_status, "material_unmet": unmet,
                "lineage": {"root_observation_ids": roots, "derived_from": parents,
                            "verified_root_observation_ids": corroborated},
                "next_observations": ["Establish " + x["condition"] + " for this use" for x in unmet],
                "can_investigate": current_context.get("investigation_authorized") is True
                                   and current_context.get("investigation_read_only") is True}
    except (ValueError, TypeError, RecursionError):
        return _unknown("invalid or unbounded assessment input")


def _decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("nonfinite number")

    def decimal(text):
        # Parse the original token, never an intermediate binary float.
        if len(text) > 2048:
            raise ValueError("decimal token exceeds limit")
        try:
            value = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError("unsupported decimal token") from exc
        if not _valid_decimal(value):
            raise ValueError("unsupported decimal precision or exponent")
        return value

    data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant, parse_float=decimal)
    _object(data, {"evidence", "proposed_use", "current_context"},
            {"evidence", "proposed_use", "current_context"})
    return data


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError("CLI accepts JSON on stdin only")
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("input exceeds byte limit")
        data = _decode(raw)
        result = assess_use(**data)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        result = _unknown("expected bounded UTF-8 JSON assessment on stdin")
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return {"eligible": 0, "ineligible": 1, "unknown": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
