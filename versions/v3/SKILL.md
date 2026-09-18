---
name: gauntlet-loop
description: Draft or run gauntlet loops for building, writing, code, research, or design using a real reference, independent builders and critics, a fixed verdict record, a default runaway budget, and evidence-backed acceptance. Solo tier by default; team tier, governed shared knowledge, and auditable agent-language experiments are opt-in. Records every run so workflows and models can be compared. Triggers on "$gauntlet-loop", "/gauntlet-loop", "gauntlet loop", "gauntlet this", "make a gauntlet prompt", or "loop until it beats X".
---

# Gauntlet Loop (v3)

Normally, give back ONE short prompt the user can paste into a fresh agent session. If the user has already asked you to run, build, fix, or continue the gauntlet, act as the lead and execute it; do not repeat the offer or ask again for authorization already given.

## Flow

1. **Read the goal.** One line restatement in your head, not on screen.
2. **Set the bar.** Use a supplied or previously accepted reference. If none is established, offer **2 or 3 candidate bars**, one line each, and wait for their pick. The definition of done can optionally be extended with relevant delivery and project-specific checks below; make the selected scope clear.
3. **Fix the tier, roles and budget.** Solo tier unless the user asked for the team tier or a selected delivery gate needs it. Name the harness and the model for each role if the user or project has set them; otherwise leave the roles open and say so. Use the default budget unless the user named one.
4. **Write the prompt.** One block, paste-ready, no preamble, no headings inside it, no narration after it.
5. **Offer to run it.** One flat line under the prompt: "I can run this here." Not a question.

If they say run it, you become the lead agent and follow the prompt you just wrote.

## Tiers

**Solo (default).** One lead that plans and builds, one separate critic per piece with fresh context, the verdict record, the budget, the stopping record, and the run log. This is the whole loop for writing, visual work, research, and bounded code pieces. Most runs never need more.

**Team (opt-in).** Two solvers, four whistleblower responsibilities, a reference researcher, and a final reviewer, run in waves within available slots. Use it only when the user says "team gauntlet" or "full setup", or when a selected delivery gate cannot be met by one writer. Before a team run, read [references/team-method.md](references/team-method.md): purpose before controls, one writer per file, one owner of a live browser, independent critique, causal fixes, scoped evidence, and a useful stopping record.

The lead does not upgrade a solo run to the team tier on its own judgment. It may propose the upgrade once, with the reason, and continue solo until the user answers. Role count is not agent count; repeated agreement is not independent evidence; a committee is not a quality gate.

In the team tier, treat messages and shared memory as a **social substrate**: ideas, mistakes and corrections spread through them. Use the reference's knowledge-admission, challenge and correction rules. A passing scorer or a popular claim cannot rewrite the user's goal. A whistleblower must have a route to place an affected acceptance decision on HOLD; the lead must resolve the evidence instead of merely collecting complaints. These are coordination rules, not new system authority or permission to change external access.

The agent-language experiment ([references/agent-language.md](references/agent-language.md)) is off unless the user names it in the goal. It is never on in a run whose purpose is to compare workflows or models, unless the pilot is the thing being compared. Its research grounding and limits are in [references/research-basis.md](references/research-basis.md); installing or invoking it does not establish that a language evolved or that productivity improved. Keep messages legible, with inline plain-language meaning; never optimize for human incomprehensibility or use a dialect to evade review.

## Roles, models and harness

Three roles carry the loop and they want different models. The **lead** plans, decomposes, dispatches and accepts; it needs the strongest judgment available. The **critic** reads a piece and the bar and decides; it needs a strong reviewer and it runs every round, so its price is the price of the loop. The **builder** types; it needs the cheapest model that clears the critic on this kind of piece, because a weaker builder costs rounds, not final quality, as long as the exit stays "the critic picks ours." Cheap builders lose long-context recall first; keep their pieces small and their context to the piece and the bar.

State the harness and the model per role in the prompt when they are known, and which quota each consumes. A run that changes harness and method at the same time cannot tell you which one helped; change one thing per run. Never let a lane silently substitute a different model for an assigned role; an unavailable model is a recorded blocker for that piece, not a quiet fallback.

Example mapping as of September 2026, to be replaced by measurement: lead on Claude Fable 5.1 at high or max effort; critic on Claude Opus 5; builder on GPT-5.6 Luna for bounded code pieces and on Opus 5 where a piece needs the whole repository in view. Vendor benchmark numbers run 4 to 16 points above independent harness results; measure builders on your own pieces with the blind critic before trusting a price.

## Budget

Every piece has a budget by default. Unless the user names one: **soft limit 6 critic rounds or 120 model requests per piece, whichever comes first; hard stop at 1.5×.** At the soft limit the builder wraps up the current attempt and the critic judges what exists. At the hard stop the piece is parked as **blocked (budget)** with the biggest remaining gap and its evidence recorded, and work moves to other pieces or to the stopping milestone.

A budget stop is not an exit and never a pass. A parked piece stays unwon in the stopping record; it can be resumed with a larger budget, a smaller piece, a different builder, or a changed bar. The loop's only exit remains winning the comparison and passing the agreed checks, or the user stopping the run. The budget exists so one piece cannot eat the day or the plan quota while the rest of the work waits.

Honor user pauses and usage constraints. At the agreed stopping milestone, record delivered and unverified work, parked pieces with their gaps, the next concrete step, evidence and active ownership; stop workers and schedule nothing unless requested. Do not turn an instruction to add backlog notes into implementation.

## Verdict record

The critic's output is a record, not a review. Prose may follow it, but the record is what the lead reads and what goes on the progress page:

```
piece: <name>
winner: ours | bar | none
biggest_gap: <one sentence, in the loser>
checks: <name>: passed | failed | blocked | not selected | not applicable  (one per agreed check)
hold: no | yes — <reason>
evidence: <paths, URLs, command output, screenshot files>
round: <n> of budget <soft>/<hard>
```

`winner` is binary against the bar; scores out of 10 drift upward every round and are not used. `checks` are verified independently by the critic, not read from the builder's report. `hold` is any critic's route to stop acceptance until the underlying evidence is resolved. A verdict without evidence paths is not a verdict. Never label a non-blind comparison blind.

For a high-stakes piece the user may ask for two or three critics with fresh context and a majority; do not add critics without being asked. The critic sees the piece, the bar, and the agreed checks. It does not see the builder's transcript or how hard the builder tried.

## Isolation

When builders run in parallel on pieces that touch the same files, each builder works in its own worktree or workspace clone and returns a patch or branch; the lead merges and then runs the checks once across the union of changed files. Sequential work keeps one writer per file and one owner of any live browser. If the harness offers no isolation, serialize the overlapping pieces and say so; do not let two builders write the same file.

Builders do not run the project's gates or formatters; they edit. The lead or the critic verifies. This avoids racing formatters and keeps the builder's context small.

## Run log

Every run appends one record at the stopping milestone (or a hook writes it) so workflows and models can be compared later instead of argued about:

```
date, task_id, workflow: gauntlet-loop v3, tier: solo|team, harness, models per role (with effort),
pieces, rounds per piece, pieces won / parked (budget) / blocked, wall time,
tokens in/out, cost (API-equivalent) and plan quota consumed if on a subscription,
critic verdicts summary, blockers, defects found in the next 7 days (filled in later)
```

Keep it in the project under `gauntlet/runs.jsonl` or the project's equivalent. A run without a record produced no evidence for the next decision. To compare this workflow against another, or one model against another, change one thing per arm, use the same frozen tasks, and let a fresh critic that saw none of the runs judge blind.

## Optional extensions to done

For software repositories, apps, sites, extensions, or demos, read [references/software-quality.md](references/software-quality.md) before drafting or running the loop. It provides optional completion checks and explains how to adapt them to the actual project. The user can select any relevant subset; reuse selections and requirements already established in the task or repository. Otherwise present relevant additions as options, not silent new requirements or blockers. Do not ask again when the selection is already clear.

Possible extensions for a GitHub project with a browser UI are: a committed and uploaded testing workflow with a successful run on the reviewed commit; a working hosted demo at the approved audience; a useful synthetic demo with guided and manual exploration, reset, and recoverable failures; a portable offline download where appropriate; a clean public release boundary; a README linking the demo and showing a real screenshot; clear installation, update/reload, and troubleshooting instructions; and regressions for the project's actual user journeys and failure boundaries. These additions are independently selectable. A separate public working copy can preserve private data and local history when needed; it is not a required repository layout. When CI is selected and both extension and demo exist, it must exercise both. Reuse existing CI and hosting where they meet the selected bar. Include selected outcomes in the generated prompt so it works in a fresh session without this skill; omit unselected extras or clearly label them optional.

Derive project-specific checks from the user's goal, repository instructions, supported platforms, reported bugs, and reference behavior. State what observable evidence will prove each selected or otherwise required check. Distinguish **passed**, **failed**, **blocked**, **not selected**, and **not applicable**. Once an extension to done is selected, it is a completion requirement: missing permissions make it blocked, not passed or silently deselected. A purely nonsoftware deliverable does not need a repository, CI, or hosted demo just because this skill is used.

The lead builds; separate critics review the actual artifacts and evidence. A visual win cannot compensate for a failing selected or otherwise required check. Use blind comparison where a meaningful blind comparison is possible, and objective independent checks for functional requirements. Do not declare SHIP until the agreed gates pass and the comparison supports it; report exact remaining blockers otherwise.

## Final delivery format

After executing a software gauntlet with delivery outputs, put verified links in this order: **repository, live demo, offline download**. Lead with the repository and a short description of what it contains, then list the demo and download. For example:

```markdown
[GitHub repository](VERIFIED_REPOSITORY_URL) — README with actual screenshots, setup, architecture, and roadmap.

1. [Live demo](VERIFIED_DEMO_URL)
2. [Offline download](VERIFIED_DOWNLOAD_URL)

VERIFIED_RESULTS_WITH_SCOPE_AND_CI_RUN_LINK_IF_SELECTED

PARKED_PIECES_WITH_BIGGEST_GAP_IF_ANY

REMAINING_BLOCKER_OR_LIMITATION_IF_ANY
```

Replace every example field and describe only documentation and evidence that actually exist. Omit unavailable or unselected links; explain a blocked selected delivery below the available links. Never invent a URL or imply that a relative HTML source link is a running demo. Preserve the order of whichever links remain. Report local tests, exact-commit CI, and live/offline checks distinctly; recheck a previously missing permission before repeating it as a current blocker. Keep any real limitation in a separate final paragraph. This format does not change prompt-only output or require software delivery for a nonsoftware task.

## The bar is the whole trick

Everything else in a gauntlet loop is scaffolding. The loop only produces quality if the thing it compares against is real.

A bar has to pass three tests:

- **Named.** A specific thing, not a category. "Stripe's pricing page" works. "Award-winning SaaS sites" does not.
- **Fetchable.** The critic can actually get it - screenshot the live page, read the published piece, run the binary, open the repo, watch the footage. If the agent cannot obtain it, it will hallucinate the comparison.
- **Comparable.** Both can sit side by side and a judge can pick one. If you cannot imagine the A/B, it is not a bar.

Bars by goal type:

| Goal | Bar that works |
|---|---|
| Website, app, UI | The live site of a specific best-in-class product, screenshotted at the same viewport |
| Game, 3D, visual | Real footage or screenshots from a named shipped title |
| Writing | A specific published piece by a named author or publication, same length and format |
| Code, tooling | A named repo's implementation, plus its benchmark or test suite as the measurable half |
| Research, analysis | A named analyst report or a paper's methods section, judged on rigour and coverage |
| Deck, doc, deliverable | A real artifact from a firm known for it, same page count |
| A workflow or a model | The incumbent, measured on the same frozen tasks, judged by a critic that saw neither run |

When you propose bars, prefer the hardest one the agent can genuinely reach. A bar that is too easy makes the loop exit on round one.

If the goal has a measurable half (load time, token cost, benchmark score, word count, pass rate), name it alongside the reference. Taste plus a number beats taste alone.

## Prompt template

Adapt the wording every time. Fill the brackets, keep it short, keep the last lines.

```
Build [GOAL].

The bar is [BAR]. Get the real thing first and compare against it directly, not against a description of it.

[Harness and models per role if known: lead on X, critic on Y, builders on Z. Insert selected extensions to done and concrete project-specific checks here, if any. Omit unselected extras or label them optional.]

Break this into the smallest pieces that can be improved and judged on their own. For each piece, fan out a builder and a separate critic with fresh context. The critic inspects the actual output, compares against the real reference blind where meaningful, independently verifies the acceptance checks, and returns a verdict record: winner ours or bar, the single biggest remaining gap, each check as passed, failed, blocked, not selected or not applicable, any hold, and the evidence. Then it goes back to the builder.

Each piece has a budget: soft [6 rounds or 120 requests], hard stop at 1.5×. At the hard stop the piece is parked as blocked with its gap recorded; it never passes because the budget ran out.

Builders that touch the same files work in separate worktrees and return patches; the lead merges and runs the checks once. One writer per file otherwise. Any critic can flag an acceptance HOLD; resolve the underlying evidence before shipping.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep fixing and rejudging until the comparison wins and every agreed acceptance check passes. Record genuine external blockers instead of claiming a pass.

Keep a live progress page updating as the work evolves so I can watch it. At the stopping milestone, append the run record: pieces won and parked, rounds, time, tokens, cost and quota, blockers.

Run builders and critics in parallel where independent work exists, in waves within available slots. Honor the user's stopping milestone and save a resumable status.
```

Rules for what you fill in:

- Bake the bar in as a concrete, fetchable thing. URL, product name, repo, title.
- Name harness and models per role when the user or project has set them; otherwise leave the roles open and say the run should record what it used.
- Keep the default budget line unless the user named a budget or a cost ceiling; then use theirs. Express a budget in rounds or requests per piece, never as a round count after which the piece is "done."
- Include selected CI, demo interaction/portability, hosted demo, public-release boundary, README evidence, installation/update, and project-specific extensions. Selection makes them required outcomes, not a prescribed stack or architecture. For software delivery, include a compact instruction to end with verified repository, demo, and offline-download links in that order, followed by scoped verification, parked pieces and remaining blockers; omit links outside the selected scope. Do not silently turn optional additions into requirements. Replace every bracketed instruction before returning the prompt.
- Add tool names only if the goal needs them (image or video generation, a browser, a deploy target).
- Leave implementation choices open unless the user or project constrains them. No invented architecture, decomposition, or stack choice. The acceptance bar specifies what must work and how it will be judged.
- Include team responsibilities only when the team tier is selected, and any language pilot only when the user named it, at the detail the task needs. If a portable prompt selects the pilot, include a versioned glossary/grammar, inline translations, independent decoding and matched plain-language comparison; do not rely on access to this skill's references in the new session. Preserve normal task success and explicit action boundaries.

## Length and voice

Keep prompts concise: usually 150 to 220 words for solo work, with room for roughly 250 to 350 words when concrete software delivery gates or the team tier need it. Do not drop required outcomes to meet a word count or paste the entire reference checklist into every prompt.

Plain sentences. No bullet lists inside the prompt. It should read like someone telling an agent what perfect looks like and refusing to accept less.

## Portability

In Codex, invoke this skill with `$gauntlet-loop` followed by the goal. The template and examples use plain-language looping and subagent instructions. Do not emit `/loop` or `ultracode` as Codex commands.

In Claude Code, the same prompt works as written; `/loop` and `ultracode` may be appended when the user wants self-paced reruns or multi-agent orchestration, and worktrees provide the isolation. In oh-my-pi, run the builder and critic chain inside `workflowz` with the verdict record as the critic's output schema and the harness `budget` as the hard stop. For any other agent, adapt orchestration wording only to capabilities actually available there. If separate subagents, isolation, or the real reference are unavailable, report that blocker; do not pretend an independent blind comparison ran.

Cross-vendor builders (a cheaper model from another provider) need a lane the harness supports: a role mapping in oh-my-pi, a custom agent behind a router in Codex, or a headless CLI called from a Claude Code subagent. Keep the lead and the critic on one harness; only builders move.

## Two filled examples

**Visual software goal, solo tier.** User: "landing page in my GitHub repo for my running brand, athletic, green and dark, has to feel alive."

Bars offered: A) Nike's current running campaign page B) On Running's homepage C) Gymshark's product landing page. User picks A and selects the CI, hosted demo, README evidence, and usability extensions to done.

```
Build a landing page in the existing GitHub repository for a running brand. Athletic, peak performance, green and dark, energetic, aimed at a young healthy audience. It needs to be interactive and visually unmistakable.

The bar is Nike's current running campaign page. Screenshot it at desktop and mobile and compare against those directly, not against a description of them.

The delivery bar also requires a GitHub testing workflow that passes on the reviewed commit, a working hosted demo at the approved audience linked from the README, an actual screenshot in the README, and clear run/update instructions. Test the real desktop/mobile controls, keyboard use, and reduced-motion behavior; verify that the published page matches the tested build. Reuse the project's approved hosting and record evidence for every gate.

Break this into the smallest pieces that can be improved and judged on their own - hero, motion, type, colour, imagery, interaction, mobile. For each piece, fan out a builder and a separate critic with fresh context. The critic opens the real page in a browser, puts our screenshot next to Nike's blind with the labels stripped, and returns a verdict record: which is better, the single biggest remaining gap, each delivery check as passed, failed or blocked, any hold, and the evidence. Then it goes back to the builder.

Each piece has a budget of six rounds, hard stop at nine; a piece that hits it is parked as blocked with its gap, never passed. Builders touching the same files work in separate worktrees and return patches.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep looping until the critic picks ours in the visual comparison and every agreed delivery check passes. Record exact evidence and any genuine external blocker; do not claim a blocked gate passed.

Keep a live progress page updating as the work evolves so I can watch it, and append the run record at the stopping milestone. Run builders and critics as parallel subagents where independent work exists. Honor a user pause and save the milestone status.
```

**Nonsoftware goal, solo tier.** User: "a 2000-word explainer on vector databases for non-engineers."

Bars offered: A) a specific Stripe engineering blog explainer B) a named Julia Evans post C) the Wikipedia article plus a comprehension test. User picks B.

```
Write a 2000-word explainer on vector databases for readers who are smart but not engineers.

The bar is Julia Evans' writing on hard technical topics. Pull three of her actual posts and compare against them directly, not against a description of her style.

Break this into the smallest pieces that can be judged on their own - the opening, each explanation, the diagrams, the analogies, the ending. For each piece, fan out a writer and a separate critic with fresh context. The critic reads ours and hers blind with the bylines stripped and returns a verdict record: which one a non-engineer would understand faster, the single biggest remaining gap, and the evidence. Then it goes back to the writer.

Each piece has a budget of six rounds, hard stop at nine; a piece that hits it is parked with its gap, never passed.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep looping on each piece until the critic picks ours blind or the user pauses the work. Preserve scoped evidence and a resumption note, and append the run record at the stopping milestone.

Keep a live progress page updating as the work evolves so I can watch it. Run writers and critics as parallel subagents where independent work exists. Honor a user pause and save the milestone status.
```

## What breaks a gauntlet loop

- **A vague bar.** The critic invents a comparison and approves everything. Most common failure by far.
- **The builder judging its own work.** The critic must be a separate agent with fresh context. It should not know how hard the builder tried.
- **A soft critic.** Say "harsh" in the prompt and give it a binary job: which one is better, A or B. Scores out of 10 drift upward every round.
- **Named exit after N rounds.** The exit is winning the comparison, or the user stopping the run. A budget parks a piece as blocked; it never turns a loss into "done."
- **No budget.** One piece that never converges eats the day and the plan quota while the rest of the work waits.
- **Tier creep.** Adding solvers, reviewers and whistleblowers because the roles exist. Solo is the default; the team tier is asked for, not assumed.
- **Over-specifying.** Every extra instruction is one fewer decision the agent makes with its own judgment. Minimal wins.
- **A polished but undelivered project.** A local workflow file, a green run for an older commit, a stale hosted demo, or a README screenshot that hides the actual product is not delivery evidence.
- **Tests derived only from the implementation.** Removing a supported case must not remove its own test. Keep independent expectations and prove a representative regression would fail.
- **Generic gates replacing project judgment.** Apply checks to real user journeys and supported platforms. Do not invent infrastructure for unrelated work or call an inconvenient requirement not applicable.
- **Two builders, one file.** Parallel builders without isolation overwrite each other and the critic judges a merge accident.
- **Silent substitution.** A lane that swaps in a different model for an assigned role produces a report nobody asked for; an unavailable model is a blocker.
- **Unrecorded runs.** A run without a record leaves no evidence for the next workflow or model decision, and the next decision is made by anecdote.
- **Changing two things at once.** A new harness and a new method in the same run cannot tell you which one helped.
