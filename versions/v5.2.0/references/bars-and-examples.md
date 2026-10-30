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

Both carry the includes in [prompt drafting](prompt-drafting.md). They exceed its length target to preserve
message continuity and reconsideration alongside acceptance and budget rules. Adapt and compress for the task.

**Visual software goal.** The user asks for a landing page in their GitHub repository for a running brand,
athletic, green and dark, that "has to feel alive". Bars offered: Nike's current running campaign page, On
Running's homepage, Gymshark's product landing page. The user picks Nike and selects CI, a hosted demo, and
README evidence.

```text
Build a running-brand landing page for young runners in the existing repository, stack and hosting. Compare the result against Nike's running campaign page on visual impact and interactions: inspect it and capture today's 1440px/390px views. Required: tests on the reviewed commit; hosted demo serving that build, linked from README with a real screenshot; working desktop/mobile controls, keyboard and reduced motion. Reuse authorization and constraints. Task class is code-feature; features enabled are evidence_ladder, delegates, isolation and blinding.

Difficulty is medium: new motion and three delivery surfaces; checks are deterministic for CI and judgment for visuals. Use compact+delegates: lead/builder, separate fresh-context critic and bounded independent workers. Assign hero, motion, typography and mobile work by dependencies; one writer per surface and one browser owner. Builders may run focused tests and formatters in isolation. The critic inspects the real page and label-stripped captures beside the reference. Inherit the configured models; record observed assignments.

Each verdict records artifact/reference/check identities, winner ours/bar/none, biggest gap, blocking findings, check statuses (passed/failed/blocked/not selected/not applicable), HOLDs and evidence. Class findings deterministic, external, or judgment; from round three uncorroborated critic judgment is advisory. Compare against the retained best and report drift. Accept only ours with all required checks passing and no blocking HOLD.

Budget: soft/hard 6/9 reviews per piece, 24/30 shared; 120/180 observable requests per piece, 480/600 shared. Reserve the last 6 reviews and 120 requests for integration. Account for all workers, disclose unknown usage, converge at soft limits and park incomplete work at hard limits. Splits/resumes do not refill allowances.

Keep unfinished objectives when new messages arrive: honor stops immediately, including affected workers and pending external actions; stopping is not rollback. Apply invalidating corrections before affected work, notify workers and check delayed results. Briefly answer questions, retain/delegate additions and resume. Conceptual dissatisfaction triggers reconsideration before further affected edits, without waiting for two verdicts, even if checks pass; ordinary defects get ordinary fixes. Preserve constraints and valid work. Get independent interpretations when useful/available before comparing concrete examples and actual trade-offs; retain dissent, do not vote. Disclose missing capabilities; use visuals when helpful. Act on settled choices; for consequential unresolved priorities, offer concrete options and a recommendation while independent preparation continues. Ground changed checks in requirements and verified facts, not a desired failure. Version changes without resetting lineage/budgets. User instructions are not advisory criticism; discussion is not independent acceptance. Report intended actions separately from confirmed effects.

After two repeated unresolved-gap verdicts, diagnose before editing. Checkpoint after each verdict with identities, obligations, holds, owners, next action, and remaining budget; after any pause, record a resume validation decision before dispatching. Keep a readable progress file. Independently verify the integrated page and the hosted surface against the reviewed commit. At acceptance, deliver the repository, demo, and download links that were selected, record anything parked, stop workers, and leave a resumable handoff.
```

**Nonsoftware goal.** The user asks for a 2000-word explainer on vector databases for non-engineers. Bars offered:
a named Stripe engineering explainer, a named Julia Evans post, the Wikipedia article plus a comprehension test.
The user picks the Julia Evans post.

```text
Write a 2000-word vector-database explainer for non-engineers; code samples at most five lines. Compare the result against Julia Evans' post on how databases work on speed to an accurate mental model. Inspect today's retrieved post under comparable length/format conditions. Required: named sources for claims, jargon explained on first use, three named misconceptions addressed, and a non-engineer can explain the purpose after one read. Reuse authorization and constraints. Task class is writing; features enabled are evidence_ladder, delegates and blinding.

Difficulty is medium: audience translation and jargon risks. Checks are judgment except deterministic source traces. Use compact+delegates: lead/writer, separate fresh-context critic and bounded section writers, one owner each. Writers may verify sources; their own feedback is not acceptance. The critic compares byline-stripped drafts with the reference. Inherit the configured models; record observed assignments.

Each verdict records artifact/reference/check identities, winner ours/bar/none, biggest gap, blocking findings, check statuses (passed/failed/blocked/not selected/not applicable), HOLDs and evidence. Class findings deterministic, external, or judgment; from round three uncorroborated critic judgment is advisory. Compare against the retained best and report drift. Accept only ours with all required checks passing and no blocking HOLD.

Budget: soft/hard 6/9 reviews per piece, 24/30 shared; 120/180 observable requests per piece, 480/600 shared. Reserve the last 6 reviews and 120 requests for integration. Account for all workers, disclose unknown usage, converge at soft limits and park incomplete work at hard limits. Splits/resumes do not refill allowances.

Keep unfinished objectives when new messages arrive: honor stops immediately, including affected workers and pending external actions; stopping is not rollback. Apply invalidating corrections before affected work, notify workers and check delayed results. Briefly answer questions, retain/delegate additions and resume. Conceptual dissatisfaction triggers reconsideration before further affected edits, without waiting for two verdicts, even if checks pass; ordinary defects get ordinary fixes. Preserve constraints and valid work. Get independent interpretations when useful/available before comparing concrete examples and actual trade-offs; retain dissent, do not vote. Disclose missing capabilities; use visuals when helpful. Act on settled choices; for consequential unresolved priorities, offer concrete options and a recommendation while independent preparation continues. Ground changed checks in requirements and verified facts, not a desired failure. Version changes without resetting lineage/budgets. User instructions are not advisory criticism; discussion is not independent acceptance. Report intended actions separately from confirmed effects.

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
