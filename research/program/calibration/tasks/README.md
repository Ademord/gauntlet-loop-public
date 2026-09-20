# Calibration fixtures

These six **constructed stress fixtures** check the experiment's apparatus. They are not six historical bugs, a representative sample of engineering work, or evidence that a workflow improves performance. All implementation and test code was written for this calibration; no third-party repository source was copied. The repository's CC BY 4.0 research license applies.

The first three exercise document-processing concerns; the next two exercise run-ledger concerns; the last exercises task coordination. Local source inspection informed the contexts, as each task's provenance states. The tasks deliberately specify several interacting requirements rather than seeding only one-token mutations.

| Task | Behavior | Hidden tests |
| --- | --- | --- |
| c001-number-parser | Locale grammar, finite values, boolean exclusion | 8 |
| c002-item-matching | One-to-one cardinality, name preference, decimal rounding, duplicates | 8 |
| c003-review-routing | Failure/skip/review precedence, severity and reason aggregation | 7 |
| c004-duration-parser | Whole-string grammars, unit ordering, fractional seconds | 7 |
| c005-checkpoint-selection | Compound identity, timezone comparison, invalid timestamps, stable order | 8 |
| c006-ready-scheduler | DAG validation, capacity, resource ownership, stable priorities | 9 |

Each task has two visible test methods. Every initial base passes the visible suite and fails the hidden suite. Every reference implementation passes both suites. This establishes that the supplied tests discriminate between these particular known-bad and known-good implementations. It does not establish that all plausible bad implementations are rejected or that a model will struggle with these tasks.

## Inputs and isolation

- `task.json` contains the full public behavior contract and hashes of all files in `base/`, `heldout/` and `oracle/`. Freeze the manifest identity in the experiment record before any model run.
- `base/` contains `solution.py` and `tests/test_visible.py`; copy **only this directory's contents** into a solver's isolated workspace. Give the solver the description, requirements and allowed path from the manifest.
- `heldout/test_hidden.py` is evaluator-only. Copy the candidate to a separate evaluator workspace, install this directory as `heldout/`, then run its command. Never add hidden checks to the solver's workspace or feedback during this calibration.
- `oracle/solution.py` is a known-good implementation for apparatus validation only. It must never reach builders or critics. Alternative implementations can pass; equality to the oracle source is not an acceptance condition.

Hidden tests were written before solving runs and do not inspect the candidate's implementation. They were written by the same authoring agent as these fixtures and reference implementations, so they are **not** an independently authored assessment. Their limited examples can miss defects. All requirements tested in the hidden suite are stated in the public task contract.

The commands use only Python's standard library:

```text
python -m unittest discover -s tests -v
python -m unittest discover -s heldout -v
```

`python validate_fixtures.py` checks hashes, copies fixtures into temporary workspaces, and runs the four base/oracle × visible/hidden checks for each task. It makes no model calls. `fixture-validation.json` records the initial successful apparatus check, with temporary workspace paths sanitized. The initial result has 24 expected suite outcomes across 12 visible and 47 hidden test methods.

Do not repair an evaluator after inspecting experimental results and pool the affected rows with earlier results. If a task contract or hidden check needs correction, version the fixture, record the reason and re-freeze it before new runs. Difficulty and usefulness remain empirical questions; seeded base failures are not model failure rates.
