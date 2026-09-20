"""One valid implementation of the frozen numeric grammar."""
import math
import re


def parse_number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return None
    if isinstance(value, (int, float)):
        try:
            result = float(value)
        except OverflowError:
            return None
        return result if math.isfinite(result) else None
    text = value.strip()
    for grouping in (" ", "'", "\u00a0", "\u202f"):
        text = text.replace(grouping, "")
    if "." in text and "," in text:
        decimal = "." if text.rfind(".") > text.rfind(",") else ","
        grouping = "," if decimal == "." else "."
        pattern = r"[+-]?\d{1,3}(?:" + re.escape(grouping) + r"\d{3})+" + re.escape(decimal) + r"\d+"
        if not re.fullmatch(pattern, text, flags=re.ASCII):
            return None
        text = text.replace(grouping, "").replace(decimal, ".")
    else:
        if not re.fullmatch(r"[+-]?[0-9]+(?:[.,][0-9]+)?", text):
            return None
        text = text.replace(",", ".")
    result = float(text)
    return result if math.isfinite(result) else None
