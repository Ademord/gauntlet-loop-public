# Recorder storage: measured scale and retention

[Measurement record](observer-storage-measurement.json), including the preserved probe-source hash.

On September 21 the live observer database occupied **57,344 bytes (56 KiB)** for four diagnostic sessions and 22 received events, including contact labels and separate outcomes. Its fourteen SQLite pages had no free pages. The fixed table/index overhead makes division by 22 a poor estimate of long-run event size. Four native diagnostic stdout files totalled 160,988 bytes (about 157 KiB). These transcripts are separate from the metadata recorder.

An in-memory gzip check reduced the existing 57,344-byte snapshot to 3,577 bytes, preserving every original byte on decompression. This is a measured compressibility result; no archive was substituted for the original and no records were deleted.

A separate synthetic probe populated 10,000 metadata-shaped events with 179-byte metadata objects and unique tool-event identities. SQLite grew from 49,152 to 5,586,944 bytes: **553.8 incremental bytes/event**. A linear projection is approximately **554 MB per million events**, before additional session, annotation, outcome and snapshot growth. It is not a forecast of event traffic or a measurement of future sessions. Raw transcripts and repeated full snapshots can dominate the metadata footprint.

No compaction is warranted at the measured size. If retention later becomes material:

1. Keep active sessions and their indexes in SQLite.
2. At reviewed checkpoints, create consistent private snapshots, then losslessly compress closed snapshots; verify original-byte hashes and a restore before removing a redundant uncompressed copy.
3. Preserve manifests, task/configuration and collector identities, outcomes, failures, human corrections, decision dependencies and reproduction evidence. Acceptance of a claim is not a deletion rule; later audits may reverse it.
4. Prune rebuildable indexes and redundant copies under a documented retention policy. SQLite vacuuming only reclaims unused pages; it does not make currently needed rows disappear.
5. Use a summary as a derived view linked to its sources. Replacing source evidence with a summary is a lossy research decision, not routine storage maintenance.

These are retention recommendations, not an enabled deletion or compaction process. No daily commit automation is installed. Database storage and agent context are separate costs: compressing an archive does not reduce model input tokens unless the retrieval strategy also changes. The [Opus diagnostic](observer-native-validation-002.json) illustrates context-loading cost; it is not evidence that database compaction improves agent performance.
