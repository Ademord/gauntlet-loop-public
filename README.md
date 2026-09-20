# Gauntlet Loop

A skill for coding agents that turns an ambitious goal into a deliverable that survives comparison with a real reference and independent, evidence-based checks. The agent builds, a separate critic with fresh context judges the actual artifact against a concrete bar, and the work is revised until it wins or its budget runs out. Current skill: 5.1.0. This is work in progress: [STATUS.md](STATUS.md) distinguishes verified behavior from unproven performance claims.

The September 20 [measurement correction](research/program/paired-study/measurement-replay.md) preserves the original study and corrects its token totals. The completed [review calibration](research/program/calibration/DECISION.md) found equal frozen scores, plus real repairs and a regression in supplementary checks. It does not benchmark full skill versions or establish a general benefit from orchestration.

## How it works

```mermaid
flowchart TD
    C["Contract<br/>outcome, real reference, frozen checks,<br/>difficulty and topology, budget"] --> B["Build one judgeable increment"]
    B --> R["Independent review<br/>a fresh-context critic inspects the actual artifact"]
    R --> V{"Verdict<br/>winner ours, bar, or none<br/>checks and HOLDs"}
    V -- "evidenced gap" --> F["Fix the cause<br/>keep the best candidate"]
    F --> B
    V -- "ours wins, every check passes,<br/>no blocking HOLD" --> I["Integrate and verify"]
    I --> D["Deliver with evidence"]
    V -- "budget exhausted" --> K["Park the piece<br/>never pass it"]
```

Findings are classed as deterministic, external, or judgment. From a piece's third review round, a judgment alone can no longer force a revision. Every run records its difficulty estimate, topology, reviews, and outcome, so later runs can test where the extra machinery pays.

## Quick start

1. **Install.** Copy [skill/](skill/SKILL.md) into your host's skills directory under the name `gauntlet-loop`, for example `~/.codex/skills/gauntlet-loop` for Codex or `.claude/skills/gauntlet-loop` for Claude Code. Hosts that take a single file or an upload can use [dist/](dist/README.md).
2. **Invoke.** Use `$gauntlet-loop` in Codex, or ask by name: "gauntlet this", "make a gauntlet prompt for ...", "loop until it beats X".
3. **Draft or run.** By default the skill drafts one paste-ready prompt that carries the whole contract. Say "run it" and the agent becomes the lead, with a separate critic.

## How it evolved

| Version | What it was, and what it improved over the previous one (or did not) | Where |
| --- | --- | --- |
| **The technique**<br>2026<br>Matt Shumer | A prompt from the [Claude of Duty](https://github.com/mshumer/Claude-of-Duty) work: a harsh, separate critic compares the work blind against a real, named reference, and the loop does not stop until the work wins. | [robonuggets/gauntlet-loop](https://github.com/robonuggets/gauntlet-loop) |
| **v1**<br>6 Aug 2026<br>Jay E, RoboNuggets<br>CC BY 4.0 | The technique packaged as a reusable skill. The bar must be named, fetchable and comparable; builder and critic are separate agents with fresh context; the verdict is binary; the exit is winning, never a round count. Ships a table of good bars per goal type, two filled examples, and a list of what breaks a loop.<br>**Improved:** the technique became repeatable and portable.<br>**Did not:** no budget, so a loop that never wins never stops; no record of verdicts or evidence; tone ("harsh") is the only quality lever. | [versions/v1](versions/v1/SKILL.md)<br>1 file<br>1,400 words |
| **v1-local**<br>before 9 Sep 2026<br>Franco Ribera<br>unversioned | v1 plus software-delivery checks a user can select: a testing workflow green on the reviewed commit, a hosted demo, an offline download, a clean public copy, a README with a real screenshot, regressions on real user journeys. Adds five check statuses and a fixed delivery format.<br>**Improved:** software work gets a definition of done beyond the critic's preference.<br>**Did not:** still no budget; the skill tripled in size. | [versions/v1-local](versions/v1-local/SKILL.md)<br>2 files<br>4,400 words |
| **v2**<br>9 Sep 2026<br>Franco Ribera | A team tier (two solvers, four challenger roles, a reference researcher, a final reviewer), rules for admitting and correcting shared knowledge, a HOLD any critic can raise to stop an acceptance, a resumable stopping record, and an optional auditable agent-language experiment.<br>**Improved:** multi-agent runs get governance, and one dissenting critic can block a bad acceptance.<br>**Did not:** still no budget; the role roster invites committee growth; checked only by one read-only scenario walkthrough. | [versions/v2](versions/v2/SKILL.md)<br>5 files<br>7,600 words |
| **v3**<br>9 Sep 2026<br>Franco Ribera, after comparing v2 with oh-my-pi | Controls and records rather than new method. Solo by default, team only on request; a per-piece budget (soft limit 6 rounds or 120 requests, hard stop at 1.5 times that) that parks a piece and never passes it; a fixed verdict record; isolated workspaces for parallel builders; no silent model substitution; a run log so workflows can be compared.<br>**Improved:** the first protection against runaway loops and the first comparable run records.<br>**Did not:** added an example model mapping and a claim about vendor benchmarks that were opinions, not measurements; forbade builders from running tests; its four reference files were never shipped with it. | [versions/v3](versions/v3/SKILL.md)<br>1 file<br>4,300 words |
| **v4.0.0**<br>12 Sep 2026<br>Franco Ribera, from ten published sources | A rewrite around evidence. `winner: ours / bar / none` replaces the harsh critic; builders may test locally while acceptance stays independent; verdicts are bound to artifact, reference and criteria identities; shared run budgets with an integration reserve; explicit HOLD dispositions; best-candidate retention; checkpoints and resume; optional environment-probed lessons. The v3 model mapping is removed.<br>**Improved:** acceptance rests on evidence instead of tone, and budgets and recovery are explicit.<br>**Did not:** dropped the bar table, the filled examples, and the list of what breaks a loop that v1 to v3 carried, a loss in teachability nobody measured. | [versions/v4](versions/v4/SKILL.md)<br>8 files<br>9,500 words |
| **v5.0.0**<br>17 Sep 2026<br>Franco Ribera, with a Claude lead and critic agents, from six papers | Every expensive mechanism becomes conditional on what can be verified: evidence classes on findings and a revision ladder, so that from the third review round opinion alone cannot force a revision; a recorded difficulty estimate with a `light` topology for easy, checkable work; a budget for retrieving lessons and a ledger of whether they helped; a resume validation record; completion-time records. Built by running the skill on itself against frozen checks; independent critics found a mechanical deadlock and a series of rule conflicts, all fixed before acceptance.<br>**Improved:** effort goes where evidence exists, and every run records what is needed to test that.<br>**Did not:** nothing shows it beats v4; the examples v4 dropped are still missing (backlog B-020); the entrypoint sits 11 bytes under its 16,000-byte limit. | [skill/](skill/SKILL.md) and [dist/](dist/README.md)<br>8 files<br>12,400 words |
| **v5.1.0**, current<br>19 Sep 2026<br>Franco Ribera, with a Claude lead and four critic agents | No new mechanism. It restores what v4 dropped for size, into a reference read only when a bar is being set, a prompt drafted, or a loop is stalling: bars by goal type, two filled prompts, and the list of what breaks a loop. The rest is wording the v5 run left ambiguous and a gauntlet on v5 itself found: which route wins when a message asks for a prompt about doing work; what `bar` means when the bar is a known-failing artifact, so it can never read as the broken original winning; what a per-piece soft limit means when a small user cap makes soft and hard coincide; a prompt-length target decided by measuring the template instead of guessing; and two milestone fields, task class and features enabled, taken from the vocabulary the run ledger already used rather than a second invented one. **Did not** improve the loop itself, and nothing here is benchmarked. Its first review round returned four verdicts, nine blocking findings, and one defect worth naming: the two fields were required in three places and carried in none, while the package claimed otherwise in writing | [skill/](skill/SKILL.md), [run](gauntlet/v51-upgrade-2026-09-19/progress.md) |

Across these versions the skill grew from about 1,400 to 12,400 words, almost nine times. No version has been benchmarked against the one before it: each was checked by release review, and v5 by independent critics against frozen checks. Whether the growth pays is the question the [research program](research/program/gauntlet-bench-v2-hypothesis.md) is built to answer. Identities, what was preserved byte for byte, how each version was evaluated, and attribution are in [versions/README.md](versions/README.md).

## What is in this repository

| If you want to | Go to |
| --- | --- |
| install or read the current skill | [skill/](skill/SKILL.md), and [dist/](dist/README.md) for the single file and zip |
| see every earlier version, with identities and attribution | [versions/](versions/README.md) |
| understand why v5 is shaped the way it is | [research/thesis/v5-thesis.md](research/thesis/v5-thesis.md) |
| read the paper notes behind a version | [research/scans/](research/scans/README.md) |
| follow or join the research program | [research/program/](research/program/gauntlet-bench-v2-hypothesis.md) and its [backlog](research/program/backlog.md) |
| inspect a complete real run: the one that produced v5 | [gauntlet/](gauntlet/README.md) |
| run the tooling | [tools/](tools/README.md) |
| see what is verified, untested, and next | [STATUS.md](STATUS.md) |
| contribute a paper, a run, or a change | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Lineage and license

The technique is Matt Shumer's; v1 was packaged by Jay E at RoboNuggets under CC BY 4.0; later versions are by Franco Ribera. Skill text, run records, and research are CC BY 4.0 and the tools are MIT. See [LICENSE.md](LICENSE.md) and the attribution in [versions/README.md](versions/README.md#attribution).
