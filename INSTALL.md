# Install or update Gauntlet Loop

Instructions for the agent receiving the [Quick start prompt](README.md#quick-start). Install the skill as `gauntlet-loop`, including every file under `skill/references/`.

1. **Choose one release.** Honor an explicitly requested version. Otherwise resolve the [latest published stable release](https://github.com/Ademord/gauntlet-loop-public/releases/latest), excluding drafts and prereleases. Record its tag and commit, and use that same release throughout this operation. `main` contains ongoing work; it is not the installation source. If the release cannot be resolved or verified, stop and explain the missing access rather than silently changing the source.

2. **Check the host and existing installs.** Use the host's supported installer and discovery rules. Inspect its active user and project skill locations for `gauntlet-loop`, including symlink targets and other folders declaring that skill name. Prefer updating the existing effective installation. If duplicate installs, unclear precedence, or a shared symlink target make the destination ambiguous, show the concrete conflict and ask which installation to keep. If the host cannot install skills, explain that limitation instead of claiming success.

3. **Compare before replacing.** Identify the installed version, then compare the complete file set and SHA256 hashes against a trustworthy baseline for that version. A version label alone is not evidence that files are unmodified. Use a published release or a recorded repository revision; older versions are archived under `versions/`. Added, missing and edited files all count as differences.

   | Existing installation | Action |
   | --- | --- |
   | None | Install the chosen release. |
   | Exactly matches the chosen release | Leave it in place and report that it is up to date. |
   | Unmodified older version | Back it up and update it. |
   | Modified files, unknown baseline, or a newer version | Preserve it; show the differences and ask whether to keep it or replace it with the chosen release. Do not silently downgrade or discard changes. |

4. **Stage and verify.** Retrieve the whole `skill/` folder from the chosen tag into a temporary directory. Prefer the host's native installer where available, targeting staging first if an installation already exists. Compare the staged file set and hashes with `dist/package-verification.json` from that same release; reject missing, extra or mismatched package files. Read and check `SKILL.md` and its relative reference links. If a future release changes the package format, follow that release's documented verification procedure rather than assuming compatibility.

5. **Replace with a recovery path.** For updates, save the existing directory and a hash inventory outside all skill-discovery roots, so the backup is not loaded as a duplicate skill. Recheck the installed files immediately before replacement; if they changed during preparation, stop and reassess. Place the verified package at the selected destination, then verify its complete file set and hashes again. Restore the previous installation if placement or verification fails. Never delete a user's modified copy to make an installer succeed.

6. **Finish briefly.** Report installed, updated or already current, with the version, location and any backup location. State the host's documented reload or next-turn behavior without claiming to have observed activation. Explain Gauntlet Loop in two short sentences, then ask what task the user wants help with. Installation alone does not start a loop or enable recorders, hooks, research drivers or managed agents.

These are instructions for a capable installation agent, not an automatic updater running in the background. The release package and its checksums provide consistency checks; they are not independent signatures of trust.
