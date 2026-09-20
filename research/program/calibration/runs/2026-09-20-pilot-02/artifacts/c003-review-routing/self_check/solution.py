"""Select the next processing route for an extracted document."""


def route_record(record):
    status = record.get("status", "ok")
    if status != "ok":
        return {"route": "failed", "reasons": [status]}

    processable = record.get("processable", True)
    if processable is False:
        return {"route": "skip", "reasons": []}

    is_target_type = record.get("is_target_type")
    if is_target_type is False:
        return {"route": "skip", "reasons": []}
    if is_target_type is None:
        return {"route": "review", "reasons": ["UNCLASSIFIED"]}

    flags = record.get("flags") or []
    error_codes = []
    seen = set()
    for flag in flags:
        if flag.get("severity") != "ERROR":
            continue
        code = flag.get("code") or "UNKNOWN_ERROR"
        if code not in seen:
            seen.add(code)
            error_codes.append(code)

    if error_codes:
        return {"route": "review", "reasons": error_codes}
    return {"route": "auto", "reasons": []}
