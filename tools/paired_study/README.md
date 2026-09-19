# Paired-study harness

Protocol: [research/program/phase2-paired-study.md](../../research/program/phase2-paired-study.md). Everything here costs zero model tokens except `run_pair.py --execute`.

1. Write a task spec from a minted revert-fix task (see `task_spec.example.yaml`). Record difficulty and verifiability before anything runs.
2. `python tools/paired_study/make_arms.py --spec <spec.yaml> --flag F1` writes `armA.prompt.md`, `armB.prompt.md`, and `manifest.json` (spec hash, counterbalanced order, prompt hashes, the only difference between arms).
3. `python tools/paired_study/run_pair.py --pair <pair dir> --dry-run` shows the worktrees and commands. `--execute --agent claude` runs both arms headlessly in their worktrees and appends rows to `research/program/paired-study/results.jsonl`. Execute mode is untested as of 17 September 2026; the first pair is the harness test and must be read by a person.
4. `python tools/paired_study/analyze_pairs.py --results research/program/paired-study/results.jsonl --flag F1` prints the exact-test results and bootstrap intervals. `--selftest` checks the analysis on synthetic pairs with a planted effect and a null.

Guards built in: the runner refuses a spec whose hash changed after the pair was generated; the critic prompt is identical across arms (the flag block is the only diff, recorded in the manifest); harness failures are excluded and counted, never scored.

Not built: automatic task minting from git history (survey first, mint by hand), token accounting from headless transcripts (recorded `unknown` until the transcript format is known), and any scheduling.

## Added 19 September 2026

- `mint_mutations.py` mints low-difficulty tasks from a Python repository with an offline test suite: one semantic mutation per candidate line, kept only if exactly one or two tests fail; the original line is the answer. Specs record the repository as `<projects-root>/<name>` and the mutation by line and byte columns.
- `run_pair.py --execute` now runs a login preflight, isolates each arm from user-level settings, hooks, MCP servers, and skills, restores protected test paths before the independent suite run, and measures cost, tokens, turns, and critic dispatches from the transcript. Transcripts and each arm's `gauntlet/` folder stay local (gitignored); the results row is the public record.

## Running a series

`run_series.py --flag F1` runs every ready pair for a flag, one at a time, skipping pairs that already have counted rows, stopping on a dead login and after two consecutive harness failures. `report_pairs.py --flag F1` then writes `research/program/paired-study/look-F1.md` from the rows, with the exact tests from `analyze_pairs.py`. Neither script interprets anything: every number in the report comes from a recorded row.
