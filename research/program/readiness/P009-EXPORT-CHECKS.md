# P009 — reusable export receipt checks

The sample tasks exposed controller failures as well as successful worker drafts. This checkpoint extracts the working P008 export-result check into a small standard-library utility. It checks process status and receipt binding to the expected input, output and options. It does not launch a renderer or change a production caller.

Independent qualification passed **8/8 valid controls and 20/20 known-negative cases**, with source bytes/options unchanged. The existing P008 receipt guard preserved 8/8 valid cases and rejected 19/20 negatives; it accepted an empty artifact with a matching receipt at this narrow layer. Its later PDF checks are outside this comparison, so this is not a demonstrated whole-pipeline acceptance bug. The extracted check rejects that case explicitly. The builder suite also passed 12/12 methods. A separate [saved-export replay](P009-saved-export-replay.json) matched two failures and one success without changing source bytes or launching a renderer.

The reference is the **working P008 guard**, including its caller's process-status check. Earlier export failures supply regression cases; an exit-code-only implementation is not presented as a competent alternative. The extraction adds an explicit nonempty-output requirement.

| Investor question | This increment |
| --- | --- |
| Exact claim | The reusable check rejects the specified failed/missing/stale export cases and preserves valid P008 receipt formats. |
| Compared with what? | The functioning P008 guard on their supported overlap. This is compatibility and fault detection, not a model-performance comparison. |
| Stop condition | Any required invalid case accepted or valid case rejected after at most one repair. No widening into a rendering framework. |
| Losses and limits | Receipts can match non-PDF bytes. Hashes do not prove fresh execution or trustworthy provenance. No visual/layout check, browser guard or general sandbox is supplied. |
| Real cost | No new native worker experiment. Deterministic probes make no model calls; the controller and reviewers preparing this checkpoint still consume resources, whose total is unknown. Prior P008 usage is provenance, not charged again. |
| Next expenditure | Adopt the qualified utility in a separately checked trusted export caller, then verify complete accounting on a prospective task before funding a performance comparison. |

The [triage](P009-triage.json) reviews all fifty existing milestones and maps the observations to five decisions. Reuse validator access and visual review; qualify the export contract; keep browser-state and complete-cost questions explicit. No milestone is promoted.

Run the focused checks from the repository root:

```text
python -B -m unittest discover -s tests -p test_export_receipt.py
python -B tools/probes/export_receipt_probe.py --candidate tools/export_receipt.py
python -B tools/readiness.py validate
```

Use `check_export_receipt(returncode, stdout, target, html_raw, options)` from `tools.export_receipt`. A returned receipt means only that this transport contract passed. The caller must still perform format/content/layout checks and preserve its actual process result and source identity. The target must be the caller's expected file, and `options` must be the caller's original request.

The [qualification result](P009-qualification.json) records the independent synthetic cases and artifact identities. The criteria were frozen before the reviewer inspected the candidate, while implementation work could overlap; the preserved criteria's `preimplementation` label is broader than the timing established here. Private P008 task data is not required to rerun the synthetic probe. Any replay of saved private export artifacts is a separate observation, not a fresh render. This checkpoint is local; publication and installed skill changes are not included.


[Independent review](P009-review.json) accepted the module hash in the qualification. Its environment-cause wording note was corrected to a hypothesis; the triage qualification was populated from the saved result. Those document-only follow-ups do not change the tested code. Frozen names refer to their original staging locations: contract.json is P009-contract.json, independent/criteria.json is P009-probe-criteria.json, and independent/probe_export_receipt.py is tools/probes/export_receipt_probe.py.
