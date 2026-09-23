# Release artifacts: current version

The files here are version 5.1.0. The filenames carry the major version, so they are stable across 5.x releases; the exact version is in the package frontmatter and in [package-verification.json](package-verification.json).

Prefer the one-line [AI setup prompt](../README.md#quick-start). This directory contains optional packaged downloads; the canonical installable skill is [skill/](../skill/SKILL.md), with its references. [GitHub Release v5.1.0](https://github.com/Ademord/gauntlet-loop-public/releases/tag/v5.1.0) publishes the same reviewed bytes, and [Latest release](https://github.com/Ademord/gauntlet-loop-public/releases/latest) points to the current published version.

## Optional terminal installation

For a fresh installation of **v5.1.0**, run this from the project where you want to use the skill:

```sh
npx skills add https://github.com/Ademord/gauntlet-loop-public/tree/v5.1.0/skill
```

For an existing installation, follow the [install/update guide](../INSTALL.md) first to check versions, duplicates and local edits before replacement.

This uses the third-party [skills CLI](https://github.com/vercel-labs/skills); the tested 1.7.0 version requires Node.js 22.20 or later, npm and Git. The exact folder URL selects this release's skill rather than the archived versions. Select your agent and installation scope when prompted. For a scripted project-local copy, append `--agent codex --copy --yes`, or substitute `claude-code`. Installing the skill alone does not enable the repository's recorder or research tools.

Codex also has a built-in skill installer and detects new skills automatically; restart it only if the skill does not appear. See [official skill setup](https://learn.chatgpt.com/docs/build-skills). The AI setup prompt lets the receiving agent use its supported installation method.

## Optional downloads

| File | What it is |
| --- | --- |
| [gauntlet-loop-v5-SKILL.md](gauntlet-loop-v5-SKILL.md) | The whole package as one Markdown file: the entrypoint, then each reference with an anchor. For hosts that take a single file |
| [gauntlet-loop-v5.zip](gauntlet-loop-v5.zip) | The package folder `gauntlet-loop/` for hosts that install a zip. Entries carry fixed timestamps, so the archive rebuilds byte for byte |
| [package-verification.json](package-verification.json) | SHA256 of every package file, the zip, and the single file |
| [RELEASE-REVIEW.md](RELEASE-REVIEW.md) | How v5.1.0 was reviewed before release, and what was not done |

Rebuild with `python tools/build_release.py` and verify with `python tools/verify_release.py`. Only the current version is kept here. Earlier versions are in [versions/](../versions/README.md); their single files can be regenerated with `python tools/export_single_file.py --package versions/<version> --out <file>`.
