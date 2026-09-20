"""Match predicted and reference rows, returning original row indices."""


def match_items(predicted, reference):
    pairs = []
    used = set()
    for gi, gold in enumerate(reference):
        for pi, pred in enumerate(predicted):
            if pi not in used and (pred.get("name") == gold.get("name") or pred.get("amount") == gold.get("amount")):
                pairs.append((pi, gi))
                used.add(pi)
                break
    return {
        "pairs": pairs,
        "unmatched_predicted": [i for i in range(len(predicted)) if i not in used],
        "unmatched_reference": [i for i in range(len(reference)) if i not in {g for _, g in pairs}],
    }
