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

## 2026-09-19, later: the first execution, kept as a pilot

The owner logged the CLI in; the preflight passed at $0.20 and both arms of t001 under flag F1 ran to completion.

| Arm | Topology | Accepted | Held-out | Reviews | Turns | Tokens | Cost | Denials | Wall clock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | light | yes | passed | 1 | 5 | 407,622 | $0.86 | 0 | 176 s |
| B | compact | yes | passed | 1 | 27 | 1,806,843 | $1.03 | 12 | 245 s |

Both arms made the same one-line change, the out-of-band sum check from warning to error, and both passed the held-out test that separates that fix from an over-broad one. Arm A dispatched one critic, which re-diffed against the task base, reran the suite, and checked that the fix was general rather than special-cased to the two pinned tests. Arm B arrived at the same place with five times the turns and four and a half times the tokens.

**Why it is a pilot and not the first counted pair.** Reading the transcripts, as a harness test is for, found two defects in the harness itself. The clone carried the source repository's whole history, so the upstream fix was reachable from inside an arm; both transcripts were searched and neither arm looked, but a design that allows it cannot be trusted. And the tool allowlist was too tight: all twelve of arm B's denials were ordinary shell composition, such as piping test output through `tee`, which cost it turns and tokens. Both rows are marked `pilot` in `results.jsonl`, the analysis skips them, and the protocol carries both findings as its second 19 September amendment.

**What the pilot does establish.** The harness runs end to end: preflight, task base, headless arm, independent rerun with the protected tests restored, scope check, held-out check, and cost measured from the transcript. A pair of this size costs about two dollars and seven minutes. The protocol's earlier guess of 100k to 400k tokens per arm was right for the light arm and four times too low for the compact one, so thirty pairs are on the order of sixty dollars rather than the earlier estimate.

**Fixes now in place.** The task base is built in a fresh repository with a single commit, so no history reaches an answer. The allowlist covers ordinary read-only shell verbs, and network and scheduling tools are denied explicitly. Every arm gets the same treatment, so neither topology is favoured.

## 2026-09-19, first look at flag F1: fourteen pairs

The harness fix held. t001 was rerun as the first counted pair, then the other thirteen ran as a series with no harness failure. Report: [look-F1.md](look-F1.md), generated from the rows by `report_pairs.py`.

| | A, light | B, compact |
| --- | --- | --- |
| accepted | 13 of 14 | 14 of 14 |
| solved (suite passes) | 14 of 14 | 14 of 14 |
| median turns | 19 | 30 |
| median tokens | 1,531,950 | 2,527,816 |
| total cost | $11.67 | $13.48 |
| median seconds | 178 | 212 |

Pre-registered tests at the first look, with the per-look threshold of 0.0167: acceptance p = 1.0 on one discordant pair; reviews identical; tokens, mean difference -787,438 with a bootstrap interval of [-1,195,730, -384,247] and a sign-test p of 0.057; cost, mean difference -$0.13 with an interval spanning zero; wall clock, no difference. The committed reading is **no difference detected**.

**What actually happened, which matters more than the headline.**

- Every arm in every pair used exactly one critic review. The compact arm's first review accepted, so it never revised. The flag's contrast therefore never exercised the revision loop; what it measured was exploration overhead. At this difficulty the two topologies collapse into the same behavior, and the extra structure bought nothing measurable while spending about a third more tokens.
- The single acceptance difference is not a failed repair. On m012 the light arm left two scratch files (`pytest_pre_output.txt`, `pytest_post_output.txt`) in the repository root, which the pre-registered scope rule counts as not accepted. Its suite passed; by solving alone both arms are 14 of 14.
- Cost did not track tokens, because most tokens are cache reads. A token difference of about 30% shows up as about 13 cents a pair.
- This is the easy end of the difficulty gradient the program set out to test, and the result is the one that gradient predicts for it. It says nothing about hard tasks, which is where the same reading predicts the opposite.

**Deviation recorded:** the protocol schedules looks at 10, 20 and 30 pairs. This look is at 14, because the series ran to completion before analysis. It counts as the first of the three planned looks, and no stopping rule was met.

## 2026-09-19, second look at flag F1: thirty pairs, and the series ends here

The sixteen remaining pairs ran as one series with no harness failure. Report: [look-F1.md](look-F1.md), generated
from the rows by `report_pairs.py`. Thirty counted pairs, two pilot rows and two harness-failure rows excluded, all
four from t001 before the login and isolation fixes.

| | A, light | B, compact |
| --- | --- | --- |
| solved, suite passes | 30 of 30 | 30 of 30 |
| accepted | 28 of 30 | 30 of 30 |
| median reviews | 1 | 1 |
| median turns | 18 | 24 |
| median tokens | 1,493,593 | 2,118,063 |
| total cost | $25.63 | $28.03 |
| median seconds | 176 | 188 |

Pre-registered tests, per-look threshold 0.0167: acceptance p = 0.5 on two discordant pairs; reviews used identical
in every pair; tokens mean difference -476,552 with a bootstrap interval of [-881,458, -44,211] and a sign-test p
of 0.200; cost mean difference -$0.08 with an interval spanning zero; wall clock mean difference -21.9 s with an
interval spanning zero. The committed reading is **no difference detected**.

**The contrast-fired rate is zero of thirty.** Not one arm B in the whole study used a second review. Under the
third amendment, written and committed before these sixteen pairs were generated, that ends the F1 series on
mutation tasks whatever the p-values say, and fixes the conclusion:

> On one-token defects with a deterministic oracle, the compact topology's first review accepts, so its extra
> structure is pure overhead. The flag is untested on work where a first review would reject.

F1 now moves to the medium-task pool. No third look will be taken; the thirty-pair target is met, and the alpha was
split across three looks while only two were used, which is conservative rather than permissive.

**Three things worth recording beyond the headline.**

- **The early token signal did not hold.** At fourteen pairs the mean difference was -787,438 with a sign-test p of
  0.057, close enough to look like something. At thirty it is -476,552 with p = 0.200, and eleven of thirty pairs
  ran the other way. The interval still excludes zero while the sign test does not reject, which is the ordinary
  disagreement between a mean-based interval and a rank-based test when a few large pairs carry the mean. Reading
  the first look as a near-miss would have been wrong.
- **Both discordant pairs are the same failure, and it is not a failed repair.** On m012 and m028 the light arm
  left pytest output files in the repository root, which the pre-registered scope rule counts as not accepted. Both
  suites passed. Two of thirty light arms did this and none of the compact arms did, which is p = 0.5 and a
  description, not a finding.
- **Cost did not follow tokens.** A token difference of roughly 30% is eight cents a pair, because most tokens are
  cache reads. Any future claim about a topology being cheaper has to say cheaper in what unit.

**Cost of the study.** Thirty pairs, $53.65 in API-equivalent pricing, about six minutes a pair.
