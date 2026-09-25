# Gauntlet Loop v5.1.0 release verification

Date: 2026-09-19. Scope: clear five queued backlog rows without growing the entrypoint past its limit, and produce
the provenance, release artifacts and version records this repository's process requires. No new research adoption,
no benchmark, no claim that 5.1 performs better than 5.0.0, and no installation. Run record:
[gauntlet/v51-upgrade-2026-09-19/](../gauntlet/v51-upgrade-2026-09-19/progress.md).

The 5.0.0 package was snapshotted byte for byte to `versions/v5/` before any edit, and its files are recorded in
`versions/SHA256SUMS`. The run was governed by 5.0.0: nine checks and eight scenario probes frozen before building,
with 5.0.0 itself as the bar.

## What 5.1.0 changes

Five rows, and nothing else in `skill/` that is not recorded as a trade in the contract's amendments.

- **B-020.** The bar table, two filled prompts and the what-breaks-a-loop list that v1 to v3 carried in the
  entrypoint and v4 dropped for size are restored, in a ninth file read when setting a bar, drafting a prompt, or
  diagnosing a stalled loop.
- **B-002.** The milestone record carries the task class and the features enabled, from closed vocabularies.
- **B-009.** The outer request governs when a message matches two routes, and a repair verdict can no longer read
  as the known-failing original winning.
- **B-012.** The prompt-length target is decided by measuring the template rather than guessing, with a rule that
  an include is never dropped to meet it.
- **B-013.** Where a small user cap makes the per-piece soft and hard limits coincide, the review in hand is the
  last for that piece.

## How it was reviewed

Compact with parallel critics. Four independent critics with fresh context, each on a different dimension: scope
and consistency, the eight frozen probes, record compatibility, and a prompt-mode forward check that drafts from
the package alone. Thirteen critic reviews across four rounds, inside the 24/30 run allowance. Deterministic checks
ran first in every round.

| Round | Verdicts | What it found |
| --- | --- | --- |
| 1 | `none`, `bar`, `ours` withheld, `ours` | Nine blocking findings. The two that mattered: the new milestone fields were required in three places and carried in none, while the package claimed in writing that its examples carried them; and the vocabularies had been invented without checking that the repository's run ledger already defined both, so the one real recorded run failed all three of its values. |
| 2 | `ours`, `none`, `ours` withheld, `ours` | Adopting the ledger's vocabulary verbatim left the package unable to record two mechanisms it governs and both examples use. The examples carried the new field and filled it wrongly, declaring a feature their own prose did not run. |
| 3 | `ours` x4, two checks still failing | The remaining findings were about records rather than text: a scope change recorded nowhere, and a vocabulary extension beyond what the row authorized. |
| 4 | `ours`, C4 passes 8 of 8 | One arithmetic error in an amendment, measured and corrected. |

Two critics verified the new controls by perturbation in their own scratch copies rather than by reading them, and
one found a hole that way: the vocabulary check could be disabled by changing a bullet marker, with no signal.
Three critics corrected their own earlier reports unprompted, one of them a search that had used the wrong spelling
in a check whose subject was spelling.

## What the review produced beyond the five rows

Prose in three documents saying "change every copy together" is not a control. `tools/validate_package.py` now
compares all three copies of both vocabularies and fails on drift, and separately checks that both worked examples
carry a marker for every include, after that coverage claim had been inaccurate in three consecutive rounds. Both
checks were verified by mutation: deleting a vocabulary row, drifting any of the three copies in either direction,
and removing one include marker from one example all fail, and the package returns to passing when restored. The
include-marker table is itself bound to the length of the include list, because a hand-written table can drift the
same way.

## Deterministic checks on the released package

`tools/validate_package.py --version 5.1.0 --expect-files 9 --export dist/gauntlet-loop-v5-SKILL.md
--max-export-bytes 110000`: nine files, name and version, entrypoint 15,997 of 16,000 bytes, single-file export
under the raised limit, fifteen local links, three YAML blocks, the forbidden-pattern scan, the vocabulary
equality check and the include-coverage check, all clean. `tools/verify_release.py`: nine package files, the zip,
the portable export, twenty-five stored version files, and every local Markdown link. `tools/public_audit.py`:
zero hard hits on tree and history. Hashes are in [package-verification.json](package-verification.json).

The export limit was raised from 90,000 to 110,000 bytes, recorded as amendment A1 with its reason. The same
amendment records that 5.0.0's export was already 90,333 bytes, over the limit the contract named, because the
validator had never been invoked with `--export`; it now is, and it measures bytes on disk rather than decoded
text, which had undercounted by a byte a line.

## Not done, and disclosed

- **Nothing here is benchmarked.** No measurement says 5.1 performs better than 5.0.0, and none was attempted.
- **The entrypoint lost a sentence to fit.** The Resume route no longer repeats "Record a resume validation
  decision before dispatch". The obligation is unchanged and stated in full four sections later and in the
  drafting reference. Restoring it needs 53 bytes the 16,000-byte entrypoint does not have: dropping either of
  this version's two entrypoint additions frees only 35 or 30. Recorded as amendment A2 with the arithmetic, and
  queued as B-038.
- **Seven wording compressions in the entrypoint are unrecorded as individual trades.** They are listed in the run
  log and diffed against `versions/v5/`; the probe critic judged across four rounds that none changes what an
  agent does, and recorded that as advisory rather than blocking.
- **The ledger's own feature vocabulary was extended** beyond what B-002 authorized, to add the two mechanisms the
  package governs and its examples use. Recorded as amendment A2 with its cost: two new rows in the feature table
  for which every already-ingested run counts as "without".
- **Nothing validates the vocabularies at ingest time** (B-037), so a value outside all three lists still reaches
  the ledger without an error.
- **No installation, no merge decision, no new research adoption.** Four backlog rows opened by this run stay
  queued: B-036, B-037, B-038, B-039.
