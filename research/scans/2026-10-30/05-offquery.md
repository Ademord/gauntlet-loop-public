# OffQuery: a correct output can leave incorrect state

Source: [Right Answers, Wrong States: Hidden Information Failures in Multi-Agent Collaboration](https://arxiv.org/html/2610.01244v1), **2610.01244v1**, submitted 1 October 2026. Assessed 30 October 2026.

The review team read all 44 PDF pages, references and Appendices A–E, all eight figures and 11 tables. All numbered figures and selected key tables were visually inspected, resolving text-extraction failures in several charts. No experiment or implementation was reproduced. See [reading coverage](reading-manifest.json).

## Source findings and limits

The benchmark measures source verification, retained factual state and current answer separately. Follow-on tasks expose corruption unused by an earlier successful answer. Controls alter information reliability and the timing of shared-context exposure. The proposed repair process verifies competing evidence before reconstructing the state used for answering.

The main setting assumes one misleading source, with smaller stress tests relaxing that assumption. Ground truth is controlled and episodes are bounded. State scoring samples facts and uses model judgments, so it does not certify every retained claim. Candidate-pool size changes both selection and work. A summary overstates human–judge agreement relative to the detailed table; aggregate judge ranking agreement does not eliminate case-level disagreement. Token comparisons do not establish a cost advantage over this workflow.

## Gauntlet 5.2 overlap and one candidate

[The execution contract](../../../skill/references/execution-contract.md) already preserves obligations, holds, budgets and uncertain effects. Its artifact acceptance rules do not explicitly require a separate retained-state postcondition for every stateful task.

**Verdict: adapt one bounded state-integrity check.** When a task writes durable state or resumes from it, verify the affected retained commitments and evidence beside the delivered artifact. This is not an audit of all workspace facts.

**Gate/falsifier:** provide a passing artifact whose handoff silently clears a hold, drops an independent obligation, resets spending or marks an unknown effect confirmed. Acceptance must fail on the affected state claim. A correct unchanged-state control must pass; blanket rejection also falsifies the check's usefulness.
