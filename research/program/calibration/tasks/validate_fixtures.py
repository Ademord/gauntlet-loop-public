"""Offline calibration-fixture checks; never dispatch an agent or call a model.

Each frozen base must pass its visible tests and fail at least one hidden test.
The known-good implementation must pass both. This validates the apparatus,
not the independence/completeness of the oracle or the difficulty for a model.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def suite(candidate, test_dir):
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", test_dir, "-v"],
        cwd=candidate, capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = completed.stdout + completed.stderr
    output = output.replace(str(candidate), "<candidate>").replace(candidate.as_posix(), "<candidate>")
    return {"returncode": completed.returncode, "output": output}


def validate(task_dir):
    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    expected = task["frozen_sha256"]
    actual = {
        path.relative_to(task_dir).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for prefix in ("base", "heldout", "oracle")
        for path in sorted((task_dir / prefix).rglob("*")) if path.is_file()
    }
    if actual != expected:
        raise AssertionError(f"frozen inputs changed: {task['id']}")
    with tempfile.TemporaryDirectory(prefix="gauntlet-calibration-") as scratch:
        candidate = Path(scratch) / "candidate"
        shutil.copytree(task_dir / "base", candidate)
        shutil.copytree(task_dir / "heldout", candidate / "heldout")
        base_visible = suite(candidate, "tests")
        base_hidden = suite(candidate, "heldout")
        for source in (task_dir / "oracle").rglob("*"):
            if source.is_file():
                target = candidate / source.relative_to(task_dir / "oracle")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        oracle_visible = suite(candidate, "tests")
        oracle_hidden = suite(candidate, "heldout")
    checks = {
        "base_visible_passes": base_visible["returncode"] == 0,
        "base_hidden_rejects": base_hidden["returncode"] != 0,
        "oracle_visible_passes": oracle_visible["returncode"] == 0,
        "oracle_hidden_passes": oracle_hidden["returncode"] == 0,
    }
    result = {"task_id": task["id"], "checks": checks, "passed": all(checks.values()),
              "outputs": {"base_visible": base_visible, "base_hidden": base_hidden,
                          "oracle_visible": oracle_visible, "oracle_hidden": oracle_hidden}}
    return result


def main():
    results = [validate(path.parent) for path in sorted(ROOT.glob("c*/task.json"))]
    if len(results) != 6:
        raise AssertionError(f"expected six fixtures, found {len(results)}")
    print(json.dumps({"model_calls": 0, "tasks": results}, indent=2))
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
