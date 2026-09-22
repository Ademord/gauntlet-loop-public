"""Offline contract probes for a byte-bound export receipt checker.

Usage: python -B probe_export_receipt.py --candidate /path/to/export_receipt.py
Optional --reference-source extracts only the reviewed parser/digest functions
from an existing controller, adding its observed nonzero-exit check. It never
imports or invokes the controller's main routine or renderer.

Synthetic bytes intentionally are not a PDF qualification fixture. A matching
receipt does not establish fresh execution, valid PDF syntax, or visual quality.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import sys

sys.dont_write_bytecode = True

HTML = b"<p>Offline input: \xc3\xbc</p>"
OUTPUT = b"%PDF-1.4\nopaque offline fixture\n%%EOF\n"
FIELDS = ("html_sha256", "html_utf8_bytes", "pdf_sha256", "pdf_bytes", "pdf_options_python")
VALID_CASES = (
    "clean_compact", "clean_pretty", "bom_whitespace", "mixed_plain_logs",
    "mixed_json_logs", "one_stale_one_current", "extra_metadata", "empty_input",
)
NEGATIVE_CASES = (
    "positive_nonzero", "negative_exit", "empty_stdout", "whitespace_stdout",
    "logs_only", "malformed_json", "invalid_utf8", "json_scalar", "json_array",
    "missing_artifact", "directory_artifact", "empty_artifact", "stale_input",
    "wrong_input_count", "stale_output", "wrong_output_count", "stale_options",
    "missing_field", "duplicate_matches", "duplicate_matches_with_logs",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def receipt_for(html, output, options):
    return {
        "html_sha256": sha(html), "html_utf8_bytes": len(html),
        "pdf_sha256": sha(output), "pdf_bytes": len(output),
        "pdf_options_python": copy.deepcopy(options),
    }


def encoded(value, **kwargs):
    return json.dumps(value, ensure_ascii=False, **kwargs).encode("utf-8")


def fixture(case, root):
    target = root / "export.pdf"
    html = b"" if case == "empty_input" else HTML
    output = b"" if case == "empty_artifact" else OUTPUT
    if case == "directory_artifact":
        target.mkdir()
    elif case != "missing_artifact":
        target.write_bytes(output)
    source = root / "source.html"
    source.write_bytes(html)
    options = {"path": str(target), "format": "A4", "margin": {"top": "12mm"}, "printBackground": True}
    current = receipt_for(html, output, options)
    changed = copy.deepcopy(current)
    code = 0
    stdout = encoded(current)
    if case == "clean_pretty":
        stdout = encoded(current, indent=2)
    elif case == "bom_whitespace":
        stdout = b"\xef\xbb\xbf \n" + encoded(current, indent=2) + b"\n\t"
    elif case == "mixed_plain_logs":
        stdout = b"Starting local export\n" + encoded(current) + b"\nFinished\n"
    elif case == "mixed_json_logs":
        stdout = b'{"event":"starting"}\n' + encoded(current) + b'\n["finished"]\n'
    elif case == "one_stale_one_current":
        changed["html_sha256"] = sha(b"older input")
        stdout = encoded(changed) + b"\n" + encoded(current)
    elif case == "extra_metadata":
        current["engine"] = "synthetic-offline"
        stdout = encoded(current)
    elif case == "positive_nonzero":
        code = 7
    elif case == "negative_exit":
        code = -9
    elif case == "empty_stdout":
        stdout = b""
    elif case == "whitespace_stdout":
        stdout = b" \n\t"
    elif case == "logs_only":
        stdout = b"Export completed successfully\n"
    elif case == "malformed_json":
        stdout = b'{"html_sha256":'
    elif case == "invalid_utf8":
        stdout = b"\xff" + encoded(current)
    elif case == "json_scalar":
        stdout = b'"success"'
    elif case == "json_array":
        stdout = encoded([current])
    elif case == "stale_input":
        changed["html_sha256"] = sha(b"older input")
        stdout = encoded(changed)
    elif case == "wrong_input_count":
        changed["html_utf8_bytes"] += 1
        stdout = encoded(changed)
    elif case == "stale_output":
        changed["pdf_sha256"] = sha(b"older output")
        stdout = encoded(changed)
    elif case == "wrong_output_count":
        changed["pdf_bytes"] += 1
        stdout = encoded(changed)
    elif case == "stale_options":
        changed["pdf_options_python"]["margin"]["top"] = "13mm"
        stdout = encoded(changed)
    elif case == "missing_field":
        changed.pop("pdf_options_python")
        stdout = encoded(changed)
    elif case == "duplicate_matches":
        stdout = encoded(current) + b"\n" + encoded(current)
    elif case == "duplicate_matches_with_logs":
        stdout = b"start\n" + encoded(current) + b"\nnext\n" + encoded(current) + b"\ndone"
    return code, stdout, target, html, options, current, source


def candidate_function(path):
    spec = importlib.util.spec_from_file_location("qualified_export_candidate", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.check_export_receipt


def reference_function(path):
    # Extract only the two reviewed pure/helper definitions. No module import.
    tree = ast.parse(path.read_text(encoding="utf-8"), filename="reviewed_reference")
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"digest", "render_receipt_from_stdout"}]
    if {n.name for n in nodes} != {"digest", "render_receipt_from_stdout"}:
        raise ValueError("Reference source lacks the reviewed helper interface")
    namespace = {"hashlib": hashlib, "json": json}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "reviewed_reference", "exec"), namespace)
    parser = namespace["render_receipt_from_stdout"]

    def checked(returncode, stdout, target, html_raw, options):
        if returncode:
            raise ValueError("Reference caller rejected nonzero exit")
        receipt, _output_bytes = parser(stdout, target, html_raw, options)
        return receipt

    return checked


def run_cases(check, private_records):
    results = []
    for case in VALID_CASES + NEGATIVE_CASES:
        with tempfile.TemporaryDirectory(prefix="export-receipt-probe-") as temp:
            args = fixture(case, Path(temp))
            code, stdout, target, html, options, expected, source = args
            original_options = copy.deepcopy(options)
            original_source = source.read_bytes()
            original_output = target.read_bytes() if target.is_file() else None
            error = None
            value = None
            try:
                value = check(code, stdout, target, html, options)
            except Exception as exc:
                error = exc
            expected_accept = case in VALID_CASES
            returned_expected = isinstance(value, dict) and value == expected
            source_unchanged = source.exists() and source.read_bytes() == original_source
            output_unchanged = (target.is_file() and target.read_bytes() == original_output) if original_output is not None else not target.is_file()
            options_unchanged = options == original_options
            outcome_pass = (error is None and returned_expected) if expected_accept else error is not None
            passed = outcome_pass and source_unchanged and output_unchanged and options_unchanged
            public = {"case": case, "expected": "accept" if expected_accept else "reject", "observed": "rejected" if error else "returned", "passed": passed, "source_unchanged": source_unchanged, "output_unchanged": output_unchanged, "options_unchanged": options_unchanged}
            if error:
                public["exception_class"] = type(error).__name__
            if expected_accept and not error:
                public["returned_matching_receipt"] = returned_expected
            results.append(public)
            private_records.append({**public, "exception_detail": str(error) if error else None})
    return results


def counts(rows):
    return {group: {"passed": sum(r["passed"] for r in rows if r["expected"] == expected), "total": sum(r["expected"] == expected for r in rows)} for group, expected in [("valid", "accept"), ("known_negative", "reject")]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--reference-source", type=Path)
    parser.add_argument("--result", type=Path, help="Optional sanitized JSON output file")
    parser.add_argument("--private-log", type=Path, help="Optional private exception details; never publish this file")
    args = parser.parse_args()
    candidate_hash = sha(args.candidate.read_bytes())
    details = {"candidate": [], "reference": []}
    rows = run_cases(candidate_function(args.candidate), details["candidate"])
    source_unchanged = sha(args.candidate.read_bytes()) == candidate_hash
    result = {"schema_version": 1, "kind": "offline_export_receipt_qualification", "candidate_sha256": candidate_hash, "probe_sha256": sha(Path(__file__).read_bytes()), "candidate_source_unchanged": source_unchanged, "accepted": all(r["passed"] for r in rows) and source_unchanged, "counts": counts(rows), "cases": rows, "scope": "Synthetic process-result/receipt/current-byte-and-options validation only; no renderer, browser, model, external service, PDF syntax/readability/visual assessment, freshness proof, or performance comparison."}
    if args.reference_source:
        ref_hash = sha(args.reference_source.read_bytes())
        ref_rows = run_cases(reference_function(args.reference_source), details["reference"])
        valid_preserved = all(r["passed"] for r in rows if r["expected"] == "accept") and all(r["passed"] for r in ref_rows if r["expected"] == "accept")
        result["reference"] = {"source_sha256": ref_hash, "source_unchanged": sha(args.reference_source.read_bytes()) == ref_hash, "counts_against_contract": counts(ref_rows), "existing_valid_semantics_preserved": valid_preserved, "cases": ref_rows, "scope": "Existing parser plus its real caller nonzero-exit guard. Differences identify bounded contract coverage, not general superiority."}
        result["accepted"] = result["accepted"] and valid_preserved and result["reference"]["source_unchanged"]
    serialized = json.dumps(result, indent=2) + "\n"
    if args.result:
        args.result.write_text(serialized, encoding="utf-8")
    if args.private_log:
        args.private_log.write_text(json.dumps(details, indent=2) + "\n", encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
