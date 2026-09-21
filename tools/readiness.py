"""Read-only post-task gap triage. Standard library; no execution or promotion."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path("research/program/readiness")
CATALOG = Path("research/program/MILESTONES-50.json")
CLASSIFICATIONS = {"missing_capability", "native_configuration", "implementation_defect",
                   "evaluator_gap", "unknown", "existing_capability"}
DISPOSITIONS = {"fix", "reuse", "defer", "investigate"}
CAUSE_STATES = {"established", "hypothesis", "unknown"}
QUALIFICATION_METHODS = {"offline", "native_no_model", "manual"}
IDENTIFIER = re.compile(r"[A-Z][A-Z0-9-]{0,63}")


def read_json(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"Duplicate JSON key: {key}")
            value[key] = item
        return value

    def invalid(value):
        raise ValueError(f"Non-finite JSON number: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=invalid)


def concrete(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in {
        "todo", "tbd", "unknown", "n/a"}


def number(value):
    return type(value) in {int, float} and math.isfinite(value) and value >= 0


def string_list(value, *, nonempty=True):
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(concrete(item) for item in value))


def catalog(root):
    data = read_json(Path(root) / CATALOG)
    rows = data.get("milestones") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("Catalog requires milestone records")
    result = {}
    for row in rows:
        if (not isinstance(row, dict) or not re.fullmatch(r"M-\d{3,}", str(row.get("claim_id", "")))
                or not concrete(row.get("milestone"))):
            raise ValueError("Invalid milestone identity/title in catalog")
        if row["claim_id"] in result:
            raise ValueError("Duplicate milestone identity in catalog")
        result[row["claim_id"]] = row["milestone"]
    return result


def record_errors(record, milestones):
    """Check structural claims only; referenced observations still need review."""
    errors = []
    if not isinstance(record, dict):
        return ["Triage record must be an object"]
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        errors.append("Unsupported schema_version")
    if not isinstance(record.get("id"), str) or not IDENTIFIER.fullmatch(record["id"]):
        errors.append("Invalid triage ID")
    if record.get("mode") != "engineering_readiness":
        errors.append("Mode must be engineering_readiness")
    if record.get("performance_evidence") != "unproven":
        errors.append("Readiness does not establish performance evidence")
    if record.get("milestone_status_changes") != []:
        errors.append("Triage must not promote or change milestone statuses")
    if record.get("paid_execution_authorized") is not False:
        errors.append("Readiness record cannot authorize paid execution")
    if not string_list(record.get("limitations")):
        errors.append("Explicit limitations required")

    source = record.get("source_task")
    if not isinstance(source, dict):
        errors.append("source_task must be an object")
        source = {}
    for field in ("id", "evidence_reference", "scope", "deployment"):
        if not concrete(source.get(field)):
            errors.append(f"source_task requires {field}")
    if source.get("outcome") not in {"passed", "failed", "blocked", "not_assessed"}:
        errors.append("source_task requires an observed outcome")
    for field in ("full_research_cost_usd", "human_minutes"):
        if field not in source or (source[field] is not None and not number(source[field])):
            errors.append(f"source_task {field} must be nonnegative or null for unknown")
    if type(source.get("controller_corrections")) is not int or source["controller_corrections"] < 0:
        errors.append("source_task requires nonnegative controller_corrections")
    attempts = source.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        errors.append("source_task requires every started attempt")
        attempts = []
    valid_costs = []
    for index, attempt in enumerate(attempts, 1):
        prefix = f"attempt {index}"
        if not isinstance(attempt, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if type(attempt.get("number")) is not int or attempt["number"] != index:
            errors.append("Attempt numbers must be consecutive from one")
        if not concrete(attempt.get("evidence_reference")) or not concrete(attempt.get("terminal_reason")):
            errors.append(f"{prefix} requires evidence and terminal reason")
        if attempt.get("acceptance") not in {"passed", "failed", "blocked", "not_assessed"}:
            errors.append(f"{prefix} requires independent acceptance status")
        cost = attempt.get("worker_api_equivalent_usd")
        if "worker_api_equivalent_usd" not in attempt or (cost is not None and not number(cost)):
            errors.append(f"{prefix} cost must be nonnegative or null for unknown")
        valid_costs.append(cost)
        if not number(attempt.get("worker_elapsed_seconds")):
            errors.append(f"{prefix} requires nonnegative observed elapsed seconds")
        checks = attempt.get("mechanical_checks")
        if (not isinstance(checks, dict) or type(checks.get("passed")) is not int
                or type(checks.get("total")) is not int
                or not 0 <= checks["passed"] <= checks["total"]):
            errors.append(f"{prefix} has invalid mechanical check counts")
    total = source.get("worker_api_equivalent_usd")
    if "worker_api_equivalent_usd" not in source or (total is not None and not number(total)):
        errors.append("source_task total cost must be nonnegative or null for unknown")
    if attempts and len(valid_costs) == len(attempts) and all(number(cost) for cost in valid_costs):
        if not number(total) or not math.isclose(sum(valid_costs), total, rel_tol=1e-9, abs_tol=1e-8):
            errors.append("Total worker cost must include all recorded attempts")
    elif total is not None:
        errors.append("Total worker cost must stay unknown when any attempt cost is unknown")

    review = record.get("milestone_review")
    if not isinstance(review, dict):
        errors.append("milestone_review must be an object")
        review = {}
    reviewed = review.get("reviewed_ids")
    if (not string_list(reviewed) or len(set(reviewed)) != len(reviewed)
            or set(reviewed) != set(milestones)):
        errors.append("reviewed_ids must cover every current milestone exactly once")
    if not concrete(review.get("unselected_reason")):
        errors.append("Explain why other milestone mechanisms are not selected")

    gaps = record.get("gaps")
    if not isinstance(gaps, list) or not gaps:
        errors.append("At least one evidence-linked gap or reuse decision required")
        gaps = []
    gap_ids = set()
    for index, gap in enumerate(gaps, 1):
        prefix = f"gap {index}"
        if not isinstance(gap, dict):
            errors.append(f"{prefix} must be an object")
            continue
        identity = gap.get("id")
        if not isinstance(identity, str) or not IDENTIFIER.fullmatch(identity) or identity in gap_ids:
            errors.append(f"{prefix} requires a unique valid ID")
        else:
            gap_ids.add(identity)
        for field in ("observation", "evidence_reference", "cause_assessment", "existing_capability",
                      "smallest_action", "decision_reason"):
            if not concrete(gap.get(field)):
                errors.append(f"{prefix} requires {field}")
        if gap.get("classification") not in CLASSIFICATIONS:
            errors.append(f"{prefix} has invalid classification")
        if gap.get("cause_status") not in CAUSE_STATES:
            errors.append(f"{prefix} has invalid cause_status")
        if not string_list(gap.get("alternative_explanations")):
            errors.append(f"{prefix} requires alternative explanations or explicit causal limits")
        if gap.get("disposition") not in DISPOSITIONS:
            errors.append(f"{prefix} has invalid disposition")
        ids = gap.get("milestone_ids")
        if (not string_list(ids) or len(set(ids)) != len(ids)
                or any(identity not in milestones for identity in ids)):
            errors.append(f"{prefix} must reference existing distinct milestone IDs")
        check = gap.get("qualification")
        if not isinstance(check, dict):
            errors.append(f"{prefix} requires qualification record")
            continue
        if check.get("method") not in QUALIFICATION_METHODS:
            errors.append(f"{prefix} qualification must be offline, native_no_model or manual")
        for field in ("procedure", "pass_condition", "failure_condition"):
            if not concrete(check.get(field)):
                errors.append(f"{prefix} qualification requires {field}")
        if check.get("status") not in {"not_run", "passed", "failed", "blocked"}:
            errors.append(f"{prefix} has invalid qualification status")
        refs = check.get("evidence_references")
        if not string_list(refs, nonempty=False):
            errors.append(f"{prefix} qualification requires an evidence reference list")
        elif check.get("status") != "not_run" and not refs:
            errors.append(f"{prefix} observed qualification requires evidence")
        elif check.get("status") == "not_run" and refs:
            errors.append(f"{prefix} not_run qualification cannot carry result evidence")
    next_gap = record.get("next_gap_id")
    if not isinstance(next_gap, str) or next_gap not in gap_ids:
        errors.append("next_gap_id must select a recorded gap")
    elif not any(gap.get("id") == next_gap and gap.get("disposition") in {"fix", "investigate"}
                 for gap in gaps if isinstance(gap, dict)):
        errors.append("next_gap_id must select a fix or investigation")
    return errors


def validate(root=ROOT):
    errors, records = [], []
    try:
        milestones = catalog(root)
    except (OSError, ValueError, TypeError) as exc:
        return {"errors": [f"Cannot read milestone catalog: {exc}"], "records": []}, {}
    identities = set()
    for path in sorted((Path(root) / DIRECTORY).glob("*-triage.json")):
        try:
            record = read_json(path)
            failures = record_errors(record, milestones)
            errors.extend(f"{path.name}: {error}" for error in failures)
            if failures:
                continue
            if record["id"] in identities:
                errors.append(f"{path.name}: duplicate triage ID {record['id']}")
                continue
            identities.add(record["id"])
            records.append(record)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"{path.name}: cannot read triage: {exc}")
    if not records and not errors:
        errors.append("No triage records found")
    return {"errors": errors, "records": records}, milestones


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("list")
    show = commands.add_parser("show")
    show.add_argument("triage_id")
    args = parser.parse_args(argv)
    report, milestones = validate(args.root)
    if report["errors"]:
        print(json.dumps({"errors": report["errors"]}, indent=2))
        return 1
    if args.command == "validate":
        result = {"errors": [], "triage_records": len(report["records"]),
                  "catalog_milestones": len(milestones), "mode": "engineering_readiness",
                  "limit": "Structure checked; no execution, factual certification or milestone promotion."}
    elif args.command == "list":
        result = [{"id": row["id"], "source_outcome": row["source_task"]["outcome"],
                   "gaps": len(row["gaps"]), "next_gap_id": row["next_gap_id"],
                   "next_action": next(gap["smallest_action"] for gap in row["gaps"]
                                       if gap["id"] == row["next_gap_id"])} for row in report["records"]]
    else:
        result = next((row for row in report["records"] if row["id"] == args.triage_id), None)
        if result is None:
            print(json.dumps({"errors": [f"Unknown triage ID: {args.triage_id}"]}))
            return 1
        result = dict(result, milestone_titles={identity: milestones[identity]
                      for gap in result["gaps"] for identity in gap["milestone_ids"]})
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
