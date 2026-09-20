# Review-stage calibration

The September 20 calibration is complete; read the [decision and measured results](DECISION.md). It compares three continuations from the **same built candidate**: deliver immediately, let its builder self-check once, or obtain a fresh review followed by one correction. It does not compare complete skill versions.

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

## Evidence identities

The two September 20 pilot runners hashed transcript text before Windows converted its line endings when saving the file. Their append-only `transcript_sha256` fields therefore identify normalized UTF-8 text, not the saved file bytes. Each run's derived `evidence-index.json` verifies those original hashes and separately records the actual file-byte hashes, binding the index to the unchanged events file. Exact frozen runner snapshots preserve what executed. Subsequent controller code explicitly hashes saved bytes.

With the local private transcripts retained, regenerate the sidecar without model calls:

```text
python tools/paired_study/index_calibration_evidence.py --run research/program/calibration/runs/2026-09-20-pilot-02
```

`stage-summaries.jsonl` exports only final result messages, bound to the transcript byte hashes. These are the models' stated accounts; claims about their own checks are not independent grading. The saved candidate code and evaluator results provide the behavioral evidence. `supplementary-c002.json` records one independently derived boundary probe outside the frozen primary score; it must not be pooled into that score.

Further concrete findings from the final messages and patches are recorded separately in `supplementary-findings.json`, including a self-check regression. Reproduce these offline with `python research/program/calibration/supplementary_probes.py --run research/program/calibration/runs/2026-09-20-pilot-02`. These checks were selected after the run and cannot support an unbiased comparative-performance estimate.

## What changes in the existing evidence

The [measurement replay](../paired-study/measurement-replay.md) preserves every historical row and recomputes only fields supported by matching raw evidence. Its corrected derived rows are separate from the original results. The [dated study erratum](../paired-study/LOG.md#2026-09-20-correction-to-the-interpretation-of-the-september-19-results) explains the previously missed nonblocking revision; the research bar and gap analysis now distinguish uncertainty from demonstrated absence of benefit.

The production skill remains at 5.1.0. A successful apparatus check is not a release argument for adding orchestration rules.
