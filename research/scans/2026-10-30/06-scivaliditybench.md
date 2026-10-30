# SciValidityBench: provenance is not decision eligibility

Source: [The Right Fact, the Wrong Decision: SciValidityBench for Scientific Agent Memory](https://arxiv.org/html/2610.34767v1), **2610.34767v1**, submitted 26 October 2026. Assessed 30 October 2026.

The review team read the complete 25-page paper, references and Appendices A–I. PDF pages 7–9 were visually checked for the main comparisons, controls and sensitivity figures/tables; not every page or figure was visually inspected. No experiment or implementation was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The benchmark separates a correct, traceable payload from whether its governing conditions permit using it for a decision. Generated scientific histories and deterministically compiled relations allow controlled finite-choice tests. Counterfactual pairs and relevant versus irrelevant repairs help test whether a reader responds to the decisive state change.

Same-content flat and typed representations often perform similarly; results do not make a graph necessary. Effects vary by reader and module, including regressions. Short synthetic histories and a known compiler do not establish reliable extraction of governing relations from real projects. A representation comparison must distinguish added information from structure, and a finite decision score is not a workflow cost or reliability measurement.

## Gauntlet 5.2 overlap and one candidate

[Acceptance and resume rules](../../../skill/references/execution-contract.md) already bind artifact, reference, criteria and authority. The useful clarification is that a matching source alone does not establish eligibility for the particular acceptance claim.

**Verdict: adapt a claim-bound evidence check**, combined where possible with [action-scoped resume coverage](03-trace.md). State which claim the evidence supports, the governing conditions and whether they hold now. Leave missing conditions unknown.

**Gate/falsifier:** present the same receipt under a valid prespecified check and an adaptively selected or compromised check, plus an irrelevant-state-change control. The acceptance decision must change only for the decisive condition. Failure to discriminate prevents adoption; no generic scientific-reasoning engine is proposed.
