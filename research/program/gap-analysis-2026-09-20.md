# Gap analysis: the phase-2 paired study against established practice

Read: `phase2-paired-study.md` with its three amendments, `paired-study/LOG.md`, `paired-study/task-classes.md`, `backlog.md`, `gauntlet-bench-v2-hypothesis.md`, plus `analyze_pairs.py`, `look-F1.md` and the 80 rows of `results.jsonl`, from which I recomputed the numbers below.

Anchors for every cost figure: 30 counted F1 pairs cost $53.65 at a median of $1.79 and 6.7 minutes per pair; the excision pilot cost $17.23 for 8 pairs. A single arm is therefore about $0.90 and three minutes. All 80 rows ran on `claude-sonnet-5`. Twenty-nine of the thirty F1 tasks came from one repository.

---

## Gap 1. No power analysis, and the study could not have detected its own observed effects

**Practice and source.** Miller, *Adding Error Bars to Evals* (Anthropic, 2024): compute the minimum detectable effect for the n you can afford and use it as a gate on whether to run at all. Kohavi (KDD 2015) states the same constraint as sigma-squared over delta-squared. NIST 5.3.3 says to select the design from the objective and the run budget before spending.

**What the programme does.** Section 5 is one sentence: "Target 30 pairs per flag. Analyze at 10, 20, and 30 pairs." There is no computation anywhere in the protocol, the tools, or the reports that connects thirty to any effect size. A grep for power, minimum detectable effect, or MDE across `research/program/` and `tools/paired_study/` returns nothing.

**What the arithmetic says.** From the 30 recorded paired differences, at 80% power and the protocol's own per-look alpha of 0.0167:

| Outcome | SD of paired difference | MDE at n=30 | as % of arm-B median | observed effect | pairs needed for the observed effect |
| --- | --- | --- | --- | --- | --- |
| total tokens | 1,194,522 | 705,648 | 33% | 476,552 (22%) | 66 pairs, $132 |
| cost | $0.30 | $0.18 | 20% | $0.08 (9%) | 151 pairs, $302 |
| wall clock | 71.3 s | 42.1 s | 22% | 21.9 s (12%) | 111 pairs, $222 |

Every observed effect is below the study's own detection floor. The result "no difference detected" was, for all three continuous outcomes, arithmetically guaranteed for any effect smaller than roughly a quarter to a third of the arm's consumption. The protocol correctly refuses to say "no effect", which is good, but neither the protocol nor the log ever states how large an effect the study was blind to.

**Cost to close.** Zero runs and zero dollars. The paired differences are already in `results.jsonl`, and the table above took one script.

**Worth it.** Yes, and it is the single cheapest correction available. It should be a gate: `analyze_pairs.py` should print the MDE at the current n next to every "no difference detected", and the protocol should require an MDE line before a series is authorized. Without it, the programme cannot distinguish a flag that does nothing from an instrument that sees nothing.

---

## Gap 2. The primary outcome had no variance, so no amount of runs could have tested it

**Practice and source.** Zhu et al., *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (NeurIPS 2025): separate task validity from outcome validity, and check whether the grader can discriminate at all. Kapoor et al., *AI Agents That Matter*: a benchmark at ceiling reports a number about nothing.

**What the programme does.** Section 4 names `accepted` as the first primary outcome. Section 6 analyses it with "exact binomial test on discordant pairs (McNemar's exact form)."

**What the arithmetic says.** McNemar's exact test at alpha 0.0167 requires at least seven discordant pairs, all pointing the same way, before it can return a significant result. Six one-way discordant pairs give p = 0.031, which fails. The study observed two discordant pairs in thirty, both the same trivial cause. At that discordance rate you would need roughly 105 pairs, about $190, before you would expect seven discordant pairs to exist, and they would all have to fall one way. On the secondary outcome `solved`, both arms were 30 of 30 on the mutation class and 8 of 8 on the excision class: 38 pairs, 76 arms, zero variance.

**Cost to close.** Zero dollars to state. Closing it properly means a task class that produces failures, which is what B-033 queues.

**Worth it.** Stating it is mandatory. The rest is already the programme's own plan. The thing to fix in the protocol is the ordering: an outcome with no observed variance in a pilot should block the series, in the same way the contrast-fired rate now does. The programme built that gate for the mechanism and not for the outcome.

---

## Gap 3. Five outcomes are tested per look, and the alpha correction was spent only on looks

**Practice and source.** Kohavi et al. (KDD 2014) on the prior-dependent posterior: the more candidates you screen, the more a single significant result is noise. Miller, *How Not To Run An A/B Test*, on how quickly uncorrected repeated testing inflates the error rate.

**What the programme does.** Section 5: "Because there are three looks, each uses a two-sided alpha of 0.05 / 3 (Bonferroni) for the primary outcomes." `analyze_pairs.py` then tests five things per look: acceptance, `reviews_used`, `cost_usd`, `total_tokens`, `wall_clock_s`, each against 0.0167, and declares a difference if any one crosses.

**What this costs.** Five independent tests at 0.0167 give a family-wise error of about 8.1% per look, above the nominal 5%, before the three looks are counted. The Bonferroni division was applied to the multiplicity dimension the protocol noticed and not to the one that actually had five members.

**Cost to close.** Zero. Either name one Overall Evaluation Criterion, which is what the RIGHT model and Kohavi both require, or divide by fifteen instead of three.

**Worth it.** Yes. It does not change the F1 verdict, because nothing crossed anything. It matters before the next series, because the first flag that produces a win will produce it under an inflated alpha, and the programme will have no defence.

---

## Gap 4. The rule for reading the interval against the sign test was not pre-specified, and they disagreed

**What the programme does.** Section 6 says: "Report both the estimate and the interval; a result with an interval that includes zero is 'no difference detected', not 'no effect'." `analyze_pairs.py` sets `significant_at_look` from the sign test p-value alone. The bootstrap interval is printed and never used.

At thirty pairs the two disagreed on the only outcome that moved. The token interval is [-881,458, -44,211], which excludes zero; the sign test gives p = 0.200. The log reconciles this after the fact: "which is the ordinary disagreement between a mean-based interval and a rank-based test when a few large pairs carry the mean." That explanation is correct and it was written after seeing which way the two tests fell.

**Cost to close.** Zero.

**Worth it.** Yes, and before the medium-task series. This is an analysis degree of freedom the pre-registration was written to remove and did not. The honest form is one sentence naming which statistic decides and what the other is for.

---

## Gap 5. There is no trivial baseline arm, and the one that ran by accident was accepted

**Practice and source.** Kapoor et al., *AI Agents That Matter*: place a trivial baseline on the same accuracy-cost plot, and declare a win only on the Pareto frontier. Their finding, quoted: "we are not aware of any papers that compare their proposed agent architectures with any of the last three of our simple baselines on HumanEval."

**What the programme does.** Section 3 fixes two arms: light, which is one build and one independent review, and compact, which is build, critic, revise. Every one of the 76 counted arms ran one of those two. The comparison is one review against one review plus structure. Zero reviews has never been measured.

The programme has one accidental data point and files it as a compliance failure rather than as evidence. From the log: "On x004 the light arm dispatched **no critic at all**. It repaired the function, verified it itself, and reported." That arm was accepted and solved.

**Cost to close.** Thirty single runs of a no-review arm against the existing thirty mutation tasks: about $27 and 1.5 hours. Eight more on the excision tasks: about $7.

**Worth it.** This is the highest-value $27 available to the programme, and it should be spent before anything else. If a build-only arm also solves 30 of 30, then the finding is not "find a class where compact fires". The finding is that on this class the whole review apparatus, light included, is unjustified, and the programme has been comparing two prices for a service nobody needed. That is a real result, it is publishable in the programme's own terms, and it costs less than half of one look.

---

## Gap 6. One model and one repository, and the limit is stated rather than closed

**Practice and source.** *Holistic Agent Leaderboard* (ICLR 2026), 21,730 rollouts across 9 models and 9 benchmarks: "For 21 of 36 runs, higher reasoning effort does not improve accuracy", so a component that helps one model can be inert on another. Narang et al. (EMNLP 2021): re-test the modification in a codebase other than the one it was born in.

**What the programme does.** It says the right thing. From `look-F1.md`: "Tasks are one-token defects and small repairs in one public Python repository, run on one model. Nothing here generalizes to harder work, other languages, or other models." All 80 recorded rows carry `"model": "claude-sonnet-5"`. Twenty-nine of the thirty F1 tasks are `intelligence-*`.

**Cost to close.** A second model across the same thirty pairs is 60 runs, about $54 and 3.5 hours. A second repository is free to mint and another $54 to run.

**Worth it. No, not now.** Spending $108 to replicate a null result about a contrast that never fired buys nothing. Stating the limit is the correct action at this stage, and the programme did state it. Import this practice at the moment one task class makes a mechanism fire, and not before. That is a case where established practice should be declined for a programme this size.

---

## Gap 7. There is no A/A run, so the noise floor is unknown

**Practice and source.** Henderson et al., *Deep Reinforcement Learning that Matters*: ten trials of the identical algorithm with identical hyperparameters, split arbitrarily into two groups of five, produced a statistically significant difference, t = -9.0916, p = 0.0016.

**What the programme does.** Section 3 fixes constants: "same model IDs for lead, builder, and critic across both arms, recorded per run; same skill version (5.0.0) with the flag as the only prompt difference". Every task is run exactly once per arm. No configuration has ever been run against itself.

This matters because the run-to-run variation here is visibly large. The paired token differences have an SD of 1.19M against a median arm size of about 2.1M, and eleven of thirty pairs ran opposite to the mean. None of that variance has been attributed. The programme currently cannot say whether its instrument is quiet and the flag is inert, or whether the instrument is too loud to see anything.

**Cost to close.** Ten of the existing mutation tasks, run twice under arm A alone: 20 runs, about $18 and one hour. That yields ten null paired differences and a noise floor that every later study reuses without re-spending.

**Worth it.** Yes. It is the second purchase to make after the baseline arm. It is the difference between "no difference detected" as an assertion and as a measurement.

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

That is the branch established practice rejects. A rule that measurably does nothing still costs context budget and review surface, which is the analogue of Kohavi's cost of additional deployments. As written, the F2 study cannot remove the evidence ladder under any outcome: A better keeps it, no difference keeps it, and only B better removes it. That is a pre-registration that has already decided.

**Cost to close.** Zero. One cell of one table.

**Worth it.** Half of it. Computing a numeric posterior is not worth doing for a programme with no positive result to interpret, and I would not import that machinery. Adopting the base rate as a default-reject stance is worth doing, because it changes F2 from a study that cannot lose into one that can.

---

## Gap 10. Nothing that enters the skill has an expiry

**Practice and source.** Mahdavi-Hezaveh et al., *Software Development with Feature Toggles* (17 practices from 99 grey-literature artifacts and 38 companies): attach a removal deadline at design time and enforce it with something other than intention, because the softer mechanism fails. Their practitioner quote: the cleanup ticket sits at the top of the next sprint's backlog for six months.

**What the programme does.** The backlog header says skill changes "land only on a versioned branch with a snapshot of the incumbent and an `UPGRADES.md` entry, approved by the owner". Nine items are marked "done in 5.1.0". None of them carries a date by which its usefulness must be demonstrated or it comes out. The backlog itself is thirty-nine rows, most of them two days old, which is exactly the state the practitioner quote describes at its beginning.

**Cost to close.** Zero runs. The enforcement machinery already exists: B-003 shipped a commit-msg hook requiring `Upgrade-run: <run-id>` on anything touching `skill/`.

**Worth it.** A light version only. A build-time time bomb is over-engineering for a one-person skill and I would not import it. What is worth importing is one field: every feature that entered the skill on judgment rather than on a measurement gets a review date, and the hook that already exists can check that the field is present. Without that, the study's only possible output is additions.

---

## Gap 11. Flags are tested one at a time, which forfeits interactions at no saving

**Practice and source.** NIST 5.3.3.4.4 on design resolution, 5.3.3.4.6 on screening under sparsity of effects, and 5.3.3.4.7's catalogue: doubling runs buys roughly one resolution step. Jones and Nachtsheim (2011) on definitive screening at 2m+1 runs.

**What the programme does.** Section 1 ranks F1 through F4 and runs them in order. The hypothesis file, section 9, confirms it: "The flag under study rotates through the pre-registered list ... one at a time, until each reaches its planned 30 pairs or is stopped at a look."

**What the arithmetic says.** Four flags at thirty pairs each is 240 runs and about $240. A resolution IV fractional factorial over the same four flags, eight configurations per task across thirty tasks, is also 240 runs and about $240. Same money, four main effects clean of pairwise interactions instead of four isolated contrasts, plus the ability to say whether the ladder and the critic shape interact.

**Worth it. Not yet, and say so.** The factorial is unrunnable today for a reason that has nothing to do with money: F2 requires tasks that reach a third review round and none exist, and F4 requires a lesson corpus the protocol itself defers. The correct action is to pre-register the factorial shape now, so that when B-025 produces medium tasks the programme does not default back to one flag at a time out of habit. I would also decline definitive screening designs and alpha spending functions outright. Both are machinery for programmes with more factors and more runs than this one will have.

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

**Futility stopping, invented independently.** The excision pilot's decision not to run a thirty-pair series is textbook conditional-power reasoning: "At a rejection rate of zero it would buy another 'no difference detected' on a class whose mechanism does not engage, for about $65 and three hours." That saved $65 and it is the best decision in the whole record. The programme also stated the letter of its own rule pointed the other way and left the override with the owner, rather than quietly reinterpreting the rule.

**The contrast-fired rate itself.** Nothing in the sources I was given names this metric, and it is the right one. A flag whose mechanism never engages produces a real number about a false subject, and the programme discovered that, named it, pre-registered it, generalized it to F2, F3 and F4 in a table, and then discovered that its own version of it could not distinguish a rejection from a confirmation and replaced it with a verdict-based definition. That sequence is better research practice than the statistics around it.

**Reading transcripts rather than counting them.** This is the SWE-Bench+ discipline, and it is what found both of the harness defects that invalidated the pilot and the x008 proxy misfire. From the excision entry: "Reading that transcript before computing anything, as the design requires, shows the proxy misfired." The programme also recorded both readings of that pair, the favourable letter-of-the-rule one and the unfavourable substantive one, and acted on the unfavourable one.

**Discarding the pilot instead of pooling it.** The git-history leak invalidated the design even though "both pilot transcripts were checked and neither arm looked". Two rows were written off on a possibility, not a demonstrated contamination. That is the correct standard.

**Never pooling classes.** Eight excision pairs ran under a separate flag key "so the rows can never pool with the mutation series", with the stated reason that mixing would "produce an average over two populations that describes neither".

**Cost reported as a top-line number, with the right caveat.** "A token difference of roughly 30% is eight cents a pair, because most tokens are cache reads. Any future claim about a topology being cheaper has to say cheaper in what unit." That is exactly the Kapoor et al. requirement, and the cache-read observation is a genuine contribution the sources do not cover.

**Nulls stated as nulls.** "a result with an interval that includes zero is 'no difference detected', not 'no effect'", applied consistently in both looks.

**Every deviation recorded, including the ones that look bad.** The look taken at 14 pairs instead of 10 is marked a deviation. The spec renamed after its arms had run is a full entry with two additional defects it uncovered. The x004 arm that dispatched no critic is recorded as a protocol violation the harness caught. The m013 self-report mismatch is recorded with the note that the audit count "is a lower bound". Four separate facts that make the programme look worse, each written down by the programme.

**Population limits stated on every result.** "on tasks of this class, from this owner's repositories, with these model versions" is in the protocol and honoured in both reports.

---

## The short version

The programme spent about $73 and learned one true thing: on one-token defects with a deterministic oracle, the extra structure of the compact topology is pure overhead, and no first critic review has ever returned a negative verdict in 76 arms. That finding is sound and the process that produced it is honest.

What it lacks is arithmetic done before spending. Three numbers would have been free and would have changed what was run: the minimum detectable effect was 33% of arm-B tokens and the observed effect was 22%, so the continuous outcomes were untestable at thirty pairs; McNemar needs seven one-way discordant pairs and the study produced two, so acceptance was untestable at any plausible n; and `solved` was 76 of 76, so the quality outcome had no variance at all. The study could not have produced a positive result about anything it measured.

The three purchases worth making, in order, before any medium-task series:

1. A build-only baseline arm on the existing thirty mutation tasks. Thirty runs, about $27, 1.5 hours. It answers whether the review apparatus is justified on this class at all, which is a larger question than the one the study asked.
2. An A/A run: ten tasks, twice, under arm A alone. Twenty runs, about $18, one hour. It establishes the noise floor once and every later study reuses it.
3. The free corrections: print the MDE next to every verdict, name one OEC or divide alpha by fifteen, fix which statistic decides, compute the contrast-fired rate from `critic_dispatches` rather than the agent's self-report, promote `solved` to primary, and change F2's no-difference branch from keep to drop.

That is $45 and three hours of runs plus a morning of scripting, against $240 for four sequential flag studies that would each hit the same ceiling.

---

Budget note, per CLAUDE.md Rule 6: this audit exceeded the 4,000-token per-task budget. Reading five programme documents, the analysis script, the report and the 80-row results file, plus four recomputations, was not compressible into it. Surfacing the breach rather than truncating the analysis.