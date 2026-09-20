# Measurement repair and calibration

User authorization: on 20 September 2026 the owner asked this agent to lead the agreed changes and reach the goal. Scope is local research tooling, correction of unsupported claims, and one bounded calibration pilot. No production skill upgrade or publication is selected.

Reference: repository commit `5d8cc2c`, clean at start. Working branch: `codex/calibration-and-measurement-repair`. Installed operational skill: v4; production package remains v5.1. They are not the experimental treatment.

Acceptance obligations:

1. Reconcile full-session token fields and retain original raw observations.
2. Reject changed experiment prompts before any paid call; include hidden-test failure in acceptance.
3. Correct unsupported narrative/statistical claims with dated provenance.
4. Provide reproducible baseline/self-check/fresh-review branches with controlled stage counts and spend reservations.
5. Validate frozen graders against good and defective artifacts, then run at most six calibration tasks when the backend is usable.
6. Independently inspect integrated code and evidence; deliver a calibrated decision without claiming a performance gain unsupported by results.

Shared implementation review allowance: six reviews, two reserved for integration. Paid pilot budget: $15, with $13.50 planned stage reservations and the remainder reserved for diagnostic calls. Task fixtures are constructed stress cases, explicitly not a representative benchmark.

Current state: telemetry, errata, fixtures and controller implemented. Historical replay binds 76/76 counted transcripts, corrects total tokens to 217,433,726 and preserves acceptance at 74/76. Original results hash remains `ee345c95beee37cb051be20818215e2c2fc57c2cdd3ab7442659739cda7c3f3f`.

Independent review 1 found four controller defects: functional/scope conflation, mutable evaluator files, partial-report crash, and unknown spend described as exact. All four were fixed and independently reproduced as closed in review 2. Seventeen calibration regression tests and thirteen telemetry tests pass. The six frozen fixtures pass all 24 expected good/bad suite checks. Release verification confirms the unchanged production package and stored versions.

Backend diagnostics spent $0.0138446 and verified authenticated execution, distinct context-preserving forks, cumulative session counters, and incremental request-boundary spending limits. Pilot 01 stopped at its first review budget limit, with total known usage $0.577671 including diagnostics. It completed no arm comparison. A recorded pre-comparison amendment reallocated the same planned spend and removed contradictory builder instructions from the reviewer prompt. Pilot 02 is executing with all prior cost charged against the same $15 ceiling; no further allocation escalation is planned.

Historical-measurement review 3 reproduced every corrected row and raised one documentation HOLD: old token MDE arithmetic still appeared current. The erratum/table now explicitly label it superseded. Review 4 confirmed closure. Independent grader review 5 found the frozen assertions valid and recorded one uncovered large-number defect in the c002 reference; see `research/program/calibration/GRADER-REVIEW.md`. No running candidate was read by that reviewer. One integrated acceptance review remains inside the six-review allowance.

Both attempts preserve exact frozen runner, telemetry and protocol snapshots matching their pre-execution manifest hashes. Rollback is the branch diff; original result rows and production skill remain unchanged. Running terminal session: pilot 02 (do not dispatch another copy; the execution marker prevents it).
