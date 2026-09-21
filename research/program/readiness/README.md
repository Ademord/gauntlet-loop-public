# Engineering readiness from real tasks

Use ordinary work to identify possible gaps before funding more comparisons. A failed delivery can expose an environment problem, an implementation defect, a weak evaluator or an unknown cause. It does not by itself establish that another orchestration feature is needed.

This index is separate from [frozen performance experiments](../WORKFLOW.md). It neither changes milestone status nor authorizes a paid worker. The first record, [P001](P001-triage.json), preserves a failed two-attempt pilot and selects managed access to existing validation as the next engineering prerequisite. The original private pilot remains unchanged.

```text
python tools/readiness.py validate
python tools/readiness.py list
python tools/readiness.py show P001
```

These commands only read files. Validation checks structure, accounting consistency, current milestone IDs and complete catalog coverage. It cannot certify that a stated observation is true, a causal diagnosis is correct or a boundary is secure.

## After a task

1. Preserve the outcome, every attempt, corrections, known usage and unknown costs. Reference the original evidence; sanitize any public record.
2. Review all existing milestones. Record every reviewed ID and link relevant IDs to concrete observations. A complete ID list is a review declaration, not proof of substantive review.
3. Separate the observed defect from its proposed cause and the proposed remedy's expected benefit. `cause_status` describes the causal explanation, not certainty that the symptom occurred. Include competing hypotheses and state confidence with its supporting evidence and limits. Classify the gap as missing capability, native configuration, implementation defect, evaluator gap, existing capability or unknown.
4. Choose the smallest action: fix, reuse, investigate or defer. Prefer a cheap check that distinguishes competing explanations before adding machinery. Check native controls and existing tools first; reusing them or adding no feature remains a valid decision. Select one next gap; other decisions remain visible.
5. Define an observable offline, native-without-model or manual qualification: procedure, pass condition and failure condition. Keep its status `not_run` until evidence exists. A passing readiness check closes only that stated engineering question.
6. Resume useful work when its prerequisites pass. Open a separate comparison only when a stable capability exists and an unresolved performance claim justifies spending.

Create a new `*-triage.json` alongside these records using P001's structure. Preserve older records when revising decisions; use a new ID for a materially changed diagnosis or observed qualification result. Keep host paths, raw prompts, task data and transcripts private. A `private:PILOT-ID/...` reference identifies provenance without publishing that evidence; outside readers cannot independently verify it from this repository.

The JSON records retain `performance_evidence: unproven`, `milestone_status_changes: []` and `paid_execution_authorized: false`. Qualified engineering is useful even while the linked research milestone remains partial or blocked: its broader performance claim is a different question. Do not treat a research dependency as a reason to postpone a necessary environment repair.

Do not invent calibrated percentages from one failure. Qualitative confidence tied to evidence is enough. If probabilities are useful later, label them subjective estimates, define the specific outcome and time horizon, and record predictions before checking the result. A probability for a suspected cause and a probability that a proposed change will help are different claims.

## Current decision

P001's worker had file tools only. Existing skill validation found invalid descriptions; inconsistent readiness claims and documentation also remained. The lack of execution access is observed. The hypothesis that providing it would prevent these defects is plausible because the existing validator detects them, but worker use of that feedback and any delivery benefit remain untested. Task breadth, incomplete revision and missed requirements are competing explanations.

The next engineering action is to qualify access to existing validation, including working dependencies and preserved independent acceptance. The cheap first check is whether the intended boundary can run that validator, distinguish the saved invalid artifact from a valid control and expose the diagnostics. That establishes useful access, not that the worker would use it or that a custom sandbox is needed. Reuse native enforcement if it suffices.

Reuse the observer, independent outcomes, attempt accounting and artifact hashes. Task sizing needs a narrower contract before adaptive allocation is considered. No evidence from this pilot currently calls for additional agents, a scheduler, persistent agent memory or automated paid retries.
