# Source 5: Recoverability as a system primitive

| Field | Value |
| --- | --- |
| arXiv | [2609.13672](https://arxiv.org/abs/2609.13672) |
| Title | Recoverability as a System Primitive for Long-Horizon AI Agents |
| Authors | Zhihui Zhang, Wei Liu |
| Submitted | September 12, 2026 |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> AI agents can be interrupted while editing files, calling tools, or carrying out multi-step tasks. Restarting repeats completed work, but continuing from unverified or outdated progress can carry earlier errors forward. A saved state is not necessarily a suitable place to resume. We introduce recoverability as a system primitive that makes reuse an explicit decision: select a supported starting point and a permitted recovery action, or withhold automatic continuation. Its behavioral contract binds that choice to supporting evidence, execution, and independent checks. A reference architecture connects persistence, validation, and control, with complementary runtime instances testing distinct responsibilities. Four deterministic and 20 paired file challenges demonstrate that accurate restoration and successful completion can conceal disallowed starting points. Progress controls attribute retained work to shared restoration. Event-time tests show that permission must also constrain the action, and that independently held policy evidence can expose violations even after an effect occurs. These findings establish why recovery decisions need their own evaluation, beyond restored bytes and final task success. Within supplied policies and a declared trust model, the contribution is a common, testable interface for retaining justified progress and making the conditions for its reuse explicit and enforceable.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| distinguishes state restoration from authorized continuation | "select a supported starting point and a permitted recovery action, or withhold automatic continuation" | matches in substance; "authorized continuation" is the scan's phrase |
| resume bound to evidence, permitted recovery actions, independent checks | "binds that choice to supporting evidence, execution, and independent checks" | matches |
| four deterministic and 20 paired file-recovery challenges | "Four deterministic and 20 paired file challenges" | matches |
| final success alone can hide invalid resumptions | "accurate restoration and successful completion can conceal disallowed starting points" | matches |

## What the abstract does not establish

- The evaluation is file-recovery challenges under supplied policies and a declared trust model, with an architecture that can enforce. A prose skill can only record and instruct; enforcement stays manual. v4 already says so about its other controls.
- Only the abstract was read. ASSUMPTION: "permitted recovery action" is a policy-defined allowlist per checkpoint.

## Where v4 already stands

v4's checkpoint-and-resume section is already close: "On resume, verify relevant files/revisions, read unresolved evidence, reconcile changed external state, and confirm ownership before dispatch. Keep existing budget charges and holds. If checkpoint and artifact disagree, record the discrepancy and reverify the affected scope; do not adopt the more flattering status ... Investigate unknown external effects before a retry; cancellation is not proof of rollback."

## The gap

v4 describes what to check but not what to decide or how to record the decision; it does not say what happens when the skill version, harness, or model changed between pause and resume; it does not say that authorization must be re-read on resume; and it does not state the paper's central point that a later success does not validate the resume. In practice an agent can "reconcile" by reading the checkpoint and continuing.

## Proposed v5 change (adapted, not copied)

1. A `resume_validation` record written before any dispatch: checkpoint ID; artifact identity match (`match | mismatch`); contract, criteria, skill, and lesson-snapshot version match; authorization still valid (user limits, delivery audience, access); external effects reconciled (`confirmed | failed | unknown`); holds carried forward; decision `resume | repair-then-resume | restart-from-evidence | withhold`; permitted next actions.
2. Rule: the decision is recorded before dispatch; `withhold` parks the run as blocked with the missing evidence named; a later acceptance never retroactively validates a resume recorded as invalid.
3. Skill, harness, or model change between checkpoint and resume is a contract amendment event: affected accepted claims are marked for revalidation, and any comparison spanning the change says so.

## Judgment on adoption

Adopt. This is a schema and two sentences on top of v4's existing procedure, and it is the change most directly needed by the repository's own situation: this v5 upgrade is itself a case where a paused v4 run would resume under a different skill version.
