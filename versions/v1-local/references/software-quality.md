# Optional software delivery and project-specific checks

Read this when the gauntlet concerns a software repository, app, site, extension, or demo. These checks can optionally extend the definition of done. Select them from the user's choices or requirements already established for the project; do not silently make every item mandatory. Offer a relevant subset when useful, and honor explicit scope such as local-only work. Once selected, a check becomes part of the completion bar and needs real evidence. Unselected extras do not block SHIP; existing project requirements remain requirements.

## Define the bar from the actual project

Inspect the repository instructions, README, existing CI, hosting configuration, release commands, supported platforms, and reported failures. Identify the important user journeys and transitions, including what a fresh user installs or downloads. Turn these into observable acceptance checks with evidence sources before building; the critic can add a missed check when a real gap appears.

Maintain a compact acceptance record in the project's existing worklog or progress artifact: **check, selection/scope, expected behavior, evidence, status, remaining gap**. Use passed, failed, blocked, not selected, or not applicable. Link to test results, screenshots, workflow runs, and the deployed demo rather than relying on a narrative assurance. Counts come from actual results. Explain why a gate is not applicable; lack of access, an inconvenient test, or an unavailable host is a blocker for a selected or otherwise required gate.

## Optional delivery extensions

Each section below describes how to satisfy an extension **after it has been selected**. CI, hosting, demo experience, portable/offline delivery, a clean public working copy, README images, onboarding, and deeper project-specific coverage can be chosen separately or together. Selecting a demo does not automatically select public hosting, offline support, or a repository split.

### Repository and CI

- For a GitHub repository, include an appropriate workflow under `.github/workflows/` and upload it. Reuse or improve an existing workflow before adding a duplicate. For a project hosted elsewhere, use its native CI instead of moving repositories merely to satisfy a GitHub-specific template.
- Trigger checks on the normal code-change path, such as push and pull request, with manual dispatch where useful. Run meaningful project checks: build/type/lint checks where the project uses them, unit and integration checks, and browser tests for the shipped UI. When extension and demo both exist, exercise both explicitly; testing the demo does not prove that the installed extension works.
- Test from a clean checkout using the project's supported, reproducible dependencies. Fail on stale generated release files before rebuilding can conceal the mismatch. Check that the actual packaged or committed installable artifact has the required resources.
- Inspect the hosted run for the exact reviewed commit. Required jobs and critical checks must execute and pass; queued, cancelled, skipped, or older-commit runs are not proof. Read failures, fix the cause, and verify the replacement run. A local passing suite or an untracked workflow file alone does not close this gate.
- A workflow reports test results. Do not imply that it blocks pushes or merges unless the relevant branch rule is actually configured and verified. Do not impose new branch restrictions merely to create CI.

### Hosted demo

- For a user-facing browser UI, app, or extension project, provide a working hosted demonstration using the existing approved provider or a suitable available one: Vercel, GitHub Pages, Sites, or equivalent. Follow environment-required hosting tools and reuse the existing site/configuration. The provider is not the quality bar; a working reviewed demo is.
- Respect the approved audience, including private/owner-only access. The skill itself does not authorize public publication, a paid hosting account, or broader access. Prepare and test the deployable artifact before any genuinely missing approval is requested.
- Publish the exact validated build, confirm deployment completion, and verify that the demo URL loads the intended experience for its intended audience. Check critical controls and routes rather than treating an HTTP 200 or a deployment log alone as sufficient. Keep the source, generated demo, and hosted revision aligned.
- Use fictional or appropriately approved demo data. Keep credentials, customer/order information, private checkout identifiers, and unrelated repository files out of public output. Verify the actual export boundary when the demo is built from a private project.
- For a CLI, library, or backend with no relevant browser UI, use a runnable example or an appropriate demonstration of its interface. Explain why a hosted browser demo is not applicable; do not build a new website just to satisfy the checklist.

### Demo experience and portable delivery

- When a usable demo experience is selected, demonstrate the product's important workflow and outcomes with representative fictional data; populated sample rows alone are insufficient. Let users explore real controls manually, reset to a known starting state, and repeat the workflow. Include relevant empty/loading states and a recoverable failure with a working recovery action when these belong to the selected journey.
- When a guided tour is selected, drive the same application handlers and state transitions as manual use. Explanatory overlays can guide the user, but scripted screenshots or tour-only state changes do not establish working behavior. For a focused walkthrough, make the real target clear with a spotlight or equivalent emphasis and an anchored explanation; dim unrelated areas where useful without obscuring the target or controls. Verify contextual help by hover, keyboard focus, and tap where supported, readable placement on the supported viewports, tour completion, exit into manual exploration, reset, and a second run; exercise interruption or resume where the tour supports them.
- Use deterministic synthetic fixtures for selected demo scenarios: known records, ordering, identifiers, and clock/seed inputs where relevant. Distinguish a successful journey, an empty starting state, and an injected failure followed by recovery. Record each starting fixture, user action, expected visible result, and observed result; a fixture-backed integration remains simulated even when it uses the actual UI handlers.
- When portable/offline delivery is selected and appropriate to the product, provide a self-contained artifact that works through its documented launch method without an account, development server, or network dependency. A single HTML file or a small downloadable bundle can satisfy this; choose the format around the product. Verify a fresh copy with networking disabled, including required assets, the selected journey, recovery, and reset. Record the artifact identity, launch method, and observed behavior. Do not infer offline readiness from a previously cached browser session.
- For each selected delivery surface, verify the same selected scenarios against the actual distributed artifact. Connect the reviewed source revision to generated artifact hashes or equivalent build identity and the hosted deployment where present. Record intentional platform limitations; passing source-tree or hosted checks alone does not prove the downloaded/offline copy works. Add parity coverage to CI when CI is selected and automation is appropriate.

### Clean public working copy

- Select this separately when a private application should have a publishable source/demo copy and may contain recorder output, customer data, local state, or private history. Preserve the original private working copy. Create or update a separate curated copy with synthetic fixtures and the files needed to build, run, and maintain the selected public deliverable; choose the repository structure around the project rather than imposing a split on every app.
- Audit the actual publication boundary before release: files entering the public repository or archive, any history being published, and deployed assets including generated bundles, source maps, fixtures, and downloads. Exclude private recordings, customer records, credentials, private local databases, and private checkout paths. An ignore rule or clean working-tree status does not prove already tracked files, copied artifacts, or history are safe to publish.
- Prove the curated copy works from a fresh location using its documented commands and synthetic data, without resolving files or state from the private original. Record the reviewed export/file list, history scope if applicable, inspection results, and build/demo evidence for the exact copy being published. Preparing this copy does not authorize making a repository or demo public; reuse the approved audience and publication authorization.

### README and user handoff

Apply the selected documentation additions independently; choosing a screenshot or update guide does not also select hosting or CI.

- When documenting an existing or selected hosted demo, link its canonical URL near the start of the README, state how to access it and whether it is private, and keep the link current. An extension's hosted demonstration should be clearly identified as a demo so users can find the real installation instructions.
- When README visual evidence is selected, include at least one useful **actual screenshot** for a visual product or demo. Prefer captures of the reviewed artifact and key setup controls when instructions are otherwise ambiguous. Store images in the repository, use working relative Markdown links, and inspect their readability. Label synthetic fixtures and illustrative mockups honestly; they do not prove a live integration. Nonvisual projects can use a useful output example instead.
- When onboarding or update guidance is selected, explain first installation, normal use, updates, and likely recovery paths in language appropriate to the user. For unpacked extensions, distinguish obtaining updated files in the loaded folder, the extension's Reload control, and refreshing existing shop tabs. State the expected version and settings implications; do not recommend reinstalling for a normal update.
- When documenting existing or selected CI, describe how to run and read it, the supported scope, and known limitations. Verify all selected instructions against the actual UI and commands. Mention export/restore only to the extent the product supports it, and make recovery steps conditional on the relevant UI still being accessible.

## Choose project-specific checks

The following are examples to select from, not an exhaustive checklist to impose on every task:

| Project or boundary | Useful observable checks |
| --- | --- |
| Browser extension | Actual installed extension in an isolated profile; manifest injection and runtime matching; full reviewed host/locale families; cross-origin shopping transitions; unsupported and lookalike hosts; settings/dismissal changes; DOM replacement and SPA/hash navigation; keyboard focus; upgrade/reload behavior |
| Interactive demo or web app | Real controls on supported desktop/mobile sizes; primary route and refresh behavior; keyboard access and focus; reduced motion when relevant; pause/resume and interrupted transitions; loading/empty/error states; generated/published artifact parity |
| API or data application | Representative valid/invalid inputs; relevant authentication and authorization boundaries; persistence and data integrity; failure/retry behavior; migrations or compatibility when affected |
| CLI, library, or packaged tool | Fresh installation and documented example; supported platforms/versions; input and output contracts; meaningful errors; actual distributed package rather than only source-tree imports |

Cover the class of a reported failure, not just one patched example. Derive supported cases from independent reviewed expectations, official interfaces, or user requirements. Do not generate the entire test oracle from the same runtime configuration under test: removing a supported entry must not quietly remove its own regression. Where that failure mode matters, demonstrate that a representative regression or in-memory removal causes the test to fail.

Separate intercepted fixtures, simulated lifecycle/clock events, live public pages, and authenticated end-to-end behavior in the evidence record. Use synthetic session paths in fixtures. Do not claim a live checkout, completed transaction, real reward credit, or native platform behavior from a simulation. Test through isolated environments appropriate to the task instead of altering a user's active browser state.

## Permissions, blockers, and final judgment

Reuse existing authorization and connections. Inspect actual capability before telling the user they need another installation or permission. For example, GitHub repository write access and workflow-editing authorization can differ. If a provider or automatic approval review blocks an operation, identify the exact action, missing capability, and reason; request only the genuinely missing approval, without retrying around the restriction. Keep credentials and device codes out of repository files and logs.

Complete independently authorized work while a blocker is pending. Preserve the prepared artifact and a concrete next step. Missing CI access or hosting permission does not justify claiming those gates passed, silently choosing a broader audience, or inventing an unsupported workaround. Resume the remaining verification when the blocker is resolved.

A separate final critic inspects the current artifacts, the meaningful reference comparison, and the evidence for every agreed gate. Recheck after material changes; an earlier verdict does not cover a later build automatically. Return **SHIP** only when selected and otherwise required gates pass and the reference comparison supports it. Otherwise return **HOLD**, identify the highest-impact remaining gap, and continue the builder/critic loop or report the actual external blocker. Unselected recommendations are not release blockers. Keep the progress artifact and final handoff consistent with the recorded evidence.
