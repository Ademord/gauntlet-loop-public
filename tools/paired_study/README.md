# Paired-study harness

Protocol: [research/program/phase2-paired-study.md](../../research/program/phase2-paired-study.md). Everything here costs zero model tokens except `run_pair.py --execute`.

1. Write a task spec from a minted revert-fix task (see `task_spec.example.yaml`). Record difficulty and verifiability before anything runs.
2. `python tools/paired_study/make_arms.py --spec <spec.yaml> --flag F1` writes `armA.prompt.md`, `armB.prompt.md`, and `manifest.json` (spec hash, counterbalanced order, prompt hashes, the only difference between arms).
3. `python tools/paired_study/run_pair.py --pair <pair dir> --dry-run` shows the worktrees and commands. `--execute --agent claude` runs both arms headlessly in their worktrees and appends rows to `research/program/paired-study/results.jsonl`. Execute mode is untested as of 17 September 2026; the first pair is the harness test and must be read by a person.
4. `python tools/paired_study/analyze_pairs.py --results research/program/paired-study/results.jsonl --flag F1` prints the exact-test results and bootstrap intervals. `--selftest` checks the analysis on synthetic pairs with a planted effect and a null.

Guards built in: the runner refuses a spec whose hash changed after the pair was generated; the critic prompt is identical across arms (the flag block is the only diff, recorded in the manifest); harness failures are excluded and counted, never scored.

Not built: automatic task minting from git history (survey first, mint by hand), token accounting from headless transcripts (recorded `unknown` until the transcript format is known), and any scheduling.
