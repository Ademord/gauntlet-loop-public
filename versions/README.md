# Versions

Every version of the skill, oldest first. The current version is [skill/](../skill/SKILL.md), with its release artifacts in [dist/](../dist/README.md); every superseded version is frozen here. What each version added, and what it improved or did not, is the chronology in the [main README](../README.md#how-it-evolved). This page records what is stored, how faithfully, how each version was evaluated, and who made it.

## What is stored

| Version | Folder | Files | SKILL.md SHA256 | How it was preserved |
| --- | --- | --- | --- | --- |
| v1 | [v1/](v1/SKILL.md) | 1 | `6a345a43bf58` | Byte for byte. The same bytes appear in every study archive of the original project; its upstream identity is reported by those archives, not verified against GitHub here. |
| v1-local | [v1-local/](v1-local/SKILL.md) | 2 | `9e02f33bc1a0` | Byte for byte. A local, unversioned customization made before 9 September; its software-quality reference is identical to v2's. |
| v2 | [v2/](v2/SKILL.md) | 5 | `02b59d88e929` originally, `5caea86de45d` here | Phrases naming an earlier private project were generalized: one in `SKILL.md`, two in `references/team-method.md` (originally `b640a14bf58e`), three in `references/research-basis.md` (originally `d6cb2b473c78`). Nothing else changed. |
| v3 | [v3/](v3/SKILL.md) | 1 | `5d89eacaccaa` | Byte for byte. It links four reference files that were never supplied with it, so those links do not resolve. |
| v4.0.0 | [v4/](v4/SKILL.md) | 8 | `94c0360fa0fd` | Byte for byte. Its single-file release can be regenerated with `python tools/export_single_file.py --package versions/v4 --out v4.md`. |
| v5.0.0 | [v5/](v5/SKILL.md) | 8 | in [SHA256SUMS](SHA256SUMS) | Byte for byte, snapshotted when 5.1.0 replaced it in `skill/`. |
| v5.1.0 | [../skill/](../skill/SKILL.md) | 9 | in [dist/package-verification.json](../dist/package-verification.json) | The current version. Adds a ninth file, the restored bars, examples and failure list. |

The full SHA256 of every stored file is in [SHA256SUMS](SHA256SUMS). From the repository root, `sha256sum -c versions/SHA256SUMS` checks them, and so does `python tools/verify_release.py`.

## How each version was evaluated

| Version | Evaluation | Record |
| --- | --- | --- |
| v1 | none known | none |
| v1-local | none recorded | none |
| v2 | one read-only scenario walkthrough by an independent agent (a skipped assertion, duplicated pass claims, language drift mid-slice, limited worker slots, a local-only stop), plus the standard skill validator | upgrade record in the frozen private repository |
| v3 | none recorded | none |
| v4.0.0 | an independent requirements review (three consistency findings fixed), a primary-source check, one prompt-mode forward check under an 8-review budget, the skill validator and package checks | release review in the frozen private repository |
| v5.0.0 | a gauntlet run on itself: nine frozen checks, six scenario probes, six independent critic reviews in three rounds, deterministic validators | 
| v5.1.0 | a gauntlet run under 5.0.0: nine frozen checks, eight scenario probes frozen before building, four independent critics per round, deterministic validators | [gauntlet/v5-upgrade-2026-09-17/](../gauntlet/v5-upgrade-2026-09-17/progress.md), [dist/RELEASE-REVIEW.md](../dist/RELEASE-REVIEW.md) |

None of these is a performance measurement.

## Attribution

- **The technique:** Matt Shumer, in the [Claude of Duty](https://github.com/mshumer/Claude-of-Duty) work. The harsh separate critic, the blind comparison, and the refusal to stop before the work wins come from that prompt.
- **v1:** Jay E at RoboNuggets, [robonuggets/gauntlet-loop](https://github.com/robonuggets/gauntlet-loop), CC BY 4.0, commit `9b1975a`, 6 August 2026. Preserved unmodified in [v1/](v1/SKILL.md).
- **v1-local to v5:** Franco Ribera. v3 borrows the shape of oh-my-pi's orchestration controls ([can1357/oh-my-pi](https://github.com/can1357/oh-my-pi), MIT; ideas, no code) and follows feedback from a practitioner who uses it. v5 was produced by a Claude lead with independent critic agents under the author's direction.

The upstream attributions are retained from the original lineage record and were not independently verified with those projects. Redistribution of any version keeps this section and the credit lines in [LICENSE.md](../LICENSE.md).

## Adding a version

When an upgrade run accepts a new version:

1. Move the outgoing package with `git mv skill versions/v5`, then put the new package in `skill/`.
2. Run `python tools/build_release.py` to rebuild `dist/` for the new version.
3. Run `python tools/verify_release.py --write-version-sums` to record the frozen files.
4. Add a row to the chronology in the main README that says what the version was and what it improved or did not, and rows to the tables above.
