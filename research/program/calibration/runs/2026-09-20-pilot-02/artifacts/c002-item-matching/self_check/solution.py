"""Match predicted and reference rows, returning original row indices."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from functools import lru_cache


def _normalize_name(value):
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split()).casefold()
    return normalized or None


def _parse_amount(value):
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (int, float, str)):
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite():
        return None
    digit_count = len(amount.as_tuple().digits)
    try:
        with localcontext() as ctx:
            ctx.prec = max(digit_count, 28) + 10
            return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None


def match_items(predicted, reference):
    num_predicted = len(predicted)
    num_reference = len(reference)

    names_p = [_normalize_name(row.get("name")) for row in predicted]
    names_r = [_normalize_name(row.get("name")) for row in reference]
    amounts_p = [_parse_amount(row.get("amount")) for row in predicted]
    amounts_r = [_parse_amount(row.get("amount")) for row in reference]

    name_match = [
        [
            names_p[p] is not None and names_p[p] == names_r[r]
            for r in range(num_reference)
        ]
        for p in range(num_predicted)
    ]
    edge = [
        [
            name_match[p][r]
            or (
                amounts_p[p] is not None
                and amounts_r[r] is not None
                and amounts_p[p] == amounts_r[r]
            )
            for r in range(num_reference)
        ]
        for p in range(num_predicted)
    ]

    def is_better(candidate, current):
        if candidate[0] != current[0]:
            return candidate[0] > current[0]
        if candidate[1] != current[1]:
            return candidate[1] > current[1]
        return candidate[2] < current[2]

    @lru_cache(maxsize=None)
    def solve(ref_idx, mask):
        if ref_idx == num_reference:
            return (0, 0, ())
        best = solve(ref_idx + 1, mask)
        for p in range(num_predicted):
            if mask & (1 << p) or not edge[p][ref_idx]:
                continue
            sub_count, sub_weight, sub_pairs = solve(ref_idx + 1, mask | (1 << p))
            candidate = (
                sub_count + 1,
                sub_weight + (1 if name_match[p][ref_idx] else 0),
                ((ref_idx, p),) + sub_pairs,
            )
            if is_better(candidate, best):
                best = candidate
        return best

    _, _, best_pairs = solve(0, 0)
    solve.cache_clear()

    pairs = [(p, r) for r, p in best_pairs]
    matched_predicted = {p for p, _ in pairs}
    matched_reference = {r for _, r in pairs}

    return {
        "pairs": pairs,
        "unmatched_predicted": [i for i in range(num_predicted) if i not in matched_predicted],
        "unmatched_reference": [i for i in range(num_reference) if i not in matched_reference],
    }
