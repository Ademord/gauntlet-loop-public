# Scenario probes for check C4 (criteria version 1)

Each probe is a situation an executing agent could face. The critic answers, for both the v4 package (`versions/v4/`) and the candidate (`skill/`): what concrete instruction does the package give, citing the section or line; or "silent". A probe passes for the candidate when it gives a concrete, non-contradictory instruction in the direction the named source supports and v4 is silent or ambiguous on that point.

## P1 Opinion-only revision pressure (source: Loop-Back Authority, arXiv 2609.14767)

A writing piece is in its third critic review. All required checks pass. The critic's `biggest_gap` is "the tone could be more confident; consider cutting qualifiers". No test, source document, or reference excerpt discriminates the current candidate from the proposed change. The previous two revisions each acted on a similar stylistic finding. What does the lead do with this finding, and what happens to the candidate?

## P2 Topology for an easy verifiable fix versus a hard coupled change (source: DATS, arXiv 2609.13890)

Two requests arrive in the same project. (a) A CSV parser mis-handles a quoted comma; a failing unit test already exists; the fix is one function. (b) A change touches the parser, the import UI, the persistence layer, and a background job, with no existing tests for the UI path. For each, what topology and review shape does the package prescribe, what is recorded about that decision, and under what condition may the topology change mid-run?

## P3 Fourteen semantically matching lessons (source: LIMBO, arXiv 2609.14138)

Cross-run learning is enabled for the project. Retrieval by similarity returns fourteen `active` lessons for the current piece. Context is limited and the piece also needs a test run and a reference comparison. How many lessons enter the working context, chosen how, and what is recorded about the retrieval and its cost?

## P4 A lesson that keeps being retrieved but never helps (source: Interactive Memory Learning, arXiv 2609.17088)

An `experimental` lesson was retrieved in three separate runs. In two it was irrelevant to the outcome; in one, following it introduced a regression that a later check caught. A reviewer originally admitted it because the source run's critic called it "an important insight". What happens to this lesson's status and retrieval priority, and what would it take to promote it to `active`?

## P5 Resuming after a drift and a skill upgrade (source: Recoverability, arXiv 2609.13672)

A run was paused after review 11 with a checkpoint. On resume: the working tree's content hash no longer matches the checkpoint's current-candidate identity; the installed skill moved from 4.0.0 to 5.0.0 in between; the user's delivery audience authorization is unchanged. What must be recorded and decided before any worker is dispatched, and can a later successful acceptance retroactively validate the resumption?

## P6 Three independent pieces and one slow check (source: PipeSwift, arXiv 2609.16491)

A run has three independent pieces. Piece 1's critic review needs a 20-minute browser-based check; pieces 2 and 3 are ready to build. What does the package say about dispatch order and what run-level time or completion accounting is recorded?
