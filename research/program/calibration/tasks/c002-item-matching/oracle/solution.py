"""Exhaustive reference implementation for lists of at most eight rows."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _name(value):
    return " ".join((value or "").split()).casefold()


def _cents(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
        return number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def match_items(predicted, reference):
    edges = {}
    for gi, gold in enumerate(reference):
        for pi, pred in enumerate(predicted):
            name = bool(_name(pred.get("name"))) and _name(pred.get("name")) == _name(gold.get("name"))
            pc, gc = _cents(pred.get("amount")), _cents(gold.get("amount"))
            if name or (pc is not None and gc is not None and pc == gc):
                edges[gi, pi] = int(name)
    best_score, best = None, []

    def search(gi, used, pairs, names):
        nonlocal best_score, best
        if gi == len(reference):
            score = (-len(pairs), -names, tuple((g, p) for p, g in pairs))
            if best_score is None or score < best_score:
                best_score, best = score, pairs[:]
            return
        search(gi + 1, used, pairs, names)
        for pi in range(len(predicted)):
            if pi not in used and (gi, pi) in edges:
                search(gi + 1, used | {pi}, pairs + [(pi, gi)], names + edges[gi, pi])

    search(0, set(), [], 0)
    return {
        "pairs": best,
        "unmatched_predicted": [i for i in range(len(predicted)) if i not in {p for p, _ in best}],
        "unmatched_reference": [i for i in range(len(reference)) if i not in {g for _, g in best}],
    }
