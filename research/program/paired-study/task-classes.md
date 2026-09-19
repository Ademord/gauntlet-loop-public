# Task classes, and how a class earns its place in the study

Written 19 September 2026, after the first look at flag F1.

## The problem this document solves

The first look ran fourteen pairs of one-token mutation tasks. Both topologies solved all fourteen. The finding
that mattered was not in the p-values:

> Every arm in every pair used exactly one critic review.

Arm B is the `compact` topology, whose mechanism is build, review, **revise**. When the first review accepts, arm B
does everything arm A does and then stops, plus the fixed cost of a second agent's context. The flag was set, the
arms differed in their prompt, and the mechanism the flag names never ran. A study can be perfectly executed and
still measure nothing, and this one was measuring exploration overhead while its title said revision loop.

The repair is not a better test. It is a task pool where a first review can fail.

## The admission criterion

A task class is admitted to a flag's study only if it makes that flag's mechanism fire. For F1 the measurable form
is the **contrast-fired rate**: the share of pairs whose arm B used two or more reviews. It is computed from
`reviews_used`, recorded for every run since the first pair, and needs no judgment. The third amendment to the
protocol pre-registers it as a secondary outcome and states what a zero rate means.

The criterion generalizes. Every flag has an observable that says whether its mechanism engaged:

| Flag | Mechanism | Fired when |
| --- | --- | --- |
| F1 light vs compact | the revision loop | arm B uses two or more reviews |
| F2 ladder on vs off | the third-round evidence rule | any arm reaches review round three |
| F3 parallel lenses vs single critic | lens disagreement | two lenses report findings that do not overlap |
| F4 retrieval on vs off | the lesson allowance | at least one retrieved lesson is cited in a decision |

Running a flag on a class that never fires its mechanism produces a real number and a false subject. Report the
rate next to the result, always.

## The ladder of classes

Three classes, cheapest first. Each is a different bargain between how easily it can be minted and how much of the
skill it exercises.

### 1. Mutation, `m*`, minted by `mint_mutations.py`

One semantic token changed in a test-covered line: a flipped comparison, a swapped `and`, a dropped `not`, an
integer off by one. Kept only if exactly one or two tests fail.

- Cost: free to mint, about two dollars and seven minutes a pair to run.
- Supply: large. Twenty-eight tasks came out of five files of one repository.
- Exercises: locating a defect from a failing test, and the scope discipline.
- Does not exercise: design, the revision loop, any judgment. Measured contrast-fired rate at the first look: zero
  of fourteen.
- Verdict: a valid class for the low-difficulty end of the gradient, and only for it. Keep it, label it.

### 2. Excision, `x*`, minted by `mint_excisions.py`

A whole function body is removed and replaced with a `raise NotImplementedError`. The signature, decorators and
docstring stay. Kept only if at least three tests fail.

- Cost: free to mint. Running cost is expected to be higher than a mutation pair, because the builder writes code.
- Supply: moderate. Fourteen functions of ten lines or more exist in the same five files; about nine are in the
  usable band of eleven to forty lines. Other repositories are needed for volume.
- Exercises: reading a contract out of tests, writing an implementation, and a review that can find it wrong,
  incomplete, or right for the wrong reason.
- Known limits: the function's name and its docstring remain, so intent is given; the task is reimplementation, not
  diagnosis. Tests that pin an exact output format make a fair-looking task that is really a guessing game, so the
  minter's size band excludes the two largest reporting functions, and any task whose failing tests are all string
  comparisons should be reviewed by hand before use.
- Status: piloted on eight pairs, 19 September 2026. Both topologies accepted and solved all sixteen arms. The
  contrast-fired rate is 1 of 8 by the pre-registered proxy and 0 of 8 by the thing it proxied for, because the one
  pair with two reviews had a first critic that passed and a second that confirmed. The class is admitted for cost
  comparisons and **not** admitted for anything about the revision loop.

### 3. Hand-cut from release commits, backlog B-025

A person reverts the implementation half of a real feature commit and keeps its tests. This is the only class that
carries real intent, real scope, and the mess of a real change.

- Cost: human time per task, which is why there are none yet. The first survey found two mintable commits out of
  seventeen; the rest are release-sized.
- Exercises: everything, including the judgment-heavy checks the deterministic classes cannot express.
- Status: owner's task. It stays on the backlog rather than being faked by a script.

## What this means for the program

1. F1 finishes its thirty mutation pairs, because the series was pre-registered and stopping at the first
   unfavourable look is the practice pre-registration exists to prevent. Its conclusion will be stated for the
   class it actually measured.
2. The excision pilot ran on 19 September and answered it: a first review never rejected. Writing more code is not
   what makes a review reject, so the next class must vary something else. See the new pre-registration below.
3. The checkpoint-handoff experiment (B-023) needs a class where the first verdict is not the last, so it is gated
   behind the same pilot.

## Pre-registered before the pilot runs

- Pilot size: up to eight excision pairs, the same F1 arms, the same runner, the same model.
- Reading: if the contrast-fired rate is zero, the class is recorded as not useful for F1 and no series follows. If
  it is one in eight or more, a thirty-pair series is registered as a separate study with its own three looks.
- The pilot's pairs are **not** pooled with the mutation series. They are a different class, and mixing them would
  produce an average over two populations that describes neither.

## Pre-registered before the next class is built, 19 September 2026

The first metric was wrong and the pilot showed how: a review count cannot tell a rejection from a confirmation.
Both fixes below are written before any task of the next class exists.

1. **The metric is the verdict, not the count.** `mechanism_fired` is true for an arm when its **first** critic
   report carries a negative verdict: `REJECT`, `FAIL`, `REVISE`, `HOLD`, or a winner of `bar` or `none` in the v5
   vocabulary. It is extracted deterministically from the transcript, and an unparsed verdict counts as not fired
   and is reported separately, never silently dropped.
2. **The next class varies specification, not volume.** Candidates, in the order they will be tried: a task whose
   tests pass for an implementation that violates a constraint stated only in the prompt; a task whose repair
   requires touching a second file the failing test does not name; a task with a deliverable that is not a test.
   Each is piloted at four pairs, and a class is admitted only if `mechanism_fired` is at least one in four.
3. **A class that fails two pilots ends the search from minted tasks**, and the program says plainly that a
   deterministic oracle over a repository cannot produce work a first review rejects, which would itself be the
   result: the gauntlet's revision loop would be measurable only on judgment-heavy deliverables.
