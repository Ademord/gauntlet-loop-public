"""Convert a duration label into seconds, or the string 'unknown'."""
import math
import re

_ISO_RE = re.compile(
    r"PT"
    r"(?:(?P<h>[0-9]+)H)?"
    r"(?:(?P<m>[0-9]+)M)?"
    r"(?:(?P<s>[0-9]+(?:\.[0-9]+)?)S)?"
)

_HUMAN_RE = re.compile(
    r"(?:about\s+)?"
    r"(?:(?P<h>[0-9]+)\s*(?:hours|hour|h))?"
    r"\s*"
    r"(?:(?P<m>[0-9]+)\s*(?:minutes|minute|min))?"
    r"\s*"
    r"(?:(?P<s>[0-9]+(?:\.[0-9]+)?)\s*(?:seconds|second|s))?",
    re.IGNORECASE,
)


def _total_from_match(match):
    if match is None:
        return None
    h, m, s = match.group("h"), match.group("m"), match.group("s")
    if h is None and m is None and s is None:
        return None
    total = 0.0
    if h is not None:
        total += float(h) * 3600
    if m is not None:
        total += float(m) * 60
    if s is not None:
        total += float(s)
    return total


def parse_duration(value):
    if not isinstance(value, str):
        return "unknown"
    text = value.strip()
    if not text:
        return "unknown"

    total = _total_from_match(_ISO_RE.fullmatch(text))
    if total is None:
        total = _total_from_match(_HUMAN_RE.fullmatch(text))
    if total is None:
        return "unknown"

    if not math.isfinite(total):
        return "unknown"
    if total == int(total):
        return int(total)
    return total
