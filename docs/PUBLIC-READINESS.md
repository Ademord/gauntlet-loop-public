# Public-readiness audit

Generated 2026-09-18T14:03:36Z by `tools/public_audit.py` on branch `main` at `bfff58c84a`. Read-only, zero model tokens. Hard patterns are personal paths, machine identity, personal identity, and secrets; review terms are names a person must decide on. The ship plan (ship / scrub / exclude) is the lead's proposal in `tools/public_audit_config.json`; the owner decides.

## Verdict: READY FOR A CURATED PUBLIC COPY

- Tracked files: 114. Ship set hard hits: 0. Scrub set hard hits: 0 (must be removed by hand before those files ship). Ship set review-term hits: 30.
- Git history: 2 commits scanned on all branches; 0 contain text blobs with hard hits. A public copy must therefore be a fresh repository, not this one made public.

## Hits by top-level path (working tree)

| path | action | hard hits | review hits |
| --- | --- | --- | --- |
| .gitattributes | ship |  |  |
| .gitignore | ship |  |  |
| LICENSE.md | ship |  |  |
| README.md | ship |  |  |
| STATUS.md | ship |  |  |
| docs/LINEAGE.md | ship |  |  |
| docs/PUBLIC-READINESS.md | ship |  | possible_client_or_confidential=14 |
| docs/RESEARCH-INTAKE.md | ship |  |  |
| docs/UPGRADES.md | ship |  |  |
| docs/public-readiness.json | ship |  | possible_client_or_confidential=9 |
| docs/thesis | ship |  |  |
| gauntlet/runs.jsonl | ship |  |  |
| gauntlet/v5-upgrade-2026-09-17 | ship |  |  |
| ledger/SCHEMA.md | ship |  |  |
| ledger/config.json | ship |  |  |
| provenance/v5 | ship |  |  |
| releases/v4 | ship |  | possible_client_or_confidential=2 |
| releases/v5 | ship |  | possible_client_or_confidential=2 |
| research/README.md | ship |  |  |
| research/historical-lineage.md | ship |  |  |
| research/program | ship |  | possible_client_or_confidential=1 |
| research/scan-2026-09-17 | ship |  |  |
| research/scan-template.md | ship |  |  |
| skill/SKILL.md | ship |  |  |
| skill/references | ship |  | possible_client_or_confidential=1 |
| tools/build_release.py | ship |  |  |
| tools/export_single_file.py | ship |  |  |
| tools/hooks | ship |  |  |
| tools/ledger | ship |  |  |
| tools/paired_study | ship |  |  |
| tools/public_audit.py | ship |  |  |
| tools/public_audit_config.json | ship |  |  |
| tools/validate_package.py | ship |  |  |
| tools/verify_release.py | ship |  |  |
| versions/v1 | ship |  |  |
| versions/v4 | ship |  | possible_client_or_confidential=1 |

## Release archives

- `releases/v4/gauntlet-loop-v4.zip`: 1 entries with hits; e.g. gauntlet-loop/references/software-quality.md (possible_client_or_confidential=1)
- `releases/v5/gauntlet-loop-v5.zip`: 1 entries with hits; e.g. gauntlet-loop/references/software-quality.md (possible_client_or_confidential=1)

## Git history

| commit | files with hard hits | sample |
| --- | --- | --- |
| bfff58c84a | 0 |  |
| 6b10b48b30 | 0 |  |

## Files with hard hits that the plan would ship or scrub

| path | action | hard hits |
| --- | --- | --- |

## Files with review-term hits (any action)

| path | action | review hits |
| --- | --- | --- |
| docs/PUBLIC-READINESS.md | ship | possible_client_or_confidential=14 |
| docs/public-readiness.json | ship | possible_client_or_confidential=9 |
| releases/v4/gauntlet-loop-v4-SKILL.md | ship | possible_client_or_confidential=1 |
| releases/v4/gauntlet-loop-v4.zip | ship | possible_client_or_confidential=1 |
| releases/v5/gauntlet-loop-v5-SKILL.md | ship | possible_client_or_confidential=1 |
| releases/v5/gauntlet-loop-v5.zip | ship | possible_client_or_confidential=1 |
| research/program/phase2-paired-study.md | ship | possible_client_or_confidential=1 |
| skill/references/software-quality.md | ship | possible_client_or_confidential=1 |
| versions/v4/references/software-quality.md | ship | possible_client_or_confidential=1 |

## Export checklist mapped to this audit

1. Private repository and project names: see review-term hits; the client site and company directories appear only in excluded paths if the plan holds, but the owner must confirm the never-name project is not referenced anywhere (the audit flags one candidate nickname for review).
2. Secrets and identity: hard-pattern counts above; the personal email appears only in historical commit metadata if at all.
3. History: dirty (see table); publish a fresh repository built from a curated export, never this one.
4. Generated and bundled output: release ZIPs and exports are scanned; entries with hits are listed.
5. Evidence: run records, ledger, pitches, task specs, and provenance are excluded from the plan; redacted excerpts can be added later by hand.
6. Private original: this repository stays private and canonical.
7. Standalone proof: the curated copy must pass `tools/validate_package.py` and `tools/verify_archive.py` from its own tree before publication (not yet done).
