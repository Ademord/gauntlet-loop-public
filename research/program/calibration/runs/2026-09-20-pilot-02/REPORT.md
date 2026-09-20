# Review calibration results

Constructed stress fixtures; exploratory shared-build comparison. No population-level performance or equivalence claim. The primary table scores frozen behavioral tests; scope compliance is reported separately.

| Task | Baseline | Self-check | Fresh review + correction |
| --- | --- | --- | --- |
| c001-number-parser | pass | pass | pass |
| c002-item-matching | pass | pass | pass |
| c003-review-routing | pass | pass | pass |
| c004-duration-parser | pass | pass | pass |
| c005-checkpoint-selection | pass | pass | pass |
| c006-ready-scheduler | pass | pass | pass |

| Arm | Evaluated tasks | Functional passes | Scope-compliant acceptances | Rescues | Spoils | Actual cost, including shared build |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 6 | 6 | 6 | 0 | 0 | $0.9802 |
| self_check | 6 | 6 | 6 | 0 | 0 | $2.8242 |
| review | 6 | 6 | 6 | 0 | 0 | $3.3463 |

Shared builds are charged to each hypothetical arm above but were physically executed only once. Session counters inherited by forks are subtracted before charging additional stages.

Execution state: `completed`.
Recorded actual experiment spend (including diagnostics): $5.768006599999999.
Unresolved paid-call reservations: none.
Reason if stopped: not applicable.

Decision: this calibration cannot justify changing the production skill. If all branches pass, report a ceiling on these fixtures and stop; if outcomes differ, inspect the concrete defects before proposing a representative confirmation study.
