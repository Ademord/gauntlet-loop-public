"""Convert a duration label into seconds, or the string 'unknown'."""
import re


def parse_duration(value):
    if not isinstance(value, str):
        return "unknown"
    found = re.search(r"(\d+)\s*(h|min|s)", value)
    if not found:
        return "unknown"
    return int(found.group(1)) * {"h": 3600, "min": 60, "s": 1}[found.group(2)]
