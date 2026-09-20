"""Routing follows explicit precedence, never the presence of any flag."""


def route_record(record):
    status = record.get("status", "ok")
    if status != "ok":
        return {"route": "failed", "reasons": [status]}
    if record.get("processable", True) is False or record.get("is_target_type") is False:
        return {"route": "skip", "reasons": []}
    if record.get("is_target_type") is not True:
        return {"route": "review", "reasons": ["UNCLASSIFIED"]}
    errors = []
    for flag in record.get("flags") or []:
        if flag.get("severity") == "ERROR":
            code = flag.get("code") or "UNKNOWN_ERROR"
            if code not in errors:
                errors.append(code)
    return {"route": "review" if errors else "auto", "reasons": errors}
