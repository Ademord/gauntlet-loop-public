# Tools

Deterministic scripts. None of them calls a model except `paired_study/run_pair.py --execute`. Python 3.10 or later (tested with 3.13). PyYAML and pytest are expected in `.validation-deps/`: run `pip install --target .validation-deps pyyaml pytest` once, then prefix commands with `PYTHONPATH=.validation-deps`.

| Tool | What it does | Command |
| --- | --- | --- |
| `validate_package.py` | Checks a skill package: frontmatter, name, version, eight files, size limits (entrypoint 16,000 bytes, single file 90,000), local links, YAML examples, forbidden personal patterns | `python tools/validate_package.py --version 5.0.0 --export dist/gauntlet-loop-v5-SKILL.md` |
| `build_release.py` | Rebuilds `dist/` from `skill/`: the single file, a reproducible zip, and `package-verification.json` | `python tools/build_release.py` |
| `export_single_file.py` | Writes one portable Markdown file from any package, references appended with anchors | `python tools/export_single_file.py --package versions/v4 --out v4.md` |
| `verify_release.py` | Checks `skill/` against `dist/package-verification.json`, the zip and single file, every stored version against `versions/SHA256SUMS`, and every local Markdown link | `python tools/verify_release.py`, with `--write-version-sums` after adding a version |
| `public_audit.py` | Scans every tracked file and every commit for personal paths, identity, and secrets; writes its report to `.audit/`. Each scan runs twice, once on the text and once on a copy with doubled separators collapsed, because a Windows path inside a JSON string matches no pattern written for the plain form | `python tools/public_audit.py` |
| `hooks/` | Two guards. `pre-commit` runs `check_staged.py`, which refuses staged text with personal paths, identity, secrets, or a term from your local `tools/private_terms.local.json`, scanning the de-escaped form as well. `commit-msg` runs `check_commit_msg.py`, which refuses a commit that changes `skill/` unless its message has an `Upgrade-run: <run-id>` line naming an existing `gauntlet/<run-id>/` | `git config core.hooksPath tools/hooks` |
| `ledger/` | Run ledger: ingests run records from the roots in `ledger/config.local.json`, aggregates cells and feature contrasts with an `insufficient` guard below three runs, writes a monthly report; outputs stay local | `python tools/ledger/run_all.py` |
| `paired_study/` | Paired-study harness: `survey_repos.py` finds candidate tasks, `mint_mutations.py` mints one-token tasks and `mint_excisions.py` mints medium ones, `make_arms.py` writes the two arm prompts, `run_pair.py` runs one pair headlessly behind a login preflight, `run_series.py` walks the ready pairs, `analyze_pairs.py` applies the committed exact tests, `report_pairs.py` writes the look report | see [paired_study/README.md](paired_study/README.md) |

Local configuration lives in gitignored `*.local.json` files. The schema of the run ledger is [ledger/SCHEMA.md](../ledger/SCHEMA.md).
