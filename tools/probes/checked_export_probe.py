"""Offline caller integration probes; every subprocess is mocked.

Requires pypdf for real readable synthetic PDF fixtures. Run only after the
controller has recorded its PDF artifact-operation marker. No fixture is a
fresh renderer result or a visual qualification.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
QUALIFIED_GUARD_SHA = "06f13218db3e22d77e47d093184eca3ccc12d45255da54a92241e62421435ca9"
CASES = (
    "valid", "nonzero", "empty_stdout", "missing_artifact", "empty_artifact",
    "stale_input", "stale_output", "stale_options", "duplicate_matches",
    "invalid_pdf", "zero_page_pdf", "timeout", "existing_destination",
    "destination_race", "existing_evidence", "missing_evidence_arg",
    "missing_profile_arg", "unsupported_shots", "unsupported_append",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pdf_bytes(zero_pages=False):
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, DictionaryObject, DecodedStreamObject
    writer = PdfWriter()
    if not zero_pages:
        page = writer.add_blank_page(width=595.28, height=841.89)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        content = DecodedStreamObject()
        content.set_data(b"BT /F1 12 Tf 50 780 Td (Synthetic export verification) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(content)
    target = io.BytesIO()
    writer.write(target)
    return target.getvalue()


def form_data():
    return {"company": "Example Organisation", "title": "Synthetic role", "url": "https://example.invalid/form", "timestamp": "2030-01-02T12:00:00+00:00", "fields": [["Example field", "A & B < C"]], "attachments": [{"field": "CV", "name": "sample.pdf", "path": "/synthetic/sample.pdf", "pages": 1, "sha256_16": "0123456789abcdef"}], "notes": "Offline synthetic verification; no submission."}


def invoke(module, argv):
    stdout, stderr = io.StringIO(), io.StringIO()
    exception = None
    with patch.object(sys, "argv", ["make_form_doc.py", *argv]), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            value = module.main()
            exit_code = 0 if value is None else value
        except SystemExit as exc:
            exit_code = exc.code
        except Exception as exc:
            exception = type(exc).__name__
            exit_code = -999
    return exit_code, stdout.getvalue(), stderr.getvalue(), exception


def run_case(case, module, helper, good_pdf, empty_pdf):
    with tempfile.TemporaryDirectory(prefix="checked-export-probe-") as tmp:
        root = Path(tmp)
        form = root / "form.json"
        form.write_text(json.dumps(form_data()), encoding="utf-8")
        node = root / "offline-node.exe"
        node.write_bytes(b"never executed")
        package = root / "playwright"
        package.mkdir()
        (package / "package.json").write_text('{"name":"playwright"}', encoding="utf-8")
        profile = root / "profile.json"
        profile.write_text(json.dumps({"schema_version": 1, "node_executable": str(node.resolve()), "playwright_module": str(package.resolve()), "browser_channel": "msedge"}), encoding="utf-8")
        output, evidence = root / "published.pdf", root / "evidence"
        original = {p: p.read_bytes() for p in (form, profile, node, package / "package.json")}
        sentinel = b"prior delivered bytes"
        if case == "existing_destination":
            output.write_bytes(sentinel)
        if case == "existing_evidence":
            evidence.mkdir()
            (evidence / "sentinel").write_bytes(sentinel)
        args = [str(form), str(output), "--export-profile", str(profile), "--evidence-dir", str(evidence)]
        if case == "missing_evidence_arg":
            args = args[:-2]
        elif case == "missing_profile_arg":
            args = args[:2] + args[4:]
        elif case == "unsupported_shots":
            args += ["--shots", str(root / "shot.png")]
        elif case == "unsupported_append":
            args += ["--append-to", str(root / "other.pdf")]
        child_calls = []
        guard_calls = []
        wire = {}
        guard = helper.check_export_receipt

        def guard_spy(returncode, stdout, target, html_raw, options):
            guard_calls.append((returncode, stdout, Path(target), html_raw, copy.deepcopy(options)))
            return guard(returncode, stdout, target, html_raw, options)

        def child(command, **kwargs):
            child_calls.append((command, kwargs))
            request = json.loads(kwargs["input"].decode("utf-8"))
            target = Path(request["pdf_options"]["path"])
            raw = good_pdf
            if case == "invalid_pdf":
                raw = b"matching receipt does not turn arbitrary bytes into PDF"
            elif case == "zero_page_pdf":
                raw = empty_pdf
            elif case == "empty_artifact":
                raw = b""
            if case != "missing_artifact":
                target.write_bytes(raw)
            html_raw = request["html"].encode("utf-8")
            receipt = {"html_sha256": digest(html_raw), "html_utf8_bytes": len(html_raw), "pdf_sha256": digest(raw), "pdf_bytes": len(raw), "pdf_options_python": copy.deepcopy(request["pdf_options"])}
            if case == "stale_input":
                receipt["html_sha256"] = digest(b"old input")
            elif case == "stale_output":
                receipt["pdf_sha256"] = digest(b"old output")
            elif case == "stale_options":
                receipt["pdf_options_python"]["format"] = "Letter"
            stdout = json.dumps(receipt).encode("utf-8")
            if case == "empty_stdout":
                stdout = b""
            elif case == "duplicate_matches":
                stdout += b"\n" + stdout
            stderr = b"synthetic child diagnostic"
            code = 7 if case == "nonzero" else 0
            wire.update(stdout=stdout, stderr=stderr, returncode=code, target=target, html=html_raw, options=request["pdf_options"], request=request)
            if case == "destination_race":
                output.write_bytes(sentinel)
            if case == "timeout":
                wire.update(stdout=b"partial stdout", stderr=b"partial stderr")
                raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=wire["stdout"], stderr=wire["stderr"])
            return subprocess.CompletedProcess(command, code, stdout, stderr)

        with patch.object(helper.subprocess, "run", side_effect=child), patch.object(helper, "check_export_receipt", side_effect=guard_spy), patch.object(subprocess, "Popen", side_effect=AssertionError("Unexpected real process")):
            exit_code, printed, error_text, exception = invoke(module, args)
        failures = []
        if any(p.read_bytes() != raw for p, raw in original.items()):
            failures.append("source_changed")
        preflight = case in {"existing_destination", "existing_evidence", "missing_evidence_arg", "missing_profile_arg", "unsupported_shots", "unsupported_append"}
        if preflight and child_calls:
            failures.append("child_called_after_preflight_rejection")
        if not preflight and len(child_calls) != 1:
            failures.append("expected_exactly_one_mocked_child")
        if case == "valid":
            if exit_code != 0 or not output.is_file() or output.read_bytes() != good_pdf:
                failures.append("valid_output_not_published_exactly")
            result = json.loads((evidence / "result.json").read_text(encoding="utf-8")) if (evidence / "result.json").is_file() else {}
            if result.get("status") != "published_pending_visual_review" or result.get("visual_review") != "pending" or result.get("receipt_checked") is not True:
                failures.append("success_claim_boundary")
            if not guard_calls or guard_calls[-1] != (wire["returncode"], wire["stdout"], wire["target"], wire["html"], wire["options"]):
                failures.append("qualified_guard_not_given_actual_inputs")
        else:
            if exit_code == 0:
                failures.append("failure_exit_zero")
            if case in {"existing_destination", "destination_race"}:
                if not output.is_file() or output.read_bytes() != sentinel:
                    failures.append("prior_output_not_preserved")
            elif output.exists():
                failures.append("failed_artifact_promoted")
            if case == "existing_evidence" and (evidence / "sentinel").read_bytes() != sentinel:
                failures.append("prior_evidence_changed")
        if child_calls:
            result_path = evidence / "result.json"
            if not result_path.is_file():
                failures.append("missing_result_receipt")
            elif case != "valid" and json.loads(result_path.read_text(encoding="utf-8")).get("status") != "failed_preserved":
                failures.append("missing_failed_preserved_status")
            for filename, key in [("stdout.bin", "stdout"), ("stderr.bin", "stderr")]:
                path = evidence / filename
                if not path.is_file() or path.read_bytes() != wire[key]:
                    failures.append("raw_" + key + "_not_preserved")
            command, kwargs = child_calls[0]
            if not isinstance(command, list) or Path(command[0]) != node or Path(command[1]).name != "offline_export.cjs" or kwargs.get("shell", False) or not 0 < kwargs.get("timeout", 0) <= 600:
                failures.append("unexpected_process_boundary")
        return {"case": case, "passed": not failures, "failures": failures, "child_calls": len(child_calls), "guard_calls": len(guard_calls), "exit_code": exit_code, "exception_class": exception}, {"case": case, "stdout": printed, "stderr": error_text}


def compatibility(module, baseline):
    checks = []
    original = form_data()
    for attachments in [original["attachments"], [["Legacy", "old.pdf"]], []]:
        form = {**original, "attachments": attachments}
        for kind in ["form", "confirmation"]:
            for shots in [False, True]:
                checks.append(module.build_html(form, kind, shots) == baseline.build_html(form, kind, shots))
    for invalid in [None, [3], [{"field": "CV"}], [["CV", ""]], [{**original["attachments"][0], "pages": True}]]:
        results = []
        for owner in [module, baseline]:
            try:
                owner.normalize_attachments(invalid)
                results.append("accepted")
            except Exception as exc:
                results.append(type(exc).__name__)
        checks.append(results[0] == results[1] and results[0] != "accepted")
    return {"case": "default_html_attachment_compatibility", "passed": all(checks), "comparisons": len(checks)}


def legacy_route(module, good_pdf):
    with tempfile.TemporaryDirectory(prefix="legacy-export-probe-") as temp:
        root = Path(temp)
        form, output = root / "form.json", root / "output.pdf"
        form.write_text(json.dumps(form_data()), encoding="utf-8")
        calls = []

        async def render(doc, target):
            calls.append("render_html")
            Path(target).write_bytes(good_pdf)

        def process(command, **kwargs):
            calls.append(command[0])
            if command[0] == "pdfunite":
                Path(command[-1]).write_bytes(good_pdf)
                return subprocess.CompletedProcess(command, 0)
            if command[0] == "pdfinfo":
                return subprocess.CompletedProcess(command, 0, "Pages: 1\n", "")
            raise AssertionError("Unexpected legacy command")

        with patch.object(module, "render_html", side_effect=render), patch.object(module.subprocess, "run", side_effect=process), patch.object(module.tempfile, "mkdtemp", return_value=str(root)), patch.object(subprocess, "Popen", side_effect=AssertionError("Unexpected real process")):
            code, _out, _err, exception = invoke(module, [str(form), str(output)])
        return {"case": "default_legacy_route", "passed": code == 0 and calls == ["render_html", "pdfunite", "pdfinfo"] and output.read_bytes() == good_pdf, "calls": calls, "exception_class": exception}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True, help="Candidate make_form_doc.py")
    parser.add_argument("--baseline", type=Path, required=True, help="Unmodified baseline make_form_doc.py")
    parser.add_argument("--pdf-marker-confirmed", action="store_true", required=True)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--private-log", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.candidate.resolve().parent))
    baseline = load_module(args.baseline, "baseline_form_document")
    module = load_module(args.candidate, "candidate_form_document")
    import checked_export as helper
    guard_path = args.candidate.parent / "export_receipt.py"
    assert digest(guard_path.read_bytes()) == QUALIFIED_GUARD_SHA, "Qualified guard bytes changed"
    good, empty = pdf_bytes(), pdf_bytes(zero_pages=True)
    rows, private = [], []
    for case in CASES:
        row, detail = run_case(case, module, helper, good, empty)
        rows.append(row)
        private.append(detail)
    rows += [compatibility(module, baseline), legacy_route(module, good)]
    result = {"schema_version": 1, "kind": "offline_real_export_caller_qualification", "accepted": all(r["passed"] for r in rows), "passed": sum(r["passed"] for r in rows), "total": len(rows), "cases": rows, "hashes": {"candidate": digest(args.candidate.read_bytes()), "helper": digest((args.candidate.parent / "checked_export.py").read_bytes()), "qualified_guard": digest(guard_path.read_bytes()), "probe": digest(Path(__file__).read_bytes()), "baseline": digest(args.baseline.read_bytes())}, "scope": "Every subprocess mocked; actual readable synthetic PDF bytes exercise the real caller's parsing/readback/publication path. No fresh Node/browser render, external call, model call or visual qualification."}
    text = json.dumps(result, indent=2) + "\n"
    if args.result:
        args.result.write_text(text, encoding="utf-8")
    if args.private_log:
        args.private_log.write_text(json.dumps(private, indent=2) + "\n", encoding="utf-8")
    print(text, end="")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
