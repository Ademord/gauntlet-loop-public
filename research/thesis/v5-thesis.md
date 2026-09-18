# Gauntlet Loop v5: verifiability-conditional mechanisms

A study of six September 2026 findings and their transfer into a build-review-revise workflow, conducted as a gauntlet run on the skill itself. Branch `codex/v5-adaptive-evidence-2026-09-17`, run `v5-upgrade-2026-09-17`, 17 September 2026. Author: the lead agent (Claude Fable 5.1 in Claude Code), under Franco Ribera's request. Nothing here is a measured result; every adopted rule is labeled as a design choice with the evidence that motivated it and the observation that could falsify it.

## Abstract

Gauntlet v4 assumed, mostly implicitly, that more of each expensive mechanism is safe: another critic review, a bigger team, a remembered lesson, a restored checkpoint. Six papers submitted between 12 and 16 September 2026 each attack one of those assumptions from a different direction. Read together they support one narrower claim: a mechanism earns its cost only on a dimension that can be verified, and a workflow should record enough per run to test that conditionality on its own tasks. v5 turns that claim into five bounded rule changes (evidence classes and a revision ladder, a recorded difficulty and topology decision with a `light` topology, a retrieval allowance and utility ledger for lessons, a resume validation record, and completion-time accounting), rejects three larger constructions the papers might seem to invite (a learned router, reinforcement-learned memory, a scheduler), and redirects the repository's dormant benchmark program from "which architecture wins" to "which architecture is the cheapest that reliably solves this task". The run that produced v5 found, through independent critics, one mechanical deadlock and five underspecified rules in the first draft; both deterministic findings were the ones that mattered most, which is the thesis observed on itself.

## 1. Problem

v4 (12 September 2026) is a careful specification. It already says that a critic's confidence does not establish quality, that observations which can reject a wrong answer are preferred, that the newest candidate may regress, and that a run should stop and diagnose after two repeated gaps. What it lacks is any place where the cost of a mechanism is weighed against what that mechanism can actually establish. Four concrete consequences:

1. A critic may drive up to nine revisions of a piece on findings that are its own taste, with no signal that distinguishes taste from evidence.
2. Every task gets the same shape, a lead plus a separate critic plus a comparison against a bar, whether it is a one-function fix with an existing failing test or a four-component change with no tests.
3. When learning is enabled, every applicable lesson may enter the working context, and no record says whether it helped.
4. A resume reads the checkpoint, reconciles what it notices, and continues; nothing records that a decision was made, and nothing addresses a skill or model change during the pause.

The user's scan phrased the shared pattern as "more agents, more review, and more remembered history are not monotonically better. The system has to decide when each is worth its cost." That is the problem statement for v5.

## 2. Method: a gauntlet on the skill

The run followed v4's own procedure, with v5 as the product and v4 as the bar. The contract ([gauntlet/v5-upgrade-2026-09-17/contract.yaml](../../gauntlet/v5-upgrade-2026-09-17/contract.yaml)) froze nine checks before any edit: structure, size, research fidelity, six scenario probes, internal consistency, backward compatibility, a prompt-mode forward check, tooling, and export boundary. The comparison dimension was operational guidance quality on the probes, which were written to hit exactly the six failure modes the papers describe ([probes.md](../../gauntlet/v5-upgrade-2026-09-17/probes.md)).

The run also applied two of the ideas under study to itself. Its difficulty was recorded as high with proxies, and its topology as compact with parallel critics of distinct lenses. Its evidence ladder allowed any finding class to drive revision in rounds one and two and required corroboration for judgment findings afterwards. The lead built; three independent critics with fresh context and no access to the lead's reasoning reviewed: one re-fetched every arXiv abstract and checked every figure, one answered the six probes for both packages and read the eight v5 files as one rule set, one acted as a fresh agent drafting a prompt from v5 alone. Each returned the verdict record from the execution contract with evidence classes on findings. The three verdict records are in [evidence/](../../gauntlet/v5-upgrade-2026-09-17/evidence/).

Only the abstracts of the six papers were read. That limit is stated in every note and in the skill's research basis.

## 3. The six sources and how each was judged

Full notes with verbatim abstracts, a line-by-line check of the scan's paraphrase, and the transfer judgment are in [research/scans/2026-09-17/](../scans/2026-09-17/README.md). This section gives the judgment and the reasoning that produced it.

### 3.1 Loop-Back Authority (arXiv 2609.14767)

The experiment isolates one edge: whether a manager may reject a worker's output and oblige a revision. Everything else is fixed. Flat wins on utility and clarity; hierarchical hedges more and each revision loop is associated with a further clarity drop; specification accuracy is at ceiling for both; the supervisory tier costs half again as many tokens. The authors' own sentence is the transferable one: a supervisor pays for itself when it can verify and becomes a liability when it can only opine.

Judgment. This is the strongest of the six for Gauntlet because Gauntlet's central loop is exactly that edge. But the evidence is one open-ended writing task scored by an LLM-judge panel, and the per-loop clarity drop is associational. The effect sizes are small to medium. I did not adopt "fewer reviews" as a rule; I adopted a class on every finding and a ladder that lets evidence keep forcing revisions while opinion loses that power after two rounds. The rule is justified by the mechanism (an opinion-driven loop has no stopping signal) more than by the effect size. The threshold of two rounds is a choice with no measurement behind it, and the research basis says so.

### 3.2 DATS (arXiv 2609.13890)

Hierarchical collaboration beats a single agent by 2.4 pass@1 points on easy problems and 21.1 on hard ones at about ten times the token cost; a per-problem selector at 40% of the always-hierarchical cost beats always-hierarchical. The domain is competitive-programming problems with deterministic scoring.

Judgment. Read next to 3.1 this is not a contradiction but a completion: hierarchy pays on hard problems whose outcomes can be verified. v4's fixed compact default is the cheap end of what DATS shows and is roughly right for easy tasks. What v4 cannot do is learn anything, because its run log does not record the features a selector would need. I adopted a recorded difficulty and verifiability estimate, a recorded topology decision with reason, a `light` topology gated on low difficulty and verifiable checks, and an observational tuple in the milestone record. I rejected building a router: there is no labeled dataset, the lead's difficulty estimate is a self-report that can bend toward whatever saves budget, and the repository's own policy defers benchmark campaigns. The disclosed weakness is that self-report; the record exists so it can be checked against outcomes later.

### 3.3 LIMBO (arXiv 2609.14138)

Replayed experience competes with retrieval, reasoning, tool use, and verification for the same budget; an online policy that decides how much memory to buy per task nearly matches the strongest memory-heavy baselines at half to four-fifths lower cost.

Judgment. The token-competition argument transfers directly; the learned policy does not, because Gauntlet has no per-task reward to learn from. I adopted the manual, disclosed version: a retrieval allowance of three lessons per piece, retrieval as a recorded event with cost, and no retrieval for `light` pieces unless an observed trigger matches. Three is a default, not a measurement.

### 3.4 Interactive Memory Learning (arXiv 2609.17088)

A Planner encodes and a Trigger retrieves; both learn under a delayed reward that propagates later feedback back to the earlier storage decision. The domain is long-term conversation and the abstract gives no numbers. The scan's wording "ICML has one agent deciding" refers to the method's acronym, not the conference.

Judgment. The idea that memory value should come from later consequences rather than storage-time importance is the right correction to v4, whose admission is a probe plus a reviewer at write time. I adopted a utility ledger on each lesson, promotion to `active` only on a recorded downstream benefit in a separate run, demotion on repeated irrelevance, and quarantine on evidenced harm. I rejected the reinforcement learning. The ledger is a manual attribution confounded by everything else in a run; the record says so, and it prioritizes retrieval rather than proving causal value. The demotion rules are v5's inference; the abstract supports delayed reward into storage decisions but does not mention penalizing retrievals, as the fidelity critic noted.

### 3.5 Recoverability (arXiv 2609.13672)

A saved state is not necessarily a suitable place to resume; reuse should be an explicit decision bound to evidence, permitted actions, and independent checks; accurate restoration and successful completion can conceal disallowed starting points.

Judgment. v4's resume paragraph is already close; what it lacks is the decision itself, the version-change case, re-reading authorization, and the statement that later success does not validate the resume. I adopted a resume validation record with four decisions (`resume`, `repair-then-resume`, `restart-from-evidence`, `withhold`), a contract amendment on skill, harness, or model change, and the rule that acceptance never retroactively validates an invalid resume. This was the change most directly needed by the repository's own situation: any v4 run paused today would resume under v5.

### 3.6 PipeSwift (arXiv 2609.16491)

Serving policies optimized for first-token latency yield worse job completion time; completion time varies by up to 1.40× across policies. A serving-systems result.

Judgment. Nothing a prompt-level workflow controls is involved. The transferable content is the objective: the unit of work is the completed job. I adopted only critical-path dispatch guidance and completion-time recording. The consistency critic called the PipeSwift-derived sentences the weakest added words, and I agree; one of them was removed from the entrypoint in round two and the principle lives in the team method.

## 4. The unifying thesis

Each source makes a supervisory, organizational, memory, or persistence mechanism conditional on something. Loop-Back: supervision, conditional on verifiability. DATS: topology, conditional on difficulty in a verifiable domain. LIMBO: memory, conditional on whether it beats spending the same budget on reasoning and verification. ICML: memory value, conditional on later consequences. Recoverability: a checkpoint's validity, conditional on evidence. PipeSwift: local optimization, conditional on the end-to-end objective.

The common shape is that the mechanism is worth its cost only where its effect can be observed. v5 states this once in the entrypoint as a design principle and, in the research basis, labels it the skill's own inference, not a claim any paper makes about this workflow. The operational consequence is two-fold: every expensive mechanism in v5 has a gate that references verifiability (the ladder keys on evidence class; `light` keys on check class; retrieval keys on an observed trigger; resume keys on identity and version matches), and every run records the fields needed to ask later whether the gate was set in the right place.

## 5. What changed in v5

| Mechanism | Rule (where) | Motivating source | What would falsify the design choice |
| --- | --- | --- | --- |
| Evidence classes | every finding is `deterministic`, `external`, or `judgment` (execution contract, verdict record) | 3.1 | classes prove unstable across critics on the same finding |
| Revision ladder | rounds 1 and 2 unrestricted; from round 3 uncorroborated judgment is advisory; parallel critics share one index; corroborating comparison does not advance it (execution contract; SKILL step 5) | 3.1 | pieces accepted under the ladder show more later defects than v4-accepted pieces |
| Revision drift | each review compares against the retained best and names hedging, clarity, or scope loss (execution contract; SKILL step 6) | 3.1 | drift findings are never actionable |
| Difficulty and verifiability estimate | recorded in the contract with proxies (SKILL contract item 6) | 3.2 | estimates do not predict reviews used or outcome |
| Topology decision | lightest topology whose gate is met, reason recorded; `light` only for low difficulty with deterministic or external checks; light exits on `bar`/`none`; changes only at stall, user request, or recorded de-escalation (SKILL team section; team method; stall diagnosis) | 3.2 | `light` pieces fail integration more often than compact ones |
| Observational tuple | milestone records difficulty, verifiability, topology, reviews, advisory counts, wall-clock, lessons and outcomes (execution contract, milestone summary) | 3.2, 3.6 | nobody ever queries it (then remove it) |
| Retrieval allowance | at most three lessons per piece from the frozen pool, `active` before `experimental`, cost recorded; none for `light` unless a trigger is observed (learning reference) | 3.3 | pieces with fewer lessons show more repeated known failures |
| Utility ledger | per-retrieval outcome; promotion needs a benefit in another run; demotion and quarantine rules; grandfathering of v4 lessons (learning reference) | 3.4 | ledger outcomes do not predict future usefulness better than admission review |
| Resume validation | record and decision before any dispatch; version change is a contract amendment; success never validates an invalid resume; `withheld_resume` state (execution contract, checkpoint and resume) | 3.5 | the record is always `resume` with no repairs (then it is ceremony) |
| Completion time | run and piece times recorded or `unknown`; critical-path dispatch (team method; checkpoint) | 3.6 | never used in any decision |
| Reserve for small caps | entrypoint now says ceil(20%) of a smaller cap; per-piece limits capped at the run's remaining allowance | round-1 critic finding, v4 inheritance | none needed; this corrected an internal contradiction |

Sizes: the entrypoint grew from 13,413 to under 16,000 bytes (the frozen limit); the single-file export from 70,753 to under 90,000. One reference (agent language) is byte-identical to v4; the software-quality reference differs by one word ("blocking" for "unresolved" in the SHIP rule), a change the third review round required for consistency with the ladder. Every schema change is additive; the consistency critic verified that v4 verdict, lesson, checkpoint, and milestone records remain valid and that an 8-review user cap still yields a soft point of 6 and a reserve of 2.

## 6. What was rejected or deferred, and why

- A learned topology router. No labeled data, self-reported difficulty, and the repository's standing rule that benchmark campaigns are separate requested work. v5 records what a router would consume; it does not build one.
- Reinforcement-learned memory policies. No reward signal, and the evaluator must not evolve to reward its own output. The ledger is manual and disclosed.
- A scheduler or orchestration graph. v4 refuses these without a demonstrated coordination need; PipeSwift demonstrates none at the workflow level.
- Enforcement. Every v5 control is recorded procedure; the skill still says where enforcement is manual. Recoverability's architecture enforces; v5 only instructs.
- Installation. The package is prepared and reviewed on a branch; installing it over the live skill is a separate user decision, as the repository's own upgrade practice requires.
- Two v4 inheritances the prompt-mode critic flagged were left as they are and are recorded here for a later revision: the Draft-versus-Execute route verbs can both match "make a prompt for: fix X" (the critic resolved it correctly by taking the outer request), and `winner: bar` reads oddly for a repair against a failing original (the execution contract already patches the semantics).

## 7. What the run itself showed

Round one used three parallel reviews, one per lens. All three returned `winner: ours` on their dimension. The fidelity critic re-fetched every abstract and found every title, identifier, date, and figure exact; its seven advisories (missing author lists, an unannotated LaTeX-macro expansion, three inferences stated as limits without labels) were all acted on. The prompt-mode critic, running on a different model, produced a compliant 449-word prompt with one word of headroom and correctly chose the `light` topology under the gate; its most useful finding was that the entrypoint's flat "reserve the final 6 reviews" contradicts the execution contract's ceil(20%) rule for small caps, a v4 inheritance that v5 now fixes at the entrypoint.

The consistency critic failed the candidate on C5 with six findings. Two were deterministic and both were real defects: v5 retrieved only `active` lessons while making `active` conditional on a benefit that can only be earned by being retrieved, so no lesson could ever activate; and the topology-change sentence said "only" and then listed a third trigger. The four judgment findings were all the same shape: the ladder had been written for one critic reviewing in sequence and did not say what happens with parallel critics, judgment-only HOLDs, corroborating reviews that consume the index they are meant to rescue, or slices created after round two. That is a fair description of how the ladder was written, and the run's own topology (three parallel critics in round one) would have put its third reviewer on advisory status under the literal text. Round two fixed all six and eleven advisories; the affected checks were rejudged rather than assumed. The rejudge found two new small conflicts that the exclusive wording of the fixes had introduced ("one exception", "only exits"), and a third round found one wording residual ("unresolved HOLD" surviving in two files); each was a one-clause repair. The prompt-mode critic's second pass found that the per-piece hard limit could consume the integration reserve under a small user cap, an arithmetic defect in a rule this run had itself added.

Two observations about the process. First, the findings that changed the artifact most were the two deterministic ones, and the judgment findings were most valuable where they pointed at a rule that could be made deterministic (an index that counts rounds, a state that exists). That is the thesis observed on the run that produced it, with the obvious caveat that one run proves nothing. Second, the run stayed inside its budget by a wide margin (six of thirty reviews) because deterministic checks ran before every review and because the three lenses did not overlap; a single generalist critic would likely have needed more rounds and produced more judgment findings. Third, fixes generate conflicts: three of the eight consistency findings after round one were caused by round-one repairs, which is an argument for the ladder's own premise that a revision must be compared against the retained best and not only against the bar.

## 8. Threats to validity

- Abstracts only. Every transfer judgment rests on an abstract; the full papers may qualify the claims in ways not reflected here.
- The critics are LLMs judging text about LLM critics. The consistency and probe checks are judgment-with-citation; the citations were verified by the lead, the judgments were not independently replicated.
- The probes were written by the same lead who wrote the candidate, to hit the failure modes the candidate addresses. The probes therefore test whether v5 says what it set out to say, not whether saying it helps. The consistency critic made this point in its own words.
- The difficulty and topology records depend on self-report. If leads bias estimates toward `low` to save budget, the `light` gate becomes a loophole. The gate's second condition (deterministic or external checks) limits the damage: a wrongly light piece still needs an evidence-based review.
- No measurement. Nothing here shows v5 accepts better artifacts, uses fewer reviews, or has fewer later defects than v4. The repository's policy defers that question, and the research program below states how it would be answered.
- Single author, single session, one day. The v4 release had a separate requirements reviewer and a separate source-verification agent; this run had three independent critics but one lead throughout.

## 9. The research program

The repository holds three archived research kits whose experiments were designed and never run, all framed as "which arm wins". DATS and Loop-Back Authority together suggest that question is wrong: there is likely a frontier, with cheap solo execution best for easy verifiable tasks and richer orchestration paying only on hard verifiable tasks, and with judgment-only dimensions penalizing extra review at any difficulty. The better question is whether the cheapest architecture that reliably solves a given task can be predicted from features known before the run.

v5 makes every ordinary run emit the observation a study of that question needs. The program proposal in [research/program/gauntlet-bench-v2-hypothesis.md](../program/gauntlet-bench-v2-hypothesis.md) states the hypotheses, the observational phase that costs nothing beyond the records v5 already keeps, the minimum volume before any inference is credible, and the designed study that would follow only under separate authorization.

## 10. Versioning and rollback

v4 is preserved byte-for-byte under `versions/v4/` with its hashes in `provenance/v4/`. v5's hashes, release file, and archive are recorded in `dist/` once the run accepts. Rolling back is copying `versions/v4/` over the installed skill and verifying against the v4 record; the installation script's before-and-after hash check from v4 applies unchanged. No run in progress under v4 needs to move; a resumed run records the version change as a contract amendment under v5's own rule.

## 11. Conclusion

v5 is a smaller change than its provenance suggests: about two thousand words across five files, all additive, all gated. Its claim is modest and testable: that a workflow should make its expensive mechanisms conditional on verifiability and should record enough to check where the gates belong. The six papers motivate that claim from six directions; none of them proves it for this workflow, and v5 does not pretend otherwise. The run that produced it found its worst defects with deterministic checks and its most useful judgment findings where judgment pointed at something that could be made deterministic. Whether that pattern holds across runs is the first thing the observational record can answer.
