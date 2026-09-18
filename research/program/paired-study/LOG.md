# Paired-study log

Newest entries last. Every entry that spends model tokens, or could, records what ran, what it cost, and what it established.

## 2026-09-19: harness hardened, first pair blocked at login, twelve tasks minted

Resume validation, written before anything was run:

```yaml
resume_validation:
  checkpoint_id: a879d38            # main, pushed and equal to origin/main
  artifact_identity: match          # clean working tree
  versions: {skill: "5.0.0", protocol: "phase2-paired-study.md as committed", tasks: "t001 and t002 specs, hash-checked by the runner"}
  authorization: valid              # owner, 2026-09-17: paired runs approved where they carry value; 2026-09-19: continue the pipeline
  external_effects: confirmed       # nothing in flight
  holds_carried: []
  decision: resume
```

**Harness changes before spending** (commit `f6ce73b`). The arm prompt goes in on stdin with stream-json output. Both arms are pinned to `claude-sonnet-5`, with permission mode `acceptEdits` and a 28-tool allowlist. Clones live in the system temporary directory, outside any repository, so no parent instruction file loads. Protected test paths are restored to the task base before the independent suite run, changed files outside the allowed paths are reported, held-out tests run last, and cost, tokens, turns, and critic dispatches are read from the transcript.

**First attempt: t001, flag F1.** Both arms ended in under two seconds at zero cost. The transcript's first assistant message was "Failed to authenticate: OAuth session expired and could not be refreshed": the standalone `claude` CLI on this machine was not logged in, while the desktop session that ran the harness was. Both rows are kept in `results.jsonl` as harness failures with that reason; the protocol excludes them from analysis. No task work happened and nothing was spent.

**Fixes after the attempt.** A preflight call of a few tokens now confirms the CLI login before anything is cloned. The runner stops a pair when an arm fails at startup instead of running the other arm. Arms run with `--setting-sources project,local --strict-mcp-config --disable-slash-commands`, because the failed transcript showed five user-level SessionStart hooks firing inside each arm; now no user-level hooks, plugins, MCP servers, or skills reach an arm. The protocol carries these changes as its 19 September amendment.

**Mutation minting (B-014).** `mint_mutations.py` over five source files of `intelligence-pipeline` (a public repository with an offline 26-test suite that runs in about 4 seconds): 189 candidate mutation points, 39 tried with seed 17, 12 kept because exactly one or two tests failed. Five flip a comparison (`is`/`is not`, `in`/`not in`), two swap `and`/`or`, five change a small integer. Six live in `evaluate.py`, three in `schema.py`, two in `vlm.py`, one in `validation.py`. The runner rebuilt all twelve task bases and each failed exactly its recorded tests. F1 arms were generated for all of them, so fourteen pairs are ready: t001, t002, and m001 to m012.

**Blocked on:** one login of the `claude` CLI by the owner. The harness test is then t001 on its own; its two transcripts get read before any further pair runs.
