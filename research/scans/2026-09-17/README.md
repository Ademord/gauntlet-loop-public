# Research scan, September 17, 2026

Six arXiv items supplied as a daily scan, each checked against its own abstract on 2026-09-17. Every note records the abstract verbatim, checks the scan's paraphrase against it line by line, states what the abstract does not establish, quotes where v4 already stands, names the gap, and gives the proposed v5 change with a judgment. Only abstracts were read; full texts were not. Claims about internal details of any paper are labeled ASSUMPTION inside the notes.

| # | Source | arXiv | Core transfer to Gauntlet | Adoption |
| --- | --- | --- | --- | --- |
| 1 | [Loop-Back Authority](01-loop-back-authority.md) | 2609.14767 | opinion-only revision authority degrades work; supervision pays when it can verify | evidence class + evidence ladder + revision-drift check |
| 2 | [DATS](02-dats-topology-selection.md) | 2609.13890 | topology should be a per-task decision; hierarchy pays on hard verifiable tasks | difficulty/verifiability estimate, recorded topology, `light` topology, observational run record |
| 3 | [LIMBO](03-limbo-memory-budget.md) | 2609.14138 | memory competes with reasoning and verification for the same budget | retrieval allowance, retrieval events, skip-on-light |
| 4 | [Interactive Memory Learning](04-interactive-memory-learning.md) | 2609.17088 | memory value comes from later consequences, not storage-time importance | utility ledger, downstream-utility promotion, demotion and quarantine |
| 5 | [Recoverability](05-recoverability.md) | 2609.13672 | a restored checkpoint is not a valid resume point until validated | resume validation record and decision, version-change amendment |
| 6 | [PipeSwift](06-pipeswift-completion-time.md) | 2609.16491 | optimize completed jobs, not per-response metrics | critical-path dispatch, completion-time record |

The unifying reading, argued in [the thesis](../../thesis/v5-thesis.md): every expensive mechanism in an agent workflow (a supervisor, a bigger team, a memory, a checkpoint) earns its cost only on dimensions that can be verified, and a workflow should record enough to test that conditionality on its own runs.

These notes are inputs to the 5.0.0 upgrade. They do not authorize a benchmark, and none of the adopted changes is claimed to be measured.
