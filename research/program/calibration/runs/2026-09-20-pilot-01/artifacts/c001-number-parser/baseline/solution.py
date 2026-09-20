"""Parse extracted numeric values without propagating invalid values."""

import math
import re

_GROUPING_MARKS = (" ", "'", " ", " ")
_SIMPLE_RE = re.compile(r"^([+-]?)(\d+)(?:([.,])(\d+))?$")


def _to_finite_float(text):
    try:
        result = float(text)
    except (OverflowError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def parse_number(value):
    if isinstance(value, bool):
        return None
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            result = float(value)
        except OverflowError:
            return None
        if not math.isfinite(result):
            return None
        return result
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    for mark in _GROUPING_MARKS:
        text = text.replace(mark, "")
    if not text:
        return None

    has_dot = "." in text
    has_comma = "," in text

    if has_dot and has_comma:
        last_dot = text.rfind(".")
        last_comma = text.rfind(",")
        if last_dot > last_comma:
            decimal_char, thousand_char = ".", ","
        else:
            decimal_char, thousand_char = ",", "."

        if text.count(decimal_char) != 1:
            return None

        sign = ""
        body = text
        if body[0] in "+-":
            sign = body[0]
            body = body[1:]

        int_part, _, frac_part = body.rpartition(decimal_char)
        if not frac_part.isdigit():
            return None

        group_re = re.compile(r"^\d{1,3}(?:" + re.escape(thousand_char) + r"\d{3})+$")
        if not group_re.match(int_part):
            return None

        digits = int_part.replace(thousand_char, "")
        normalized = sign + digits + "." + frac_part
    else:
        match = _SIMPLE_RE.match(text)
        if not match:
            return None
        sign, int_digits, sep, frac_digits = match.groups()
        if sep:
            normalized = sign + int_digits + "." + frac_digits
        else:
            normalized = sign + int_digits

    return _to_finite_float(normalized)
