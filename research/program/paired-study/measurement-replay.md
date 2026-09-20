# Measurement replay

Original results SHA-256: `ee345c95beee37cb051be20818215e2c2fc57c2cdd3ab7442659739cda7c3f3f`.

This report derives measurements from saved transcripts. It makes no model calls and does not rerun correctness checks. Original result rows remain unchanged.

Of 80 original rows, 76 are counted. 76 counted transcripts bind to their original rows; 76 have complete modelUsage token categories.

| Measurement | Value |
| --- | ---: |
| Original counted token sum | 150,771,035 |
| modelUsage token sum, known counted rows only | 217,433,726 |
| Costs reconciled to result.total_cost_usd | 76 |
| Cost mismatches | 0 |
| Original / held-out-aware acceptance | 74 / 74 |

| Flag | Complete pairs with modelUsage | Mean tokens A minus B |
| --- | ---: | ---: |
| F1 | 30 | -363,217.133 |
| F1-excision | 8 | -508,759.000 |

The corrected token sum uses inputTokens + outputTokens + cacheReadInputTokens + cacheCreationInputTokens across all result.modelUsage entries. result.usage is recorded separately. No lead/subagent semantics are inferred, and missing categories stay unknown. Cached input tokens are included; token count is not a dollar-equivalent cost.

Each derived row records source line, source/line/transcript SHA-256, tool hashes, binding method, and original measurements. Legacy binding matches usage, cost and turns; it cannot retroactively prove the identity of an unsaved historical transcript. Excluded pilot/startup rows are not rebound to later reruns.

Agent/Task calls are dispatch attempts, not verified critic reviews. Legacy review fields remain labeled unverified. Acceptance is recomputed from recorded suite, scope and held-out results; no test suite is rerun. These corrections do not establish a causal performance benefit.
