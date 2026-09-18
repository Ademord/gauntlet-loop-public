---
name: gauntlet-loop
description: Draft or run gauntlet loops for building, writing, code, research, or design using a real reference, independent builders and critics, and evidence-backed acceptance. Supports purpose-first teamwork, governed shared knowledge, and optional auditable agent-language experiments. Triggers on "$gauntlet-loop", "/gauntlet-loop", "gauntlet loop", "gauntlet this", "make a gauntlet prompt", or "loop until it beats X".
---

# Gauntlet Loop

Normally, give back ONE short prompt the user can paste into a fresh agent session. If the user has already asked you to run, build, fix, or continue the gauntlet, act as the lead and execute it; do not repeat the offer or ask again for authorization already given.

## Flow

1. **Read the goal.** One line restatement in your head, not on screen.
2. **Set the bar.** Use a supplied or previously accepted reference. If none is established, offer **2 or 3 candidate bars**, one line each, and wait for their pick. The definition of done can optionally be extended with relevant delivery and project-specific checks below; make the selected scope clear.
3. **Write the prompt.** One block, paste-ready, no preamble, no headings inside it, no narration after it.
4. **Offer to run it.** One flat line under the prompt: "I can run this here." Not a question.

If they say run it, you become the lead agent and follow the prompt you just wrote.

## Executing with a team

Before a substantive team run, read [references/team-method.md](references/team-method.md). It generalizes the method of an earlier private project: purpose before controls, one writer per file, one owner of a live browser, independent critique, causal fixes, scoped evidence, and a useful stopping record. Small edits need only the relevant parts; do not manufacture a committee or testing campaign.

Treat messages and shared memory as a **social substrate**: ideas, mistakes and corrections can all spread through them. Use the reference's lightweight knowledge-admission, challenge and correction rules. A passing scorer or a popular claim cannot rewrite the user's goal. A whistleblower must have a route to place an affected acceptance decision on HOLD; the lead must resolve the evidence instead of merely collecting complaints. These are coordination rules, not new system authority or permission to change external access.

Use two solvers, four whistleblower responsibilities, a reference researcher and a final reviewer when the user requests the full setup or the task benefits from it. Run responsibilities in waves within available slots; smaller work needs fewer agents. Do not equate role count with simultaneous agents, or repeated agreement with independent evidence.

For a requested agent-language experiment, or a concrete repeated communication bottleneck worth testing, read [references/agent-language.md](references/agent-language.md). Agents may propose and evolve a task-specific compositional shorthand, retaining its grammar, glossary, translations and evaluation results in project methodology. Keep messages legible, with inline plain-language meaning. Never optimize for human incomprehensibility or use a dialect to evade review. The pilot is optional; normal work continues in plain language when it adds no measured value.

The research grounding and its limits are in [references/research-basis.md](references/research-basis.md). This extension implements an auditable experiment procedure; installing or invoking it does not establish that a language evolved or that productivity improved. Project lessons remain project proposals until reviewed; a run must not silently rewrite this installed skill or its own authority.

Honor user pauses and usage constraints. At the agreed stopping milestone, record delivered and unverified work, the next concrete step, evidence and active ownership; stop workers and schedule nothing unless requested. Do not turn an instruction to add backlog notes into implementation.

## Optional extensions to done

For software repositories, apps, sites, extensions, or demos, read [references/software-quality.md](references/software-quality.md) before drafting or running the loop. It provides optional completion checks and explains how to adapt them to the actual project. The user can select any relevant subset; reuse selections and requirements already established in the task or repository. Otherwise present relevant additions as options, not silent new requirements or blockers. Do not ask again when the selection is already clear.

Possible extensions for a GitHub project with a browser UI are: a committed and uploaded testing workflow with a successful run on the reviewed commit; a working hosted demo at the approved audience; a useful synthetic demo with guided and manual exploration, reset, and recoverable failures; a portable offline download where appropriate; a clean public release boundary; a README linking the demo and showing a real screenshot; clear installation, update/reload, and troubleshooting instructions; and regressions for the project's actual user journeys and failure boundaries. These additions are independently selectable. A separate public working copy can preserve private data and local history when needed; it is not a required repository layout. When CI is selected and both extension and demo exist, it must exercise both. Reuse existing CI and hosting where they meet the selected bar. Include selected outcomes in the generated prompt so it works in a fresh session without this skill; omit unselected extras or clearly label them optional.

Derive project-specific checks from the user's goal, repository instructions, supported platforms, reported bugs, and reference behavior. State what observable evidence will prove each selected or otherwise required check. Distinguish **passed**, **failed**, **blocked**, **not selected**, and **not applicable**. Once an extension to done is selected, it is a completion requirement: missing permissions make it blocked, not passed or silently deselected. A purely nonsoftware deliverable does not need a repository, CI, or hosted demo just because this skill is used.

The lead builds; separate critics review the actual artifacts and evidence. A visual win cannot compensate for a failing selected or otherwise required check. Use blind comparison where a meaningful blind comparison is possible, and objective independent checks for functional requirements. Never label a nonblind review blind. Do not declare SHIP until the agreed gates pass and the comparison supports it; report exact remaining blockers otherwise.

## Final delivery format

After executing a software gauntlet with delivery outputs, put verified links in this order: **repository, live demo, offline download**. Lead with the repository and a short description of what it contains, then list the demo and download. For example:

```markdown
[GitHub repository](VERIFIED_REPOSITORY_URL) — README with actual screenshots, setup, architecture, and roadmap.

1. [Live demo](VERIFIED_DEMO_URL)
2. [Offline download](VERIFIED_DOWNLOAD_URL)

VERIFIED_RESULTS_WITH_SCOPE_AND_CI_RUN_LINK_IF_SELECTED

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

When you propose bars, prefer the hardest one the agent can genuinely reach. A bar that is too easy makes the loop exit on round one.

If the goal has a measurable half (load time, token cost, benchmark score, word count, pass rate), name it alongside the reference. Taste plus a number beats taste alone.

## Prompt template

Adapt the wording every time. Fill the brackets, keep it short, keep the last line.

```
Build [GOAL].

The bar is [BAR]. Get the real thing first and compare against it directly, not against a description of it.

[Insert selected extensions to done and concrete project-specific checks here, if any. Omit unselected extras or label them optional.]

Break this into the smallest pieces that can be improved and judged on their own. For each piece, fan out a builder and a separate critic with fresh context. The critic inspects the actual output, compares against the real reference blind where meaningful, independently verifies the acceptance checks, and names the single biggest remaining gap. Then it goes back to the builder.

Start each piece with the user's task and the cost of the proposed change. Assign one writer per file and one owner of any live browser. Preserve original failures; promote shared findings only with scoped evidence and independent review. Any critic can flag an acceptance HOLD; resolve the underlying evidence before shipping.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep fixing and rejudging until the comparison wins and every agreed acceptance check passes. Compare blind where meaningful; verify functional requirements independently. Record genuine external blockers instead of claiming a pass.

Keep a live progress page updating as the work evolves so I can watch it.

Run builders and critics in parallel where independent work exists, in waves within available slots. Honor the user's stopping milestone and save a resumable status.
```

Rules for what you fill in:

- Bake the bar in as a concrete, fetchable thing. URL, product name, repo, title.
- Include selected CI, demo interaction/portability, hosted demo, public-release boundary, README evidence, installation/update, and project-specific extensions. Selection makes them required outcomes, not a prescribed stack or architecture. For software delivery, include a compact instruction to end with verified repository, demo, and offline-download links in that order, followed by scoped verification and remaining blockers; omit links outside the selected scope. Do not silently turn optional additions into requirements. Replace every bracketed instruction before returning the prompt.
- Add a budget or cost ceiling line **only if the user named one**. No default cap.
- Add tool names only if the goal needs them (image or video generation, a browser, a deploy target).
- Leave implementation choices open unless the user or project constrains them. No invented architecture, decomposition, round count, or stack choice. The acceptance bar specifies what must work and how it will be judged.
- Include team responsibilities and any language pilot only at the detail the task needs. If a portable prompt selects the pilot, include a versioned glossary/grammar, inline translations, independent decoding and matched plain-language comparison; do not rely on access to this skill's references in the new session. Preserve normal task success and explicit action boundaries.

## Length and voice

Keep prompts concise: usually 120 to 180 words for general work, with room for roughly 220 to 320 words when concrete software delivery gates need it. Do not drop required outcomes to meet a word count or paste the entire reference checklist into every prompt.

Plain sentences. No bullet lists inside the prompt. It should read like someone telling an agent what perfect looks like and refusing to accept less.

## Portability

In Codex, invoke this skill with `$gauntlet-loop` followed by the goal. The template and examples use plain-language looping and subagent instructions for Codex. Do not emit `/loop` or `ultracode` as Codex commands.

For another agent, adapt orchestration wording only to capabilities actually available there. If separate subagents or the real reference are unavailable, report that blocker; do not pretend an independent blind comparison ran.

## Two filled examples

**Visual software goal.** User: "landing page in my GitHub repo for my running brand, athletic, green and dark, has to feel alive."

Bars offered: A) Nike's current running campaign page B) On Running's homepage C) Gymshark's product landing page. User picks A and selects the CI, hosted demo, README evidence, and usability extensions to done.

```
Build a landing page in the existing GitHub repository for a running brand. Athletic, peak performance, green and dark, energetic, aimed at a young healthy audience. It needs to be interactive and visually unmistakable.

The bar is Nike's current running campaign page. Screenshot it at desktop and mobile and compare against those directly, not against a description of them.

The delivery bar also requires a GitHub testing workflow that passes on the reviewed commit, a working hosted demo at the approved audience linked from the README, an actual screenshot in the README, and clear run/update instructions. Test the real desktop/mobile controls, keyboard use, and reduced-motion behavior; verify that the published page matches the tested build. Reuse the project's approved hosting and record evidence for every gate.

Break this into the smallest pieces that can be improved and judged on their own - hero, motion, type, colour, imagery, interaction, mobile. For each piece, fan out a builder and a separate critic with fresh context. The critic opens the real page in a browser, puts our screenshot next to Nike's blind with the labels stripped, says which is better, and names the single biggest remaining gap. Then it goes back to the builder.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep looping until the critic picks ours in the visual comparison and every agreed delivery check passes. Record exact evidence and any genuine external blocker; do not claim a blocked gate passed.

Keep a live progress page updating as the work evolves so I can watch it.

Run the builders and critics as parallel subagents where independent work exists, within available slots. Honor a user pause and save the milestone status.
```

**Nonsoftware goal.** User: "a 2000-word explainer on vector databases for non-engineers."

Bars offered: A) a specific Stripe engineering blog explainer B) a named Julia Evans post C) the Wikipedia article plus a comprehension test. User picks B.

```
Write a 2000-word explainer on vector databases for readers who are smart but not engineers.

The bar is Julia Evans' writing on hard technical topics. Pull three of her actual posts and compare against them directly, not against a description of her style.

Break this into the smallest pieces that can be judged on their own - the opening, each explanation, the diagrams, the analogies, the ending. For each piece, fan out a writer and a separate critic with fresh context. The critic reads ours and hers blind with the bylines stripped, says which one a non-engineer would understand faster, and names the single biggest remaining gap. Then it goes back to the writer.

The critic should be a harsh critic. Praise is not useful. If ours does not win, it keeps going.

Keep looping on each piece until the critic picks ours blind or the user pauses the work. Preserve scoped evidence and a useful resumption note.

Keep a live progress page updating as the work evolves so I can watch it.

Run the builders and critics as parallel subagents where independent work exists, within available slots. Honor a user pause and save the milestone status.
```

## What breaks a gauntlet loop

- **A vague bar.** The critic invents a comparison and approves everything. Most common failure by far.
- **The builder judging its own work.** The critic must be a separate agent with fresh context. It should not know how hard the builder tried.
- **A soft critic.** Say "harsh" in the prompt and give it a binary job: which one is better, A or B. Scores out of 10 drift upward every round.
- **Named exit after N rounds.** The exit is winning the comparison, or the user stopping the run. Never a round count.
- **Over-specifying.** Every extra instruction is one fewer decision the agent makes with its own judgment. Minimal wins.
- **A polished but undelivered project.** A local workflow file, a green run for an older commit, a stale hosted demo, or a README screenshot that hides the actual product is not delivery evidence.
- **Tests derived only from the implementation.** Removing a supported case must not remove its own test. Keep independent expectations and prove a representative regression would fail.
- **Generic gates replacing project judgment.** Apply checks to real user journeys and supported platforms. Do not invent infrastructure for unrelated work or call an inconvenient requirement not applicable.
