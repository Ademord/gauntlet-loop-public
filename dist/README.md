# Release artifacts: current version

| File | What it is |
| --- | --- |
| [gauntlet-loop-v5-SKILL.md](gauntlet-loop-v5-SKILL.md) | The whole package as one Markdown file: the entrypoint, then each reference with an anchor. For hosts that take a single file |
| [gauntlet-loop-v5.zip](gauntlet-loop-v5.zip) | The package folder `gauntlet-loop/` for hosts that install a zip. Entries carry fixed timestamps, so the archive rebuilds byte for byte |
| [package-verification.json](package-verification.json) | SHA256 of every package file, the zip, and the single file |
| [RELEASE-REVIEW.md](RELEASE-REVIEW.md) | How v5.0.0 was reviewed before release, and what was not done |

Rebuild with `python tools/build_release.py` and verify with `python tools/verify_release.py`. Only the current version is kept here. Earlier versions are in [versions/](../versions/README.md); their single files can be regenerated with `python tools/export_single_file.py --package versions/<version> --out <file>`.
