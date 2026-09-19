# Research scan, 19 September 2026

Four arXiv items supplied as a daily scan, each checked against its own abstract on 2026-09-19. Every note records the abstract verbatim, checks the scan's paraphrase line by line, states what the abstract does not establish, quotes where v5 already stands, names the gap, and gives a bounded proposal with a falsifier. Only abstracts were read; inferences beyond them are labeled ASSUMPTION. Two dates in the supplied scan were announcement dates rather than submission dates, and the notes say so.

| # | Source | arXiv | Core transfer | Verdict |
| --- | --- | --- | --- | --- |
| 1 | [Continual Enterprise World Model Discovery](01-continual-enterprise-world-model.md) | 2609.19551 | Memory of an environment should be a revisable model of what actions do, not a pile of observations | defer; small `environment_model` record gated on repeated surprise (B-021) |
| 2 | [Closed-World Resolution](02-closed-world-resolution.md) | 2609.19425 | Whether a tool exists is a question that precedes whether it is allowed; merged tool namespaces shadow each other | adopt the recording half: tool surface in the contract, evidence pointers must resolve, tool list per study arm (B-022) |
| 3 | [Reach or Solve?](03-reach-or-solve.md) | 2609.19636 | An agent writes the state it is later judged from, so endpoint success mixes arriving with finishing | adopt as a program design: [checkpoint handoff](../../program/checkpoint-handoff.md), gated after the first F1 look (B-023) |
| 4 | [Faithful yet Collusive](04-faithful-yet-collusive.md) | 2609.18346 | For an agent that acts in a market, its stated reasoning is not evidence about its conduct | adopt a small selectable check class for deliverables that act (B-024) |

The scan's own synthesis was a layered picture: persistent world model, typed tool resolution, bounded action, environment state, checkpointable trajectory, behavioral audit, model revision. Read against this repository, three of the four land on the same rule the skill already follows for critics and now needs for environments and tools: trust what can be observed, and record the observation, not the explanation. The fourth, checkpoint handoff, is the one that changes what the research program can measure, because it splits an outcome this repository currently reports as a single number.

None of these changes is adopted yet. Each is a backlog candidate; skill changes land only through an upgrade run.

All four full texts were read on 19 September 2026, and each note carries a "Full text" section recording what the abstract hid. The readings changed one design and produced three backlog rows: the handoff design was corrected in three places ([checkpoint-handoff.md](../../program/checkpoint-handoff.md)), and B-030, B-031 and B-032 were queued. B-030 was then checked against the recorded transcripts and found not yet runnable, for the same reason the F1 contrast never fired: no verdict varies.
