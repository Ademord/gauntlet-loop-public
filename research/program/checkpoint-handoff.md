# Checkpoint handoff: telling "arrived well" apart from "finished well"

A design for the research program. Revision 2, 19 September 2026, after reading the source paper's full text.
Status: proposed, not run. Gate: the F1 mutation series finishes, and the excision pilot shows a task class where a
first verdict is not the last ([task-classes.md](paired-study/task-classes.md)). Source:
[Reach or Solve?](../scans/2026-09-19/03-reach-or-solve.md) (arXiv 2609.19636), adapted; that paper studies
reinforcement-learned against supervised policies on agent benchmarks, and nothing in it is a claim about software
workflows.

## The confound this removes

In the paired study, each arm writes the state it later works from. A light arm and a compact arm reach different
working trees, different notes, and different partial fixes, then each finishes from its own. When one arm is
accepted more often, the result mixes two abilities: getting the work into a good state, and completing from one.

Restricting the comparison to states both arms reach does not fix it, because that selects on the outcome. The
source paper measures the damage: on its 480-row matrix the endpoint interaction is 24.2 points with a 95% interval
of [13.3, 35.0], while the same episodes scored survivor-only give -12.6 points with an interval of [-45.8, 22.7],
a paired difference of -36.8 points. The authors add that this diagnostic was specified after its point estimates
were seen, so it is not itself a confirmatory result. The rule it justifies is the one worth copying: **a run that
never produces a handoff state is a failure in the population, not a row to drop.**

## What the paper's second variant licenses

The frontier variant needs an environment oracle. ALFWorld's symbolic engine can enumerate admissible actions, so
"exactly two valid actions from success, with budget to take them" is verifiable, and membership depends on the
environment rather than on which checkpoint produced the state. A git repository has no such oracle, and inventing
one would be the weakest part of this design.

The paper's TravelPlanner variant has no oracle either. There the cut is a recorded-trajectory event, taken
immediately before the reacher's final model call; both solvers then receive the same record and a fixed budget of
four model decisions, and the replayed prefix is checked for an identical reconstructed history. That is the shape
this repository can implement honestly, and this design follows it rather than the frontier variant.

## Definitions for this repository

- **Handoff rule.** Prespecified, computed from the reacher's own run and nothing else: the cut is the end of the
  arm's first review round, which for `light` is its single independent review and for `compact` is its first
  critic verdict. It cannot depend on the solver or on any continuation outcome.
- **Handoff state.** The arm's working tree at the cut, committed in its clone with a fixed message, plus the
  arm's own notes and the remaining budget. Recoverable after the arm runs on to completion.
- **Non-arrival.** The arm produced no first verdict inside its budget: it parked, timed out, or exhausted its
  reviews. Its continuation value is zero, and it stays in the denominator.
- **Continuation.** A fresh headless session, same model and tool allowlist, cloned from the handoff state, with a
  prompt carrying the same contract and a fixed continuation budget. It is told the tree came from an earlier run
  and where that run's notes are. It is **not** told which topology produced it.
- **REACH, `A_W`.** The share of a configuration's runs that produce a handoff state at all.
- **SOLVE, `C_{W,R}`.** The share of handoff states produced by W that configuration R finishes within the
  continuation budget.
- **Endpoint.** `J(W, R) = A_W * C_{W,R}`. The reacher moves the first factor, the solver the second. Reporting
  the product and both factors is required, so that no result can say "better" without saying which factor moved.
- **Interaction.** `I = [J(c,c) - J(c,o)] - [J(o,c) - J(o,o)]` over the two configurations, the difference of two
  products of an arrival rate and a same-state solve gap. Positive means a configuration's own state is worth more
  to itself than to the other.

## Design

Per task, four cells: reacher in {light, compact} crossed with solver in {light, compact}. The two self cells are
the plain arms continuing their own work, which the F1 runs already produce. The two cross cells are new
continuations, so the marginal cost is two shorter runs per task.

Order within a task is counterbalanced as in the main protocol, and every continuation gets the same budget so a
cell cannot win by spending more.

**Guards, all deterministic and all copied from the source:**

1. The two continuation prompts for one handoff state must hash to the same value. The runner computes the hash of
   the prompt and of the cloned tree, records both, and refuses the pair if they differ. Only the topology block
   may differ, exactly as the arm prompts differ today, and it is hashed separately.
2. The handed-off tree is compared against the recorded handoff commit before the solver starts, the way the source
   replays a prefix and checks for an identical reconstructed history.
3. The producer's notes are scanned for its own topology name before they are handed over. If the state announces
   who made it, the comparison is not blind.
4. Non-arrivals are written to the results file with a zero outcome, never omitted.

## Outcomes

| Outcome | Question it answers |
| --- | --- |
| `reach_rate` = `A_W` | Does this configuration produce a state to hand off at all? |
| `solve_rate` = `C_{W,R}` | Does this configuration finish work someone else set up? |
| `J(W,R)` | The endpoint the two factors multiply to |
| interaction `I` | Is a configuration's own state worth more to itself than to the other? |
| first continuation act | Does the solver rerun the checks before editing, or edit first? |

The last row is the local analogue of the source's two-stage split of SOLVE into choosing a bridge action and
finishing from it, which showed the deficit split roughly evenly between the two stages. A single conversion rate
would hide the same thing here.

Analysis is paired by task and uses the exact tests already committed in `tools/paired_study/analyze_pairs.py`,
with the same sequential looks and the same alpha split. Harness failures are excluded and counted, as in the main
protocol; non-arrivals are **not** harness failures and are never excluded.

## Not adopted, with reasons

- **The component prediction test.** Forecasting the interaction from independently measured gaps needs a separate
  sample of handoff states that the target runs never visited. This repository has no such sample. The source's own
  result argues against the effort: the forecast lands 3.5 points from the observed value in aggregate while the
  per-type residuals run from +25.0 to -12.0 and take both signs.
- **Paired seeds.** The source pairs seeds because seed choice alone moves reported agent performance by a wide
  margin. A headless CLI run of a hosted model exposes no seed, so pairing here is by task only. This is a real
  weakness of the local adaptation, not a detail.
- **The verified frontier.** No oracle for "how far from done is this repository state" exists, and a surrogate
  dressed up as a measurement would be worse than the recorded-cut variant.

## What could make this measure nothing

- **The tasks are too easy.** On a one-token mutation an arm finishes in its first round, so the cut lands on a
  tree that is already accepted and every solver trivially finishes. The first F1 look confirms the risk: fourteen
  of fourteen pairs used exactly one review. The gate is therefore a task class where a first verdict is not the
  last, which is what the excision pilot tests.
- **The milestones are not comparable.** Each arm's cut is its own first verdict, so the two producers have spent
  different effort by then. Comparing solvers on identical states is sound; comparing producers' states across arms
  carries that caveat and must state it in the same table.
- **The commit instruction changes behavior.** Asking an arm to commit its handoff state is a deviation from the
  plain arm prompt, so handoff runs are their own condition and cannot be a reanalysis of existing F1 rows.
- **Continuations inherit notes.** Guard 3 exists for this, and it must run before the first crossing, not after.

## First step when the gate opens

1. Extend the runner with a handoff commit instruction and a `--continue-from <state>` mode that clones a recorded
   handoff state and runs a continuation prompt, with guards 1 to 4 wired in from the start.
2. Take three tasks from the class that passed the gate, run the two cross cells for each, and read all six
   transcripts before computing anything. The first F1 look found two harness defects by reading transcripts and
   none by reading numbers.
3. Report `A`, `C`, `J` and the interaction together, with the recorded-cut definition of REACH stated in the same
   table and the non-arrival count beside it.
