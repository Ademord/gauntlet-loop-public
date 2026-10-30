# RiseHarness: diagnose a bounded harness change

Source: [Harness Self-Evolution for Long-Horizon Terminal Agents](https://arxiv.org/html/2610.27435v1), **2610.27435v1**. Submitted 20 October 2026; the manuscript cover says 19 October. Assessed 30 October 2026.

The review team read the complete 38-page paper, references and Appendices A–E, all seven figures and seven tables, including worked examples and prompts. Selected PDF pages were visually checked. No implementation or experiment was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The method pairs successes and failures under one configuration, combines agent-visible trajectories with internal runtime traces and a versioned behavioral map, then develops and screens a harness patch. Fixed model weights help isolate harness adaptation within each experiment.

Controls distinguish repeated success, any success and mixed outcomes, but historical baseline reuse and development selection complicate causal claims. One headline transfer result selects a version using the target benchmark; the frozen final version has a smaller gain and also loses some task coverage. Lower variability alone can hide consistently failing tasks. Component ablations combine interventions, and worked examples retain unrun independent-check receipts. Some completion interventions act only once and some paths fail open. Reported predefined budgets do not establish equal consumed cost; no complete cost advantage follows.

## Gauntlet 5.2 overlap and one candidate

[The execution contract](../../../skill/references/execution-contract.md) already requires bottleneck diagnosis, versioned proposals and non-resetting budgets. [Learning and evolution](../../../skill/references/learning-and-evolution.md) already separates method changes from delivery and requires independent validation.

**Verdict: adapt, as an optional between-run diagnosis packet.** For one observed recurring harness failure, add paired same-configuration success/failure evidence, the relevant runtime/source map and stable-success counterexamples. Use existing recordings; unavailable signals remain unknown.

**Gate/falsifier:** a bounded candidate must pass independent positive, negative and recovery cases, then a frozen held-out comparison with fresh controls and full failure/cost accounting. Missing signals, false acceptance, a stable-task regression or no predeclared useful benefit prevents promotion. Do not install tracing or run a paid campaign merely to fill the packet.
