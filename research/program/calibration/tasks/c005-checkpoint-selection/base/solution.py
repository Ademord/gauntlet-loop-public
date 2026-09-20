"""Select one checkpoint per project and run."""


def select_latest(records):
    chosen = {}
    for record in records:
        key = record["run_id"]
        if key not in chosen or record.get("updated_at", "") >= chosen[key].get("updated_at", ""):
            chosen[key] = record
    return list(chosen.values())
