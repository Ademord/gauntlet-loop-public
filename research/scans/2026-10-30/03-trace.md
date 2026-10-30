# TRACE: evidence sufficient for the next resumed action

Source: [TRACE: Governing Memory Validity in Evolving Multi-Agent Systems](https://arxiv.org/html/2609.33517v1), **2609.33517v1**, submitted 27 September 2026. Assessed 30 October 2026.

The review team read all 41 PDF pages, references and Appendices A–I, all five figures and 17 tables. All numbered figures and selected key tables were visually inspected. No experiment or implementation was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The method reconciles departure state with intervening changes, separates source origin from present eligibility, and checks whether selected evidence covers the returning task. It also prevents excluded information from re-entering through private memory.

Shared-input comparisons and component removals test admission, selection and later action separately. Benefits are uneven: explicit replacements show no consistent advantage, and some gains require more tokens. Trustworthy identity and source bindings are assumed. The derived benchmark has eligibility filters; matched-budget verifier controls remain future work. Some printed pooled baseline components do not reconcile with the stated bucket weights, so precise component claims need caution. Binding a view does not prove its facts, and admitting evidence does not prove the subsequent action is correct.

## Gauntlet 5.2 overlap and one candidate

[Resume validation](../../../skill/references/execution-contract.md) already rechecks artifacts, authority, ownership and unknown effects while preserving holds and spending. [Memory rules](../../../skill/references/learning-and-evolution.md) already separate history from active guidance.

**Verdict: adapt action-scoped evidence coverage.** For materially changed resumed work, connect each permitted next action to its current required evidence and unresolved dependencies. Withhold only the affected action; continue independent authorized work. This can share one check with [evidence eligibility](06-scivaliditybench.md), rather than create a second framework.

**Gate/falsifier:** test mixed valid/stale state and a missing publication dependency. Stale action, lost valid constraints or budget, private-summary bypass, or unnecessary blocking of read-only investigation fails the candidate. Do not require the whole project to be complete before work resumes.
