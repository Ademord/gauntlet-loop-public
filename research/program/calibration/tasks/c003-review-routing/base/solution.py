"""Select the next processing route for an extracted document."""


def route_record(record):
    flags = record.get("flags") or []
    if flags:
        return {"route": "review", "reasons": [flag.get("code", "UNKNOWN_ERROR") for flag in flags]}
    if not record.get("processable", True):
        return {"route": "skip", "reasons": []}
    return {"route": "auto", "reasons": []}
