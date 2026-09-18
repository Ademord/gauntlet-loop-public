# Run records

A gauntlet run keeps its evidence next to its result. [runs.jsonl](runs.jsonl) holds one milestone line per run: difficulty estimate, verifiability, topology, reviews used, advisory-only reviews, outcome, wall clock, models, and tokens where the host reports them. Each run has its own folder:

| File | What it is |
| --- | --- |
| `contract.yaml` | The frozen outcome, reference, checks, difficulty, topology, and budget, written before building |
| `probes.md` | Scenario probes for judgment checks, when the run uses them |
| `events.jsonl` | Append-only events: builds, verdicts, revisions, acceptance, delivery |
| `state.yaml` | Derived current state: candidates, check statuses, budget, next action |
| `progress.md` | Human-readable timeline and review ledger |
| `evidence/` | Verdict records, validator outputs, candidate hashes |

## v5-upgrade-2026-09-17

The run that produced v5.0.0 by applying v4 to itself, with v4 as the bar: nine frozen checks, six scenario probes, and six independent critic reviews in three rounds. Start with [progress.md](v5-upgrade-2026-09-17/progress.md), then the [contract](v5-upgrade-2026-09-17/contract.yaml) and the verdicts in [evidence/](v5-upgrade-2026-09-17/evidence/R1-fidelity-verdict.md).

Paths inside this record refer to the repository layout of 17 September 2026. Since then `releases/v5/` and `provenance/v5/` became `dist/`, `docs/thesis/` became `research/thesis/`, and `research/scan-2026-09-17/` became `research/scans/2026-09-17/`. The record itself is left as written.

## Starting a new run record

Follow the execution contract in [skill/references/execution-contract.md](../skill/references/execution-contract.md): create `gauntlet/<run-id>/` with the files above and append the milestone line to `runs.jsonl` at the stopping milestone. Refer to another project by name only if it is public; the pre-commit guard blocks local paths and private terms.
