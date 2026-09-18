# Run ledger schema (version 1)

One JSON object per run in `ledger/runs.jsonl`, produced only by `tools/ledger/ingest.py` from committed run records under each project's `gauntlet/` directory. The ledger copies milestone lines, never evidence directories. Fields absent from a source are `unknown`, never guessed. This file is the single schema every source shape is mapped to; the v5 milestone summary (execution contract) is the canonical source shape, and older shapes are mapped with their original keys preserved under `raw`.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | int | 1 |
| `run_id` | string | source run identifier |
| `project` | string | directory name of the project (or repository) that owns the run |
| `source_path` | string | path of the record the row was read from |
| `source_shape` | `v5 | alh | gym | unrecorded` | which mapping produced the row |
| `skill_version` | string | as recorded (`gauntlet-loop 4.0.0`, `gauntlet-loop v3`, ...) |
| `state` | string | `accepted | in_progress | parked_budget | blocked_external | withheld_resume | paused_user | stopped_user | unknown` |
| `difficulty` | `{estimate, proxies[]}` | lead's recorded estimate; `unknown` when absent |
| `verifiability` | string | `deterministic | external | judgment | mixed | unknown` |
| `topology` | `{chosen, reason}` | canonical v5 values when recorded; older `tier` values kept verbatim (`solo`, `team`) |
| `task_class` | string | closed vocabulary `code-fix | code-feature | research | writing | design | deliverable | skill | unknown` (backlog B-002 adds this to the skill's own record) |
| `features_enabled` | string[] | closed vocabulary: `evidence_ladder`, `light_topology`, `order_swap`, `delegates`, `team`, `isolation`, `learning`, `retrieval_allowance`, `parallel_critics`; `unknown` when the record cannot say |
| `reviews` | `{used, per_piece, advisory_only}` | critic reviews; `unknown` where absent |
| `models` | `{lead, builders, critics}` | as recorded or `unknown` |
| `cost` | `{subagent_tokens, wall_clock_s}` | harness-reported subagent tokens and wall clock in seconds, or `unknown` |
| `lessons_retrieved` | list | lesson IDs with ledger outcomes when learning was on; empty otherwise |
| `later_defects` | string | `not assessed` unless a later inspection was recorded |
| `holds_open` | list | unresolved holds at the milestone |
| `raw` | object | the original record verbatim for older shapes (omitted for `v5`) |
| `ingested_at` | string | UTC timestamp of ingestion |

`ledger/unrecorded.jsonl` lists every `gauntlet/` or `gauntlet-work/` directory found with no machine-readable milestone line, with a note of which prose files exist (`PROGRESS.md`, `LOG.md`, `status.json`, round files). That list is the denominator: a missing row is a row.

Privacy: the ledger lives in this private repository. It carries project names and one-line summaries copied from milestone records; it never copies evidence, transcripts, fixtures, or client data. Before any public export the export checklist applies and the ledger is excluded.
