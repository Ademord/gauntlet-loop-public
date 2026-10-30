# Humanize: bounded review and its long tail

Source: [Humanize: Judgement Engineering for Agentic Coding](https://arxiv.org/html/2610.08900v2), **2610.08900v2**. First submitted 6 October 2026; version 2 submitted 8 October. Assessed 30 October 2026.

The review team read the complete 14-page paper, references and Appendices A–B, all six figures and both tables. Selected PDF pages were visually checked. This is full-text assessment, not reproduction or an audit of the authors' implementation. See [reading coverage](reading-manifest.json).

## Source findings and limits

The system separates an approved plan, a builder, fresh review, mechanically routed rounds and later diff review. Its operational corpus exposes substantial work after initial implementation acceptance, including repeated overclaiming. Mechanical gates protect particular artifacts and transitions; they do not establish semantic correctness.

The evidence is deployment history and self-selected issue reports, with reporter concentration and template effects. Applications combine the review process with other interventions and vary in oracle quality. Conditional defect-survival reasoning does not establish independent model errors or a benefit from changing vendors. Some reported applications retain failures or await external acceptance. Gate activation, full cost and a controlled workflow comparison are unavailable. The final diff-review phase is uncapped; that is a design choice, not an experimentally justified rule.

## Gauntlet 5.2 overlap and disposition

[The delivery loop](../../../skill/SKILL.md) already requires fresh evidence-based acceptance, all blocking findings, retained best candidates and integration checks. [The execution contract](../../../skill/references/execution-contract.md) carries unresolved findings across reviewers and preserves budgets. These rules already address the relevant review-tail risk.

**Verdict: defer a new mechanism; retain the existing rules.** Do not copy mandatory reviewer counts, vendor alternation, review cadence or an uncapped final loop. No separate candidate is proposed from this paper. Its useful role is contrary evidence against treating initial acceptance or additional review rounds as sufficient quality evidence.
