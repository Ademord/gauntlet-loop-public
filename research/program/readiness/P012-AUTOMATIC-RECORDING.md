# P012: all local task metadata

The user selected automatic metadata recording for local Codex and Claude tasks. The existing adapter now supports `hook --auto-enroll`: a valid first received event enrolls an unknown session, including work already underway. Existing registrations and matching explicit SessionStart enrollment retain their attribution. Earlier missing events are not reconstructed.

The upgrade replaced nine Codex and ten Claude recorder handlers with a fresh frozen runtime, preserved unrelated settings and exact backups, and retained all 15 historical sessions and 417 events. The core collector bytes are unchanged. Native Codex review trusted the nine exact changed definitions; the installer does not modify trust or bypass review. See the [checkpoint and six expenditure questions](P012-automatic-recording.json).

Integrated regression tests passed 61/61; corrected independent groups passed 8/8. The original independent fixture had five errors in two groups because it put unsupported metadata on a nominal hook wrapper. That field moved to rejection cases while the shared unrelated handler remained in the valid case; original results and the amendment are preserved. The original candidate was retained.

A known Claude session captured SessionStart and SessionEnd without a task prompt. Two known Codex sessions captured SessionEnd only. These are actual native receipts, with a narrower scope than a working request/tool/stop cycle. An initial Claude diagnostic lacked a predetermined session identity, so one additional identified diagnostic was run. The native updater changed the Claude CLI from 2.1.278 to 2.1.280 between launches; the identified result uses 2.1.280. No benchmark worker was dispatched.

Ongoing desktop task capture and complete event delivery remain unqualified. Running sessions may retain old configuration; their metadata begins only after the updated hooks actually receive an event. Enrollment and event storage are separate transactions, so an enrolled session can still have no events after a later failure. Costs, human time and human correction totals remain unknown; this checkpoint makes no performance claim or milestone promotion.

Next: reconcile the next ordinary local task with [the read-only coverage audit](../../../ledger/OBSERVER.md#audit-existing-coverage), including request/tool/stop events, then classify genuine human corrections from separate evidence. No fresh paid benchmark is justified yet.

The [independent probe](../../../tools/probes/observer_auto_enrollment_probe.py) uses temporary databases/settings. It accepts `--candidate-tools`, `--baseline-tools`, `--result` and `--private-log`; the baseline is the pre-P012 tools directory from Git. Synthetic tests do not establish native coverage. [Codex hook review](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks) and [Claude hook reference](https://code.claude.com/docs/en/hooks) describe the host interfaces.

The first program check flagged four historical source hashes after this upgrade. All ten source/test artifacts supporting that older native result were frozen byte-for-byte, and only their index paths moved. Original claims and hashes remain unchanged; see the [relocation receipt](../materials/observer-native-001/relocation.json).
