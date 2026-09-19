# Bars, worked examples, and what breaks a loop

Read this when setting a bar or drafting a prompt, and read the failure list at the end when a loop stalls. The
rest is not needed while executing a run whose bar is already fixed. Versions 1 to 3 carried this material in the entrypoint; v4 dropped it for size. It is restored here
because a bar that is not real is the one defect that makes every later step pointless, and because an agent
that has never done this needs an example, not only a rule.

## A bar has to pass three tests

- **Named.** A specific thing, not a category. "Stripe's pricing page" works. "Award-winning SaaS sites" does not.
- **Fetchable, which the entrypoint calls accessible.** The critic can actually get it: screenshot the live page, read the published piece, run the
  binary, open the repository, watch the footage. What cannot be obtained will be invented.
- **Comparable.** Both can sit side by side and a judge can pick one. If you cannot imagine the A/B, it is not a
  bar. Match audience, task, length, viewport, and constraints where they matter.

## Bars by goal type

| Goal | Bar that works |
| --- | --- |
| Website, app, UI | The live site of a specific best-in-class product, captured at the same viewport |
| Game, 3D, visual | Real footage or screenshots from a named shipped title |
| Writing | A specific published piece by a named author or publication, same length and format |
| Code, tooling | A named repository's implementation, plus its benchmark or test suite as the measurable half |
| Research, analysis | A named analyst report or a paper's methods section, judged on rigour and coverage |
| Deck, document, deliverable | A real artifact from a firm known for it, same page count |
| A repair | The failing original, plus the behavior contract and trusted examples the fix must satisfy |
| A workflow or a model | The incumbent, measured on the same frozen tasks, judged by a critic that saw neither run. Only for a comparison the user explicitly asked for; the entrypoint defers benchmarking |

For a repair the bar is not a prestige product. It is the broken artifact and the contract it must now meet, which
is why the verdict rules treat a repair comparison differently: see the execution contract.

## Two filled examples

Both obey the length target in [prompt drafting](prompt-drafting.md) and carry every include it lists. They are
illustrations of the shape, not text to paste unchanged.

**Visual software goal.** The user asks for a landing page in their GitHub repository for a running brand,
athletic, green and dark, that "has to feel alive". Bars offered: Nike's current running campaign page, On
Running's homepage, Gymshark's product landing page. The user picks Nike and selects CI, a hosted demo, and
README evidence.

```text
Complete a landing page in the existing GitHub repository for a running brand, for a young audience that runs, within the current site's stack and hosting. Compare the result against Nike's current running campaign page on visual impact and interaction quality, using screenshots captured today at desktop 1440px and mobile 390px. Inspect the real reference first. Required checks and selected delivery outputs are: the repository's test workflow passes on the reviewed commit; the hosted demo serves the reviewed build and is linked from the README; a real screenshot in the README; desktop and mobile controls, keyboard use, and reduced-motion behavior all work. Reuse existing authorization and project constraints. Task class is code-feature; features enabled are evidence_ladder, delegates, isolation and blinding.

Difficulty is medium because the page is new, the motion work is novel here, and three surfaces must agree; required checks are deterministic for CI and judgment for the visual comparison. Use the lightest topology whose gate is met: this one needs a lead/builder with a separate critic in fresh context, because the comparison is judgment, and delegates for the independent pieces, so the topology is compact+delegates. Break the work into pieces that can be judged alone: hero, motion, type, colour, imagery, mobile. Delegate independent pieces and serialize dependencies; one writer per shared surface, one owner for the browser session. Builders may run focused tests and formatters in isolation; the critic opens the real page and puts our capture beside Nike's with labels stripped. Inherit the configured models and record actual assignments where observable.

Each verdict carries candidate identity, reference snapshot, criteria version, winner ours/bar/none, the biggest gap, all blocking findings, each check as passed/failed/blocked/not selected/not applicable, any HOLD, and concrete evidence. Class every finding deterministic, external, or judgment; from a piece's third review round on, an uncorroborated judgment finding is advisory and cannot force a revision or block acceptance. Compare each revision against the retained best and name drift. Acceptance requires ours to win, every applicable required check to pass, and no blocking HOLD.

Budget: 6 reviews per piece, hard stop at 9; 24 shared, hard stop at 30, with the last 6 reserved for integration and handoff; 120/180 observable requests per piece and 480/600 per run where they are observable. All workers share one ledger; splitting or resuming does not refill it. At soft limits converge; at hard limits park the piece with its gap, never as passed.

After two repeated unresolved-gap verdicts, diagnose before editing. Checkpoint after each verdict with identities, obligations, holds, owners, next action, and remaining budget; after any pause, record a resume validation decision before dispatching. Keep a readable progress file. Independently verify the integrated page and the hosted surface against the reviewed commit. At acceptance, deliver the repository, demo, and download links that were selected, record anything parked, stop workers, and leave a resumable handoff.
```

**Nonsoftware goal.** The user asks for a 2000-word explainer on vector databases for non-engineers. Bars offered:
a named Stripe engineering explainer, a named Julia Evans post, the Wikipedia article plus a comprehension test.
The user picks the Julia Evans post.

```text
Complete a 2000-word explainer on vector databases for readers who are smart but not engineers, within one document and no code samples longer than five lines. Compare the result against Julia Evans' post on how databases work on how fast a non-engineer reaches an accurate mental model, using the published post as retrieved today, same length band and format. Inspect the real reference first. Required checks are: every claim traceable to a named source; no unexplained jargon on first use; three named misconceptions addressed; a non-engineer reader can state what a vector database is for after one read. Reuse existing authorization and project constraints. Task class is writing; features enabled are evidence_ladder, delegates and blinding.

Difficulty is medium because the audience gap is wide and the topic invites jargon; required checks are judgment except the source trace, which is deterministic. Use a lead/writer with a separate critic in fresh context, delegating the sections, so the topology is compact+delegates; the comparison is judgment, which is what rules out light. Break the work into the opening, each explanation, the analogies, and the ending, and judge each alone. One writer per section, who may check sources and read the draft aloud before handing it over; that is the writer's own feedback, not acceptance. The critic reads ours and the reference with bylines stripped. Inherit the configured models and record actual assignments where observable.

Each verdict carries candidate identity, reference snapshot, criteria version, winner ours/bar/none, the biggest gap, all blocking findings, each check as passed/failed/blocked/not selected/not applicable, any HOLD, and concrete evidence. Class every finding deterministic, external, or judgment; from the third review round on, an uncorroborated judgment finding is advisory. Compare each revision against the retained best and name added hedging or lost clarity as drift. Acceptance requires ours to win, every applicable required check to pass, and no blocking HOLD.

Budget: 6 reviews per piece, hard stop at 9; 24 shared, hard stop at 30, last 6 reserved; 120/180 and 480/600 observable requests where observable. Splitting or resuming does not refill the ledger. At hard limits park the piece with its gap.

After two repeated unresolved-gap verdicts, diagnose before editing. Checkpoint after each verdict; after any pause, record a resume validation decision before dispatching. Keep a readable progress file. Independently verify the assembled document end to end, not only the sections. At acceptance, deliver the document and the source list, record anything parked, and stop workers.
```

## What breaks a gauntlet loop

- **A vague bar.** The critic invents a comparison and approves everything. Every other item on this list is
  survivable; this one makes the whole loop decorative.
- **The builder judging its own work.** The critic is a separate agent with fresh context, and it should not know
  how hard the builder tried.
- **A soft critic.** Give it a job it can fail the candidate on: which is better, ours or the bar, and `none` for a tie,
  inadequate evidence, a comparison that cannot be made, or judgments that stay in conflict. Scores out of ten drift upward every round.
- **A named exit after N rounds.** The exit is winning the comparison, or the user stopping the run. A budget
  parks a piece as incomplete; it never turns a loss into done.
- **No budget.** One piece that never converges eats the day and the quota while the rest of the work waits.
- **Topology creep.** Adding roles because the roles exist. Compact is the default; a larger topology has to solve
  a coordination need.
- **Over-specifying.** Every extra instruction is one fewer decision the agent makes with its own judgment.
- **A polished but undelivered project.** A local workflow file, a green run for an older commit, a stale hosted
  demo, or a README screenshot hiding the real product is not delivery evidence.
- **Tests derived only from the implementation.** Removing a supported case must not remove its own test. Keep
  independent expectations and show that a representative regression would fail.
- **Generic gates replacing project judgment.** Apply checks to real user journeys and supported platforms. Do not
  invent infrastructure for unrelated work, or call an inconvenient requirement not applicable.
- **Two builders, one file.** Parallel builders without isolation overwrite each other, and the critic judges a
  merge accident.
- **Silent substitution.** A lane that swaps in a different model for an assigned role produces a report nobody
  asked for; an unavailable explicitly assigned model is a blocker.
- **Unrecorded runs.** A run without a record leaves no evidence for the next decision, so the next decision is
  made by anecdote.
- **Changing two things at once.** A new harness and a new method in the same run cannot tell you which helped.
