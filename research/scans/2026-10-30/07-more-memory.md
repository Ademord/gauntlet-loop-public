# More Memory: descendants are not independent support

Source: [More Memory, Worse Agents: Error Reproduction and Anti-Persistence in LLM Agents](https://arxiv.org/html/2610.27406v1), **2610.27406v1**, submitted 19 October 2026. Assessed 30 October 2026.

The review team read the complete 31-page paper, references and Appendices A–H. PDF pages 6, 7, 10, 27, 29 and 31 were visually checked for results, retention, cost, provenance and sensitivity; not every page or figure was visually inspected. No experiment or implementation was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The tested system preserves execution records while discarding synthesized task advice. Retention ablations favor discarding in four tested settings, but filtering selected skills improves one baseline. This supports investigating harmful feedback from retained guidance, not discarding all memory.

The provenance analysis is observational, without verified event-level reconstruction or group uncertainty; it does not isolate causal amplification. Indirect feedback can remain even when advice is temporary. Cost is measured in calls rather than tokens, latency or money, and auxiliary results lack task/seed uncertainty. No result establishes that validated lessons, user requirements or factual history should be deleted, or that the paper's selection policy should become a default.

## Gauntlet 5.2 overlap and one candidate

[Learning and evolution](../../../skill/references/learning-and-evolution.md) already requires scoped admission, probes, independent review, contrary evidence and benefit in another run. It distinguishes source records from proposed advice and does not enable automatic learning.

**Verdict: adapt a provenance-independence clarification.** A later trajectory influenced by a lesson is not independent confirmation of that lesson merely because it belongs to another run. Keep synthesized advice unadmitted unless it meets the existing process.

**Gate/falsifier:** test a faulty rule, a trace influenced by that rule and a re-derived copy. Preserve their historical records, but do not promote the descendant solely from that chain. A genuinely independent qualifying probe is the positive control. Automatic promotion from circular evidence or deletion of the source history fails the candidate.
