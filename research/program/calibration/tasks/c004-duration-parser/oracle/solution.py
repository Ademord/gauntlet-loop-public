"""Parse a whole duration string using the frozen two-format grammar."""
import math
import re


def parse_duration(value):
    if not isinstance(value, str):
        return "unknown"
    text = value.strip()
    iso = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
    human = r"(?:about\s+)?(?:(\d+)\s*(?:hours?|h)\s*)?(?:(\d+)\s*(?:minutes?|min)\s*)?(?:(\d+(?:\.\d+)?)\s*(?:seconds?|s)\s*)?"
    match = re.fullmatch(iso, text, flags=re.ASCII)
    if match is None:
        match = re.fullmatch(human, text, flags=re.ASCII | re.IGNORECASE)
    if match is None or not any(part is not None for part in match.groups()):
        return "unknown"
    seconds = sum(float(part or 0) * multiplier for part, multiplier in zip(match.groups(), (3600, 60, 1)))
    return seconds if math.isfinite(seconds) else "unknown"
