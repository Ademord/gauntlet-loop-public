# Review-stage calibration

This is the next experiment after the historical F1 study's measurement audit. It compares three continuations from the **same built candidate**: deliver immediately, let its builder self-check once, or obtain a fresh review followed by one correction. It does not compare complete skill versions.

Read the [frozen protocol](PROTOCOL.md) and [fixture limitations](tasks/README.md). The six original stress fixtures validate the apparatus. They are not a representative repository benchmark and cannot establish a general performance improvement.

The controller owns the stages instead of asking a lead to self-report how many reviews occurred. All hidden grading happens after the branches are saved. Fresh reviewer context contains public requirements and candidate code, not the builder's conversation. Self-check and correction fork the original builder session; neither inherits the other's changes. Actual CLI session counters include parent usage, so the controller subtracts the parent when charging each fork.

## Reproduce

From the repository root, with Python 3.10+ and the authenticated Claude CLI available:

```text
python -m unittest discover -s tests -v
python research/program/calibration/tasks/validate_fixtures.py
python tools/paired_study/run_calibration.py --prepare --run research/program/calibration/runs/my-pilot
python tools/paired_study/run_calibration.py --execute --run research/program/calibration/runs/my-pilot
```

Only `--execute` spends model usage. It is an explicit choice to run the documented $15 pilot; preparation never dispatches. The previous backend diagnostic cost can be included via `--diagnostic-cost`. This pilot fixes the recorded model to `claude-sonnet-5` by default; a different model is a separate experiment and must be recorded at preparation. No automatic model fallback is configured.

The prepared manifest freezes the runner, telemetry, protocol and all task files. A changed input refuses execution. An existing execution marker refuses a second execution, even after a stop; diagnose the stopped attempt and create a separately recorded run rather than silently spending again. Raw prompts/transcripts stay in gitignored `private/`; public results contain relative identities, grades and reconciled usage. Generated code remains inspectable in `artifacts/`.

`REPORT.md` separates functional outcomes from scope compliance. It reports actual stage cost, rescues and spoils relative to the shared build, and incomplete work. An unresolved paid call makes total spend unknown and the observed amount a lower bound. CLI limits are checked at request boundaries, so they are not a promise of an exact external billing cutoff.

Cost figures mean CLI-reported API-equivalent usage, not an independently verified subscription charge or invoice.

## What changes in the existing evidence

The [measurement replay](../paired-study/measurement-replay.md) preserves every historical row and recomputes only fields supported by matching raw evidence. Its corrected derived rows are separate from the original results. The [dated study erratum](../paired-study/LOG.md#2026-09-20-correction-to-the-interpretation-of-the-september-19-results) explains the previously missed nonblocking revision; the research bar and gap analysis now distinguish uncertainty from demonstrated absence of benefit.

The production skill remains at 5.1.0. A successful apparatus check is not a release argument for adding orchestration rules.
