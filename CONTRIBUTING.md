# Contributing

Four kinds of contribution, each with a fixed path.

1. **A paper.** Write one note per paper under `research/scans/<date>/` with [TEMPLATE.md](research/scans/TEMPLATE.md), following [research/INTAKE.md](research/INTAKE.md): the abstract verbatim, the supplied paraphrase checked line by line, limits, where the skill already stands, a bounded proposed change with a falsifier, and a verdict. A note may add one candidate row to the [backlog](research/program/backlog.md).
2. **A run record.** Gauntlet runs keep a contract, events, state, progress, and evidence under `gauntlet/<run-id>/` and append one milestone line to `gauntlet/runs.jsonl`; see [gauntlet/README.md](gauntlet/README.md). Refer to another project by name only if it is public.
3. **A change to the skill.** Only through an upgrade run: checks frozen first, the current version as the bar, independent critics, then the steps in [versions/README.md](versions/README.md#adding-a-version). Nobody edits `skill/` directly: the `commit-msg` hook refuses a commit that changes `skill/` unless its message carries `Upgrade-run: <run-id>` for an existing `gauntlet/<run-id>/`.
4. **A research decision or experiment.** Link source/evidence records to stable milestone IDs in the [program index](research/program/README.md). Follow its [workflow](research/program/WORKFLOW.md): concrete comparison, six investor questions, scoped prerequisites, frozen inputs and an outcome including losses and unknown costs. Update the plan when research or native capabilities change; preserve previous results.

## Branches and releases

`main` is the continuing project home. It contains the usable skill, optional tooling, research, including unsuccessful experiments, and the historical versions. A research checkpoint is not a skill release, and merging its report does not promote a performance claim.

Use short-lived `codex/` branches for changes that need isolation; small documentation changes can land directly on `main` after checks. Integrate reviewed work without rewriting historical records. An integrated branch is no longer a parallel development home. Preserve archived versions, frozen inputs and original results; record corrections as dated additions or derived records.

The current release is identified in the main README and the published release tag. Skill changes still require the upgrade run described above, an incumbent snapshot, the version archive and release notes, rebuilt distribution artifacts, and independent acceptance. Tag the accepted release commit with its exact version when publishing a new release. Documentation, recorder changes or new evidence alone do not require a skill version bump.

For branch integration, verify the release and historical hashes, run the package validator, the relevant regression tests, `python tools/program.py validate`, `python tools/program.py render --check`, `python tools/readiness.py validate`, and the public-readiness audit. Inspect findings rather than interpreting a scanner exit code as acceptance. Keep raw task records, personal data and local settings private; publish only the selected sanitized evidence. Keep current status pages current while preserving checkpoint statements as dated history.

Community ideas are [backlog candidates](research/program/backlog.md#community-candidates-23-september-2026), not automatic release commitments. Reuse the existing milestone and readiness indexes when taking one up. Do not add another research queue or require repository instrumentation just to use the skill.

## Before your first commit

- Run `pip install --target .validation-deps pyyaml pytest`, then `git config core.hooksPath tools/hooks`. The pre-commit guard refuses staged text containing personal paths, machine or personal identity, secrets, or any term in your local `tools/private_terms.local.json`.
- Keep real paths in gitignored `*.local.json` files: `ledger/config.local.json` holds the roots for the run ledger, and its first root also fills `<projects-root>` in task specs (or set `GAUNTLET_PROJECTS_ROOT`); `tools/paired_study/survey_config.local.json` holds the survey root.
- Before pushing, run `python tools/verify_release.py`, and the validator if you touched `skill/` (see [tools/README.md](tools/README.md)).
