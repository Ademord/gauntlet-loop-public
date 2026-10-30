# CALM: preserve history without treating it as current guidance

Source: [CALM: Conflict-Aware Lifecycle Memory Governance for Long-Horizon Language Agents](https://arxiv.org/html/2610.38573v1), **2610.38573v1**, submitted 28 October 2026. Assessed 30 October 2026.

The review team read all 25 PDF pages, references and Appendices A–B, all four figures and 14 tables. All numbered figures and selected key tables were visually inspected. No experiment or implementation was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The method separates retained history, persistent lifecycle metadata and query-specific evidence admission. Fixed rules construct relationships; fixed or learned scoring selects from a retrieved candidate set. Missing attributes remain unspecified, and heuristic evidence weights are not truth probabilities.

Matched controls share retrieval and nominal context budgets, but actual packed lengths and order can differ. Bad-memory injection occurs after retrieval. Evaluation excludes adversarial LoCoMo questions, and useful multi-step evidence can be lost. Query-time costs exclude construction and training. Although an overview figure depicts decay, detailed rules do not infer staleness from elapsed time alone. These experiments establish neither transactional durability nor authorization enforcement.

## Gauntlet 5.2 overlap and one candidate

[Learning and evolution](../../../skill/references/learning-and-evolution.md) already separates source history, current state and working context; applies scope and validity before similarity; and preserves superseded evidence for historical questions.

**Verdict: adapt validation, defer a new memory mechanism.** Add one paired current/historical-query case over the same retained source versions. This tests existing policy rather than requiring a graph or learned gate.

**Gate/falsifier:** current guidance must use the applicable version, historical reconstruction must retain the earlier version, and neither query may mutate history or promote duplicated summaries to independent corroboration. A latest-only solution, contradictory current guidance or evidence loss fails. Use observed dependencies rather than importing the paper's numerical thresholds.
