# Contributing

Three kinds of contribution, each with a fixed path.

1. **A paper.** Write one note per paper under `research/scans/<date>/` with [TEMPLATE.md](research/scans/TEMPLATE.md), following [research/INTAKE.md](research/INTAKE.md): the abstract verbatim, the supplied paraphrase checked line by line, limits, where the skill already stands, a bounded proposed change with a falsifier, and a verdict. A note may add one candidate row to the [backlog](research/program/backlog.md).
2. **A run record.** Gauntlet runs keep a contract, events, state, progress, and evidence under `gauntlet/<run-id>/` and append one milestone line to `gauntlet/runs.jsonl`; see [gauntlet/README.md](gauntlet/README.md). Refer to another project by name only if it is public.
3. **A change to the skill.** Only through an upgrade run: checks frozen first, the current version as the bar, independent critics, then the steps in [versions/README.md](versions/README.md#adding-a-version). Nobody edits `skill/` directly: the `commit-msg` hook refuses a commit that changes `skill/` unless its message carries `Upgrade-run: <run-id>` for an existing `gauntlet/<run-id>/`.

## Before your first commit

- Run `pip install --target .validation-deps pyyaml pytest`, then `git config core.hooksPath tools/hooks`. The pre-commit guard refuses staged text containing personal paths, machine or personal identity, secrets, or any term in your local `tools/private_terms.local.json`.
- Keep real paths in gitignored `*.local.json` files: `ledger/config.local.json` holds the roots for the run ledger, and its first root also fills `<projects-root>` in task specs (or set `GAUNTLET_PROJECTS_ROOT`); `tools/paired_study/survey_config.local.json` holds the survey root.
- Before pushing, run `python tools/verify_release.py`, and the validator if you touched `skill/` (see [tools/README.md](tools/README.md)).
