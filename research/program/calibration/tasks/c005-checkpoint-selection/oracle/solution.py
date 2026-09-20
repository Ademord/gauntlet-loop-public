"""Stable deduplication using timezone-aware checkpoint timestamps."""
from datetime import datetime


def _stamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
    except ValueError:
        return None


def select_latest(records):
    chosen = {}
    for record in records:
        project, run = record.get("project"), record.get("run_id")
        if not isinstance(project, str) or not project.strip() or not isinstance(run, str) or not run.strip():
            continue
        key = project, run
        stamp = _stamp(record.get("updated_at"))
        if key not in chosen:
            chosen[key] = stamp, record
            continue
        previous = chosen[key][0]
        if (stamp is None and previous is None) or (stamp is not None and (previous is None or stamp >= previous)):
            chosen[key] = stamp, record
    return [record for _, record in chosen.values()]
