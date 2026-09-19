# Checkpoint handoff: telling "arrived well" apart from "finished well"

A design for the research program, 19 September 2026. Status: proposed, not run. Gate: after the first look at the plain F1 comparison. Source: [Reach or Solve?](../scans/2026-09-19/03-reach-or-solve.md) (arXiv 2609.19636), adapted; that paper studies reinforcement-learned against supervised policies on agent benchmarks, and nothing in it is a claim about software workflows.

## The confound this removes

In the paired study, each arm writes the state it later works from. A light arm and a compact arm reach different working trees, different notes, and different partial fixes, then each finishes from its own. When one arm is accepted more often, the result mixes two abilities: getting the work into a good state, and completing from one. Restricting the comparison to states both arms reach does not fix it, because that selects on the outcome; the source paper reports that this restriction flipped the sign of the effect in its data.

The harness already clones repositories per arm and commits a task base, so the missing piece is not plumbing. It is the crossing: let each configuration finish from the other's state.

## Definitions for this repository

- **Milestone state.** The arm's working tree at the end of its first review round: for `light`, after its single independent review; for `compact`, after its first critic verdict. The arm commits it in its own clone with a fixed message, so the state is recoverable after the arm runs to completion.
- **Continuation.** A fresh headless session, same model and tool allowlist, starting from a cloned milestone state with a prompt that carries the same contract plus a fixed continuation budget. It is told the tree was produced by an earlier run and where that run's notes are; it is not told which topology produced it.
- **REACH proxy.** The share of a configuration's milestone states that any continuation finishes within the continuation budget. The source paper defines arrival against an environment oracle for distance to success; a repository has no such oracle, so completion under a fixed budget is the surrogate, and it is a surrogate, not the paper's measure.
- **SOLVE.** The share of milestone states, from either producer, that a given configuration finishes within the same budget.

## Design

Per task, four cells: reacher in {light, compact} crossed with solver in {light, compact}. The two self cells are the plain arms continuing their own work, which the F1 runs already produce. The two cross cells are new continuations, so the marginal cost is two shorter runs per task.

Order within a task is counterbalanced as in the main protocol, and every continuation gets the same budget so a cell cannot win by spending more. The continuation prompt is identical across cells except for the topology block, exactly as the arm prompts are today.

## Outcomes

| Outcome | Question it answers |
| --- | --- |
| `reach_rate` per configuration | Does this configuration leave the work in a state that anyone can finish? |
| `solve_rate` per configuration | Does this configuration finish work someone else set up? |
| reacher by solver interaction | Is a configuration's own state worth more to itself than to the other? |

Analysis is paired by task and uses the exact tests already committed in `tools/paired_study/analyze_pairs.py`, with the same sequential looks and the same alpha split. Harness failures are excluded and counted, as in the main protocol.

## Cost

Two extra continuations per task, each starting mid-task and therefore shorter than a full arm. The gate keeps that bounded: run the crossing only on tasks where the plain arms disagreed, or on a random subset of them, and only after the first F1 look has measured per-arm cost.

## What could make this measure nothing

- **The tasks are too easy.** On a one-token mutation an arm may finish before any milestone exists, leaving nothing to hand off. Then the design belongs on medium tasks, which must be cut by a person from release commits (B-025), and the mutation tasks stay with the plain comparison.
- **The milestones are not comparable.** Each arm's milestone is defined by its own first verdict, so the two producers have spent different effort by then. The crossing compares solvers on identical states, which is sound; comparing producers' states across arms carries that caveat and must state it.
- **The commit instruction changes behavior.** Asking an arm to commit its milestone is a small deviation from the plain arm prompt, so handoff runs are their own condition and cannot be a reanalysis of existing F1 rows.
- **Continuations inherit notes.** The state includes the producer's own records, which may reveal its topology. If a continuation can infer the producer, the comparison is no longer blind; the notes it inherits must be checked for that before the first crossing runs.

## First step when the gate opens

1. Extend the runner with a milestone commit instruction and a `--continue-from <snapshot>` mode that clones a recorded milestone and runs a continuation prompt.
2. Take three tasks where F1 arms disagreed, run the two cross cells for each, and read all six transcripts before computing anything.
3. Report `reach_rate`, `solve_rate`, and the interaction beside the plain acceptance numbers, with the surrogate definition of REACH stated in the same table.
