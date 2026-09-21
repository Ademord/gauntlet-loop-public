# Paired-study log

Newest entries last. Every entry that spends model tokens, or could, records what ran, what it cost, and what it established.

The September 19 entries are historical records. See the [September 20 correction](#2026-09-20-correction-to-the-interpretation-of-the-september-19-results) before relying on their x008 or statistical interpretations.

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

## 2026-09-19, deviation: a task spec was renamed after its arms had run

One spec named a project repository that is not public. The rule in this repository is that another project may be
named only if that project is public, so the name was removed from the tree: the spec file is now
`002-demo-autoplay-on-entry.yaml`, its `repo` field reads `<projects-root>/<alias:demo-app-1>`, and a gitignored
`tasks/aliases.local.json` resolves the alias locally. A quoted commit message that carried the name was replaced
with a neutral description. The runner gained alias resolution for this.

The deviation is that the spec changed after both of its arms had run. Its two recorded rows keep the hash of the
spec as it was, so `run_pair` would refuse to rerun that pair against the old manifest; the manifest was
regenerated, and the pair would have to be rerun from scratch to be counted again. Nothing in the recorded results
changed, and t002 stays in the thirty counted pairs, because the task content is identical: only a name moved
behind an alias.

The name is still in two commits of this repository's history. Removing it there needs a history rewrite and a
force push of a public repository, which is the owner's decision, not the agent's.

Two defects were found while doing this, and both are fixed:

- **The manifest recorded whatever spec path it was given.** Regenerating with an absolute path put a personal home
  directory into a tracked file. `make_arms.py` now records the path relative to the repository and refuses a spec
  from outside it.
- **Neither the audit nor the pre-commit hook could see that path.** A Windows path inside a JSON string has its
  separators doubled, and the patterns were written for the single form, so the doubled form matched nothing. Both
  now scan a de-escaped copy as well. Verified against a synthetic escaped path: one hard hit where there were
  none before, the plain form still hit, clean text still clean, and the hook refuses a staged file carrying one.

## 2026-09-19, excision pilot: the proxy fired once, the mechanism never did

Eight pairs on the excision class, run under the flag key `F1-excision` so the rows can never pool with the
mutation series. No harness failure. Report: [look-F1-excision.md](look-F1-excision.md). Cost $17.23.

| | A, light | B, compact |
| --- | --- | --- |
| solved, suite passes | 8 of 8 | 8 of 8 |
| accepted | 8 of 8 | 8 of 8 |
| median turns | 23 | 34 |
| median tokens | 2,032,807 | 3,417,203 |
| total cost | $8.02 | $9.21 |
| median seconds | 202 | 242 |

**The pre-registered number and what it turned out to mean.** The contrast-fired rate is 1 of 8: on x008 the
compact arm used two reviews. The rule written before the pilot says one in eight or more registers a thirty-pair
series. Reading that transcript before computing anything, as the design requires, shows the proxy misfired. The
first critic returned "Verdict: PASS" with one non-blocking edge-case note, and the lead then ran a *second,
confirmatory* final review, which returned "Verdict: ACCEPT". No rejection, no revision. The sequence the flag
names, build then reject then revise, did not happen.

So two readings, both recorded, neither hidden:

- by the letter of the pre-registered metric, the class clears the bar, 1 of 8;
- by the thing the metric was a proxy for, a first review that rejects, the class scores **0 of 8**, and across all
  76 recorded arms of both classes **no first review has ever returned a negative verdict**.

**What is not being done, and why it is stated rather than quietly skipped.** The thirty-pair excision series is
not being run now. At a rejection rate of zero it would buy another "no difference detected" on a class whose
mechanism does not engage, for about $65 and three hours, which is the exact mistake the third amendment was
written to stop repeating. The letter of the rule says run it; the owner can overrule this and have it run. What
replaces it is a new pre-registration, written below before any new data exists.

**Why the class failed to fire, which is the useful part.** The difficulty axis was wrong. An excision task removes
between 11 and 29 lines and fails three to eight tests, so it is much larger than a one-token mutation, and the
model solved all sixteen arms anyway. Volume of code to write is not what makes a first review reject. The
candidates for what does: a contract the tests underspecify, so a passing implementation can still be wrong;
coupling across files, so a local fix breaks something the arm did not look at; a stated constraint that conflicts
with the obvious implementation; or a deliverable whose acceptance is not a test at all.

**Two compliance findings, from the same transcripts.**

- On x004 the light arm dispatched **no critic at all**. It repaired the function, verified it itself, and
  reported. The light topology asks for one *independent* review, so that run did not run the topology it was
  assigned. The harness still judged it correctly, because acceptance is the harness's own rerun and never the
  arm's word.
- On m013 in the mutation series, the arm's own milestone reported one review while the harness observed two
  dispatches. `reviews_used` prefers the arm's self-report and falls back to the observed count, so it is not the
  deterministic measure the protocol calls it. This is the stated-versus-behavioral gap of the fourth
  19 September paper, in this repository's own data, on the one dimension it can measure today.
  `tools/paired_study/audit_self_reports.py` now reports both: 1 mismatch and 1 zero-dispatch arm in 76, and that
  count is a lower bound, because an arm that writes no milestone agrees with the observed count by construction.

Neither finding changes any recorded result. The mutation series contrast-fired rate stays 0 of 30: the m013
discrepancy is in arm A, and the metric is defined on arm B.

## 2026-09-20: correction to the interpretation of the September 19 results

No new benchmark runs or paid model experiments were launched. This correction preserves the earlier entries,
raw results, recorded stopping decision and historical sign-test verdicts; it corrects their interpretation.

- **x008 did revise.** The earlier "No rejection, no revision" statement is wrong. In the
  private arm-B transcript (local file `pairs/x008-intelligence-vlm-call_json/F1-excision/armB.transcript.jsonl`), line 182 says the
  lead will address the critic's edge case; line 185 changes the provider exception handler to preserve
  `VLMParseError` as well as `VLMTransportError`; line 195 initiates another independent review. The first
  verdict was PASS with a non-blocking finding. Thus there was no rejection-triggered revision, but there was
  a critic-driven code revision followed by a second review. The original dispatch-count rate remains 1/8;
  a rate based only on negative verdicts would miss this behaviour. This local contribution is not evidence
  that compact outperformed light across tasks.
- **The two token summaries answer different questions.** The bootstrap interval describes the paired mean;
  the sign test tests the balance of positive and negative differences after excluding ties and ignores their
  magnitudes. The earlier description as a "rank-based test" was imprecise: this was not a signed-rank test.
  An interval excluding zero and a non-significant sign test can coexist. They must not be used interchangeably
  or selected after seeing which favours a configuration.
- **Non-significance is not equivalence.** All sampled tasks passed their suites, and the historical tests did
  not establish an outcome difference. That supports "no observed correctness gain on these sampled tasks",
  not "pure overhead" as a general causal conclusion. MDE estimates discussed in the later audit are planning
  quantities at a specified power, not hard floors below which a significant result is impossible; a paired-mean
  approximation also does not describe the power of the sign test. A/A repeats would measure local variability,
  not a universal noise threshold for later task classes.

See the [corrected gap analysis](../gap-analysis-2026-09-20.md) for the associated methodology erratum.
