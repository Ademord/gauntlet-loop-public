"""Parse extracted numeric values without propagating invalid values."""

import math

_GROUPING_CHARS = " '  "
_ASCII_DIGITS = frozenset("0123456789")


def _is_ascii_digits(s):
    return len(s) > 0 and all(ch in _ASCII_DIGITS for ch in s)


def parse_number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            result = float(value)
        except OverflowError:
            return None
        return result if math.isfinite(result) else None
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    text = "".join(ch for ch in text if ch not in _GROUPING_CHARS)
    if not text:
        return None

    sign = ""
    body = text
    if body[0] in "+-":
        sign = body[0]
        body = body[1:]
    if not body:
        return None

    has_dot = "." in body
    has_comma = "," in body

    if has_dot and has_comma:
        if body.rfind(".") > body.rfind(","):
            decimal_sep, group_sep = ".", ","
        else:
            decimal_sep, group_sep = ",", "."

        parts = body.split(decimal_sep)
        if len(parts) != 2:
            return None
        integer_part, frac_part = parts
        if not _is_ascii_digits(frac_part):
            return None

        groups = integer_part.split(group_sep)
        if len(groups) < 2:
            return None
        first_group, rest_groups = groups[0], groups[1:]
        if not (1 <= len(first_group) <= 3) or not _is_ascii_digits(first_group):
            return None
        for group in rest_groups:
            if len(group) != 3 or not _is_ascii_digits(group):
                return None

        numeral = sign + first_group + "".join(rest_groups) + "." + frac_part
    elif has_dot or has_comma:
        sep = "." if has_dot else ","
        if body.count(sep) > 1:
            return None
        integer_part, frac_part = body.split(sep)
        if not _is_ascii_digits(integer_part) or not _is_ascii_digits(frac_part):
            return None
        numeral = sign + integer_part + "." + frac_part
    else:
        if not _is_ascii_digits(body):
            return None
        numeral = sign + body

    try:
        result = float(numeral)
    except (ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None
