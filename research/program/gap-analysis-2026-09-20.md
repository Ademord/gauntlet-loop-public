# Gap analysis: the phase-2 paired study against established practice

## Erratum, 2026-09-20

**Token-metric correction:** every token statistic retained below (including the 476,552 F1 mean difference, SD, intervals and MDE) was calculated from the old `result.usage` field. It is historical arithmetic on a superseded metric, not corrected full-session token evidence or a valid input for a new sample-size plan. The [measurement replay](paired-study/measurement-replay.md) uses complete `modelUsage` categories and gives an F1 mean difference of **-363,217.133 tokens (A minus B)**. Cost reconciliation remains unchanged. Recompute uncertainty from the corrected derived rows before any future token-based inference.

This audit's original wording overstated several conclusions. The affected passages below are corrected; historical sample counts, cost figures and decisions are retained as records of the original study. The MDE table is an approximate, retrospective calculation for a **paired mean**, not a power calculation for the sign test that decided the original results. A low-power comparison can still detect an effect, and a non-significant result does not prove equivalence. Microsoft's web-feature rates do not supply a numeric prior for prompt rules. A/A repeats measure local variability, and a resolution IV design does not identify every pairwise interaction. Finally, x008 **did revise in response to non-blocking critic feedback**; no first-review rejection is not the same as no review-driven revision. See the [dated log correction](paired-study/LOG.md#2026-09-20-correction-to-the-interpretation-of-the-september-19-results). No new experiments were run for this correction.

Read: `phase2-paired-study.md` with its three amendments, `paired-study/LOG.md`, `paired-study/task-classes.md`, `backlog.md`, `gauntlet-bench-v2-hypothesis.md`, plus `analyze_pairs.py`, `look-F1.md` and the 80 rows of `results.jsonl`, from which I recomputed the numbers below.

Anchors for every cost figure: 30 counted F1 pairs cost $53.65 at a median of $1.79 and 6.7 minutes per pair; the excision pilot cost $17.23 for 8 pairs. A single arm is therefore about $0.90 and three minutes. All 80 rows ran on `claude-sonnet-5`. Twenty-nine of the thirty F1 tasks came from one repository.

---

## Gap 1. No prospective power analysis matched to the decision statistic

**Practice and source.** Miller, *Adding Error Bars to Evals* (Anthropic, 2024): compute the minimum detectable effect for the n you can afford and use it as a gate on whether to run at all. Kohavi (KDD 2015) states the same constraint as sigma-squared over delta-squared. NIST 5.3.3 says to select the design from the objective and the run budget before spending.

**What the programme does.** Section 5 is one sentence: "Target 30 pairs per flag. Analyze at 10, 20, and 30 pairs." There is no computation anywhere in the protocol, the tools, or the reports that connects thirty to any effect size. A grep for power, minimum detectable effect, or MDE across `research/program/` and `tools/paired_study/` returns nothing.

**What the arithmetic says.** From the 30 recorded paired differences, a normal approximation for a paired-mean comparison at 80% power and per-look alpha 0.0167 gives the table below. These retrospective plug-in calculations are illustrative planning estimates; they do not give the power of the historical sign test, and sample sizes based on the observed effect are uncertain rather than guarantees:

| Outcome | SD of paired difference | Approximate mean MDE at n=30 | as % of arm-B median | observed mean effect magnitude | estimated pairs if this mean effect and SD persist |
| --- | --- | --- | --- | --- | --- |
| legacy result.usage tokens (superseded) | 1,194,522 | 705,648 | 33% | 476,552 (22%) | historical estimate only; do not reuse |
| cost | $0.30 | $0.18 | 20% | $0.08 (9%) | 151 pairs, $302 |
| wall clock | 71.3 s | 42.1 s | 22% | 21.9 s (12%) | 111 pairs, $222 |

Each observed mean effect is below this approximation's 80%-power MDE. That does not make a non-significant result inevitable: smaller effects can be detected with lower probability. It also does not explain the sign-test result, which concerns the balance of positive and negative paired differences rather than their mean size. The missing prospective step was to choose an estimand, a practically worthwhile effect and a matching analysis, then assess the design's sensitivity under explicit assumptions.

**Cost to close.** Zero runs and zero dollars. The paired differences are already in `results.jsonl`, and the table above took one script.

**Worth it.** Yes: report uncertainty and a clearly labelled planning sensitivity estimate matched to the intended analysis. A retrospective MDE must not become a second significance gate or a claim that the study was incapable of detecting a smaller effect. Use the interval to show which effects remain compatible with the data.

---

## Gap 2. Few acceptance discordances and a ceiling on observed solves

**Practice and source.** Zhu et al., *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (NeurIPS 2025): separate task validity from outcome validity and check the grader. A benchmark at an observed ceiling provides little comparative information about correctness; it can still describe success on the sampled tasks and resource costs.

**What the programme does.** Section 4 names `accepted` as the first primary outcome. Section 6 analyses it with "exact binomial test on discordant pairs (McNemar's exact form)."

**What the arithmetic says.** McNemar's exact test at alpha 0.0167 requires at least seven discordant pairs, all pointing the same way, before it can return a significant result. Six one-way discordant pairs give p = 0.031, which fails. The study observed two discordant pairs in thirty, both the same trivial cause. At that discordance rate you would need roughly 105 pairs, about $190, before you would expect seven discordant pairs to exist, and they would all have to fall one way. On the secondary outcome `solved`, both arms were 30 of 30 on the mutation class and 8 of 8 on the excision class: 38 pairs, 76 arms, zero variance.

**Cost to close.** Zero dollars to state. Closing it properly means a task class that produces failures, which is what B-033 queues.

**Worth it.** State the ceiling and use a pilot to assess whether a planned quality comparison is informative. Zero observed failures does not establish zero population failure probability, and seven expected discordances is not an 80%-power sample-size calculation. Further runs might reveal failures, but a task class that discriminates meaningfully is a better next calibration target than automatically extending this series.

---

## Gap 3. Five outcomes are tested per look, and the alpha correction was spent only on looks

**Practice and source.** Kohavi et al. (KDD 2014) on the prior-dependent posterior: the more candidates you screen, the more a single significant result is noise. Miller, *How Not To Run An A/B Test*, on how quickly uncorrected repeated testing inflates the error rate.

**What the programme does.** Section 5: "Because there are three looks, each uses a two-sided alpha of 0.05 / 3 (Bonferroni) for the primary outcomes." `analyze_pairs.py` then tests five things per look: acceptance, `reviews_used`, `cost_usd`, `total_tokens`, `wall_clock_s`, each against 0.0167, and declares a difference if any one crosses.

**What this costs.** Five independent tests at 0.0167 give a family-wise error of about 8.1% per look, above the nominal 5%, before the three looks are counted. The Bonferroni division was applied to the multiplicity dimension the protocol noticed and not to the one that actually had five members.

**Cost to close.** Zero. Either name one Overall Evaluation Criterion, which is what the RIGHT model and Kohavi both require, or divide by fifteen instead of three.

**Worth it.** Yes. It does not change the historical F1 sign-test verdict because none of those tests crossed the decision threshold. The bootstrap mean interval is a different summary, discussed below. Specify the family of confirmatory claims before the next series; the 8.1% calculation above assumes independent tests, whereas these resource metrics are correlated.

---

## Gap 4. The rule for reading the interval against the sign test was not pre-specified, and they disagreed

**What the programme does.** Section 6 says: "Report both the estimate and the interval; a result with an interval that includes zero is 'no difference detected', not 'no effect'." `analyze_pairs.py` sets `significant_at_look` from the sign test p-value alone. The bootstrap interval is printed and never used.

At thirty pairs the token mean interval is [-881,458, -44,211], which excludes zero; the sign test gives p = 0.200. These answer different questions. The interval estimates the average paired token difference; the sign test examines positive versus negative differences after excluding ties and ignores their magnitudes. It is not a signed-rank test. A few large differences can shift the mean without making signs sufficiently imbalanced. The analyses also need compatible error levels if used together for a decision. Their different results do not license selecting whichever favours an arm.

**Cost to close.** Zero.

**Worth it.** Yes, and before the medium-task series. This is an analysis degree of freedom the pre-registration was written to remove and did not. The honest form is one sentence naming which statistic decides and what the other is for.

---

## Gap 5. There is no trivial baseline arm, and the one that ran by accident was accepted

**Practice and source.** Kapoor et al., *AI Agents That Matter*: place a trivial baseline on the same accuracy-cost plot, and declare a win only on the Pareto frontier. Their finding, quoted: "we are not aware of any papers that compare their proposed agent architectures with any of the last three of our simple baselines on HumanEval."

**What the programme does.** Section 3 fixes two arms: light, which is one build and one independent review, and compact, which is build, critic, revise. Every one of the 76 counted arms ran one of those two. The comparison is one review against one review plus structure. Zero reviews has never been measured.

The programme has one accidental data point and files it as a compliance failure rather than as evidence. From the log: "On x004 the light arm dispatched **no critic at all**. It repaired the function, verified it itself, and reported." That arm was accepted and solved.

**Cost to close.** Thirty single runs of a no-review arm against the existing thirty mutation tasks: about $27 and 1.5 hours. Eight more on the excision tasks: about $7.

**Worth it.** A capable single-agent baseline is necessary before claiming a benefit from review. It should retain ordinary tools, self-tests and revision within a stated budget. If it also solves all sampled tasks, that would show no observed correctness gain from review on that sample, not prove review useless or the configurations equivalent. The thirty-run purchase above was the original proposal, not an authorization or a demonstrated optimum; baseline calibration on the intended task class should determine the next spend.

---

## Gap 6. One model and one repository, and the limit is stated rather than closed

**Practice and source.** *Holistic Agent Leaderboard* (ICLR 2026), 21,730 rollouts across 9 models and 9 benchmarks: "For 21 of 36 runs, higher reasoning effort does not improve accuracy", so a component that helps one model can be inert on another. Narang et al. (EMNLP 2021): re-test the modification in a codebase other than the one it was born in.

**What the programme does.** It says the right thing. From `look-F1.md`: "Tasks are one-token defects and small repairs in one public Python repository, run on one model. Nothing here generalizes to harder work, other languages, or other models." All 80 recorded rows carry `"model": "claude-sonnet-5"`. Twenty-nine of the thirty F1 tasks are `intelligence-*`.

**Cost to close.** A second model across the same thirty pairs is 60 runs, about $54 and 3.5 hours. A second repository is free to mint and another $54 to run.

**Worth it. No, not now.** Spending $108 to replicate a null result about a contrast that never fired buys nothing. Stating the limit is the correct action at this stage, and the programme did state it. Import this practice at the moment one task class makes a mechanism fire, and not before. That is a case where established practice should be declined for a programme this size.

---

## Gap 7. Within-configuration repeatability has not been measured

**Practice and source.** Henderson et al., *Deep Reinforcement Learning that Matters*: ten trials of the identical algorithm with identical hyperparameters, split arbitrarily into two groups of five, produced a statistically significant difference, t = -9.0916, p = 0.0016.

**What the programme does.** Section 3 fixes constants: "same model IDs for lead, builder, and critic across both arms, recorded per run; same skill version (5.0.0) with the flag as the only prompt difference". Every task is run exactly once per arm. No configuration has ever been run against itself.

The paired token differences have an SD of 1.19M against a median arm size of about 2.1M, and eleven of thirty pairs ran opposite to the mean. These differences combine task-specific treatment effects and stochastic variability; their spread is not itself an estimate of within-configuration run-to-run noise. Repeats can help separate those sources on the sampled tasks.

**Cost to close.** The original proposal was ten existing mutation tasks, run twice under arm A alone: 20 runs, about $18 and one hour. This would give a small local repeatability sample for that task mix, model, harness and budget. It would not establish a universal noise floor reusable across later task classes or model versions.

**Worth it.** Repeats are useful when they resolve uncertainty relevant to the next comparison. They need not be a separate mandatory purchase on the old mutation pool. A treatment comparison still needs its own uncertainty estimate; an A/A result cannot certify that another study's null result is informative.

---

## Gap 8. The number that ended the study was measured by asking the subject

**Practice and source.** Kohavi and Longbotham, *Unexpected Results in Online Controlled Experiments*: investigate the instrument before the phenomenon, because "Getting numbers is easy, getting numbers you can trust is quite difficult." Aleithan et al., *SWE-Bench+*: manually screen the passing cases rather than accepting an aggregate.

**What the programme does.** The 19 September amendment: "`reviews_used` is the agent's recorded review count when it writes an integer, otherwise the number of critic dispatches counted in the transcript." The third amendment then builds the contrast-fired rate on `reviews_used`, and the second look's terminal conclusion rests on it: "**The contrast-fired rate is zero of thirty.**" The programme found the defect itself and recorded it honestly: "`reviews_used` prefers the arm's self-report and falls back to the observed count, so it is not the deterministic measure the protocol calls it."

**Cost to close.** Zero. `critic_dispatches` is already a field on every one of the 80 rows. I recomputed the contrast-fired rate from it: 0 of 30 on the mutation series and 1 of 8 on the excision pilot, identical to the reported figures. The single mismatch is m013 arm A, `reviews_used` 1 against 2 dispatches, and the metric is defined on arm B, so the conclusion survives.

**Worth it.** Yes, and it should be done before the medium-task series rather than left as B-034 and B-035. The conclusion was correct by luck: the one discrepancy in 76 arms happened to sit in the arm where the metric is not read. A terminal decision was committed on a measure the protocol itself had already demoted.

---

## Gap 9. No prior is stated, and the no-difference branch of F2 is "keep"

**Practice and source.** Kohavi et al. (Microsoft ThinkWeek 2009): "only about one-third were successful at improving the key metric", with about one third actively harming it, and "There is always a cost to additional deployments". Kevic et al. (Bing, 21,220 experiments over 2.5 years): "33.4% of the experiment groups were ultimately deployed to all users." Mattos on HYPEX: the loop terminates in abandon, iterate or complete, and "leave it in and move on" is not one of the verdicts.

**What the programme does.** Section 9 gives qualitative predictions with "Confidence: moderate" and "Confidence: low", which is more than most programmes state and is not a prior. The binding defect is in the section 1 decision table. Three of the four flags handle a null correctly: F1's no-difference branch is "keep `light` (cheaper at equal acceptance)", which keeps the cheaper arm; F4's is "drop retrieval"; F3's is "choose by cost". F2's is:

> keep ladder (no cost, no harm)

That branch assumes zero cost and zero harm without measuring either. However, "no difference detected" also does not prove the ladder does nothing. The study can remove it when B is better, so the original claim that it could not lose under any outcome was too strong. A future decision rule should specify the relevant quality margin, costs and treatment of inconclusive evidence. Microsoft's web-product rates motivate caution; they do not supply a numeric prior for this rule.

**Cost to close.** Zero. One cell of one table.

**Worth it.** Clarify the decision under uncertainty without imposing a borrowed numeric prior. Choosing the simpler configuration when a useful benefit remains unproven can be a product policy; record it as that policy, not as evidence of equivalence or an empirical law that one third of prompt rules work.

---

## Gap 10. Nothing that enters the skill has an expiry

**Practice and source.** Mahdavi-Hezaveh et al., *Software Development with Feature Toggles* (17 practices from 99 grey-literature artifacts and 38 companies): attach a removal deadline at design time and enforce it with something other than intention, because the softer mechanism fails. Their practitioner quote: the cleanup ticket sits at the top of the next sprint's backlog for six months.

**What the programme does.** The backlog header says skill changes "land only on a versioned branch with a snapshot of the incumbent and an `UPGRADES.md` entry, approved by the owner". Nine items are marked "done in 5.1.0". None of them carries a date by which its usefulness must be demonstrated or it comes out. The backlog itself is thirty-nine rows, most of them two days old, which is exactly the state the practitioner quote describes at its beginning.

**Cost to close.** Zero runs. The enforcement machinery already exists: B-003 shipped a commit-msg hook requiring `Upgrade-run: <run-id>` on anything touching `skill/`.

**Worth it.** A light version only. A build-time time bomb is over-engineering for a one-person skill and I would not import it. What is worth importing is one field: every feature that entered the skill on judgment rather than on a measurement gets a review date, and the hook that already exists can check that the field is present. Without that, the study's only possible output is additions.

---

## Gap 11. A factorial could screen main effects, with explicit aliasing limits

**Practice and source.** NIST 5.3.3.4.4 on design resolution, 5.3.3.4.6 on screening under sparsity of effects, and 5.3.3.4.7's catalogue: doubling runs buys roughly one resolution step. Jones and Nachtsheim (2011) on definitive screening at 2m+1 runs.

**What the programme does.** Section 1 ranks F1 through F4 and runs them in order. The hypothesis file, section 9, confirms it: "The flag under study rotates through the pre-registered list ... one at a time, until each reaches its planned 30 pairs or is stopped at a look."

**What the arithmetic says.** Four flags at thirty pairs each is 240 runs. A resolution IV half-fraction over four flags, eight configurations per task across thirty tasks, also has 240 runs. Equal run counts do not guarantee equal cost or power. In the standard design I = ABCD, main effects are clear of two-factor interactions but aliased with three-factor interactions; AB = CD, AC = BD and AD = BC. Thus a ladder-by-critic interaction cannot be isolated from its aliased pair without additional assumptions or follow-up runs. [NIST's resolution and aliasing guidance](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3344.htm).

**Worth it. Not yet.** F2 requires tasks that reach a third review round, and F4 requires a lesson corpus the protocol defers. Choose a design when the factors, feasible configurations and estimands are concrete; no factorial commitment is needed before that. Screening main effects and attributing a particular interaction are different objectives.

---

## Gap 12. The mutation class does not exercise what it claims to exercise

**Practice and source.** Zhu et al., ABC: check whether the task can be solved without doing the intended work. Aleithan et al.: two thirds of an apparent SWE-bench improvement was the issue report containing its own answer.

**What the programme does.** `task-classes.md` says of the mutation class: "Exercises: locating a defect from a failing test, and the scope discipline." The failing pytest output names the assertion, the file and the line. The location is handed to the arm before it starts. The class exercises reading an error message and applying a one-token edit.

The programme caught the harder version of this leak and fixed it, which is to its credit: the pilot's clone carried full history, so the answer commit was reachable, and both pilot rows were discarded rather than pooled. The remaining leak is milder and structural.

**Cost to close.** Zero dollars. Read five existing transcripts and count how many turns went to locating versus fixing.

**Worth it.** Yes, because the class description is the input to the next class design. If the class never required diagnosis, then "writing more code is not what makes a review reject" is only half the lesson, and the other half is that nothing in the pool has ever required diagnosis either.

---

## Gap 13. The primary acceptance metric is dominated by housekeeping

**Practice and source.** Kohavi et al. (KDD 2012) on OEC design: the first pitfall is "Picking an OEC for which it is easy to beat the control by doing something clearly wrong", demonstrated by a Bing quality bug that improved both executive metrics.

**What the programme does.** Both of the two discordant acceptance pairs in thirty are the same non-event, recorded plainly in the log: "On m012 and m028 the light arm left pytest output files in the repository root, which the pre-registered scope rule counts as not accepted. Both suites passed." The programme noticed, computed `solved` post hoc at the first look, and pre-registered it in the third amendment, which is correct handling. But `accepted` remains the primary outcome and `solved` remains secondary, so the headline binary is decided by whether an arm deleted a temp file.

**Cost to close.** Zero. Promote `solved` to primary and demote `accepted` to a guardrail that must not degrade.

**Worth it.** Yes. As it stands the top-line quality metric of the study is a tidiness check, and the one number that moved between arms measured tidiness.

---

## What the programme does that established practice would call good

This is a thin programme, not a bad one. The following are not politeness, they are things most published agent evaluations do not do:

**Pre-registration that actually constrained the data.** The protocol and `analyze_pairs.py` were both committed before the first pair ran. The runner refuses a spec edited after its first arm ran, by spec hash. The third amendment is committed as a separate commit that "precedes the second batch", so the stopping rule it introduces was written before the sixteen pairs it governs existed. That is stricter than the norm in this literature.

**Refusing to stop at the first unfavourable look, and saying why.** From the third amendment: "abandoning a pre-registered series at the first unfavourable look is the practice pre-registration exists to prevent." Correct, and it survived a temptation the log records honestly.

**An explicit decision not to expand the pilot.** The excision series was not extended, and the conflict with the pre-registered dispatch-count rule was recorded. This was a practical judgment, not a calculated conditional-power analysis or proof that further runs must be null. The x008 correction below also weakens the original premise that no review-driven revision occurred. The historical stop remains a recorded decision, not a new statistical finding.

**Checking whether the proposed mechanism occurred.** This is useful diagnostic evidence. Neither dispatch count nor verdict wording alone establishes whether feedback changed an artifact: x008 had a passing first verdict followed by a critic-driven edit and another review. Record those behaviours separately. The diagnostic can support error analysis; it does not establish a performance advantage or a novelty claim.

**Reading transcripts rather than counting them, with an auditable correction.** Transcript review found harness defects, but the first x008 reading missed a real edit. In arm B's transcript, line 182 says the lead will address the critic's edge case, line 185 adds `VLMParseError` to the preserved exception types, and line 195 initiates another review. The first verdict was non-blocking, so the reject-then-revise sequence did not occur; feedback-then-revise did. This is evidence of a local review contribution, not a comparative performance result. [Transcript](paired-study/pairs/x008-intelligence-vlm-call_json/F1-excision/armB.transcript.jsonl).

**Discarding the pilot instead of pooling it.** The git-history leak invalidated the design even though "both pilot transcripts were checked and neither arm looked". Two rows were written off on a possibility, not a demonstrated contamination. That is the correct standard.

**Never pooling classes.** Eight excision pairs ran under a separate flag key "so the rows can never pool with the mutation series", with the stated reason that mixing would "produce an average over two populations that describes neither".

**Cost reported as a top-line number, with the right caveat.** "A token difference of roughly 30% is eight cents a pair, because most tokens are cache reads. Any future claim about a topology being cheaper has to say cheaper in what unit." That is exactly the Kapoor et al. requirement, and the cache-read observation is a genuine contribution the sources do not cover.

**A stated distinction between non-significance and no effect.** The protocol contains that distinction, but this audit's original "pure overhead" and "could not have produced a positive result" language went beyond it. Those claims are corrected here.

**Every deviation recorded, including the ones that look bad.** The look taken at 14 pairs instead of 10 is marked a deviation. The spec renamed after its arms had run is a full entry with two additional defects it uncovered. The x004 arm that dispatched no critic is recorded as a protocol violation the harness caught. The m013 self-report mismatch is recorded with the note that the audit count "is a lower bound". Four separate facts that make the programme look worse, each written down by the programme.

**Population limits stated on every result.** "on tasks of this class, from this owner's repositories, with these model versions" is in the protocol and honoured in both reports.

---

## The short version

The programme spent about $73. Both arms solved every sampled mutation and excision task; the mutation series showed no second review in arm B, and the recorded first critic verdicts were not negative. Compact used more resources in the observed aggregates, but the historical decision tests did not establish a performance difference. These observations do not prove equivalence or that review is pure overhead. On x008, non-blocking feedback did cause a code revision.

The design lacked prospective sensitivity planning tied to its actual decision statistic. The retrospective token mean MDE was about 33% of arm-B median consumption versus an observed mean difference of 22%; that indicates limited power under the approximation, not impossibility of detection. Acceptance had only two discordant pairs, while the historical per-look McNemar threshold required at least seven one-way discordances. Solved outcomes were at an observed ceiling. The useful correction is to match tasks, estimands, uncertainty and decision rules before further runs.

The original audit proposed these purchases; the corrected interpretation does not authorize or require them in this order:

1. A build-only baseline arm on the existing thirty mutation tasks. Thirty runs, about $27, 1.5 hours. It answers whether the review apparatus is justified on this class at all, which is a larger question than the one the study asked.
2. An A/A run: ten tasks, twice, under arm A alone. Twenty runs, about $18, one hour. This would estimate local repeatability only; calibration on the next intended task class may be more useful.
3. The free corrections: align the estimand, test and interval; label MDE assumptions; declare the confirmatory claim and multiplicity policy; use observed events for dispatch counts; distinguish verdicts from feedback-driven edits; and specify how inconclusive evidence affects the product decision. Changes to primary outcomes and decision rules apply prospectively, not to rewriting historical results.

The original $45 estimate is retained as an estimate for those proposed runs. It is not evidence that this is the best next spend, nor that all future flag studies would hit the same ceiling. First calibrate a capable baseline and the grader on the intended task class, then size a focused comparison.

---

Budget note, per CLAUDE.md Rule 6: this audit exceeded the 4,000-token per-task budget. Reading five programme documents, the analysis script, the report and the 80-row results file, plus four recomputations, was not compressible into it. Surfacing the breach rather than truncating the analysis.
