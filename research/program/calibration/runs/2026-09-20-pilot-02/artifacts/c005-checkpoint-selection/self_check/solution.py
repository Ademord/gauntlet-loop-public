"""Select one checkpoint per project and run."""

from datetime import datetime


def _valid_identity_part(value):
    return isinstance(value, str) and value.strip() != ""


def _parse_instant(value):
    if not isinstance(value, str):
        return None
    text = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        return None
    return parsed


def select_latest(records):
    chosen = {}
    for record in records:
        project = record.get("project")
        run_id = record.get("run_id")
        if not _valid_identity_part(project) or not _valid_identity_part(run_id):
            continue

        key = (project, run_id)
        instant = _parse_instant(record.get("updated_at"))

        if key not in chosen:
            chosen[key] = (record, instant)
            continue

        current_record, current_instant = chosen[key]
        keep_current = current_instant is not None and (
            instant is None or instant < current_instant
        )
        if not keep_current:
            chosen[key] = (record, instant)

    return [record for record, _ in chosen.values()]
