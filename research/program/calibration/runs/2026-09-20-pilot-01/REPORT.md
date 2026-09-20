# Review calibration results

Constructed stress fixtures; exploratory shared-build comparison. No population-level performance or equivalence claim. The primary table scores frozen behavioral tests; scope compliance is reported separately.

| Task | Baseline | Self-check | Fresh review + correction |
| --- | --- | --- | --- |

| Arm | Evaluated tasks | Functional passes | Scope-compliant acceptances | Rescues | Spoils | Actual cost, including shared build |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0 | 0 | 0 | 0 | 0 | $0.3020 |
| self_check | 0 | 0 | 0 | 0 | 0 | $0.3020 |
| review | 0 | 0 | 0 | 0 | 0 | $0.5638 |

Shared builds are charged to each hypothetical arm above but were physically executed only once. Session counters inherited by forks are subtracted before charging additional stages.

Execution state: `stopped`.
Recorded actual experiment spend (including diagnostics): $0.577671.
Unresolved paid-call reservations: none.
Reason if stopped: Stage failure/delegation/budget exceeded; stopped without paid retry.

Decision: this calibration cannot justify changing the production skill. If all branches pass, report a ceiling on these fixtures and stop; if outcomes differ, inspect the concrete defects before proposing a representative confirmation study.
