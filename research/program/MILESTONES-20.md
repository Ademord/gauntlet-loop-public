# Twenty progressive decision milestones

Expanded by the [50-milestone matrix](MILESTONES-50.md), which adds current native Codex/Claude Code overlap, research support and scoped completion states. Its native-host baseline and duplicate-arm rules govern future comparisons; this document preserves the earlier detailed proposal.

Proposal, 20 September 2026. This replaces the blanket first-tranche experiment in [the earlier funding proposal](STAGED-FUNDING-PLAN.md). It is a roadmap, not permission to spend twenty rounds of funding.

**Each milestone closes with adopt, reject, reuse, defer, or insufficient evidence.** A newer version is not automatically the incumbent. Progress means a better-supported decision; it does not require a new model experiment. Milestones 1–3 include the three requested configurations, but their local controls belong to one shared comparison, not three separately charged studies.

The [research reuse register](RESEARCH-REUSE-20.md) records eleven primary papers, inspected methods, counterevidence, transfer limits and the savings calculation. Literature can replace generic demonstrations. It cannot establish this exact package's current performance by association.

## Shared definitions and protections

- **Q:** independently accepted tasks / all started eligible tasks, including failed/time-limited attempts as unaccepted. Show not-started tasks and cross-arm attrition separately; never report only successful completions.
- **Cost per acceptance:** total attributable metered cost, including failed attempts and all participating agents, divided by accepted tasks. Undefined if none are accepted. Distinguish CLI-equivalent usage from actual billed cash. Show preparation/evaluation/human work separately and allocate shared cost once; unknown costs remain unknown.
- **Time:** end-to-end wall time including coordination and integration. **Human effort:** observed active minutes, not waiting time or an invented estimate.
- **Rescue/spoil:** a paired task where the incumbent fails and challenger passes, or incumbent passes and challenger fails. Independent graders see the requirements/artifacts, not the builder's persuasive account.
- **False acceptance/rejection:** incorrect or correct artifacts misclassified in a labeled frozen control set. Zero observed failures on that set is not proof of a zero population failure rate.
- **G, an exploratory funding gate:** at least one net additional accepted task in a four-task paired screen without higher cost per acceptance, OR at least 25% lower cost per acceptance with no fewer accepted tasks. Require no new critical regression and no concealed additional human repair. Select the primary route before execution; do not switch after seeing results. These are proposed economic hurdles, not literature effect sizes or significance tests. They replace the earlier six-task hurdle for a smaller bridge, not retroactively grade old results.
- A completed screen earns at most the next bounded expenditure. General superiority/noninferiority claims need a separately planned sample size and uncertainty analysis at milestone 19. Failure to cross a gate means stop funding the current claim for now; it does not prove universal uselessness.
- Before **any** live comparison, including V1: protect hidden evaluation, validate public requirements and grader controls, freeze source/prompt/model identities, provide baseline tools fairly, establish ownership, and verify complete accounting. These are prerequisites, not protections delayed until their later audit milestones.
- Exact archived-package runs and extracted-feature tests are labeled separately. V1 includes its actual prompt generation and documented host/budget adaptation. V3's missing references and legacy rules remain documented. Models stay fixed until the explicit allocation experiment.
- Outcomes/actual losses for unrun local milestones are **not measured**. The loss field below says what a round must expose, not that those losses have already occurred.

## Cost keys

**L:** literature or offline reuse, $0 newly allocated solver-benchmark spend and up to 30 minutes of additional analysis per decision; research inference/tool credits and investigator time still belong in the ledger.

**S:** conditional small screen, up to $24 reserved execution capacity (four paired tasks × two configurations × $3), plus at most one investigator hour of preparation/review. This is a planning cap, not a promise that meaningful tasks fit. Obtain a usable quote first; otherwise re-scope or defer.

**B:** the one possible $46 initial bridge described in the research register. Confirmation's earlier $36 reservation is deferred, not counted as savings. Later costs are conditional individual funding requests, not a blanket commitment or summed project estimate. No automatic paid retries or cap increases.

Every round report must answer the six questions below before and after execution. Before execution, losses and actual costs say “not yet measured”; afterward append the actual observations and retain the predeclared gate.

| # | Decision milestone | Version/source |
| --- | --- | --- |
| 1 | Establish the capable ordinary-agent baseline | Control, before V1 |
| 2 | Determine when self-checking is justified | The second initial comparison |
| 3 | Test the exact V1 workflow's remaining local claim | V1 |
| 4 | Improve deficient development feedback | Evidence-quality mechanism; V1/V4 |
| 5 | Decide whether another review/revision is worth doing | V1 stopping policy |
| 6 | Verify ownership and workspace isolation | V2/V3 engineering control |
| 7 | Test task decomposition and specialized roles | V2 |
| 8 | Measure parallel execution's real latency benefit | V2 scheduling |
| 9 | Test shared findings with provenance | V2 knowledge governance |
| 10 | Evaluate dissent and HOLD resolution | V2 |
| 11 | Allocate budgets across pieces and park stalls | V3 |
| 12 | Bind acceptance to the actual artifact and evidence | V4 |
| 13 | Retain the best verified candidate | V4 |
| 14 | Recover from interruption | V4/V5 checkpoints |
| 15 | Choose light versus heavier effort | V5 initial routing |
| 16 | Limit unsupported repeated judgments | V5 evidence ladder |
| 17 | Reuse verified lessons across tasks | V4/V5 optional memory |
| 18 | Allocate model capability economically | Beyond fixed-model mechanism tests |
| 19 | Confirm the integrated surviving configuration | Whole-system validation |
| 20 | Demonstrate independent user value and reuse | Product evidence; includes V5.1 usability |

## 1. Establish the capable ordinary-agent baseline

Origin: Control, before V1. Research/engineering reuse: Reuse R1/R5 and the existing accounting repairs; no new generic baseline study.

1. **What exact claim are you testing?** A competent ordinary coding workflow is a credible, economical alternative for the chosen user job: independently accepted fixes with little human repair.
2. **Compared with what?** Current agent with normal tests, tools and revisions; check it against the strongest applicable simple published workflow, not an intentionally weak one-shot prompt.
3. **What result would make you stop?** Metric and advance/stop rule: Record Q, cost per acceptance, elapsed time and human minutes. Close readiness only when requirements/tools are equal across arms and every metered component reconciles. Stop on missing inputs or incomplete accounting; do not claim superiority. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Published results concern older models/benchmarks. Report local baseline failures, grading blind spots and missing cost categories; local comparative results are not yet measured.
5. **What did this really cost?** Proposed allowance: L: $0 new benchmark allocation; up to 30 minutes of bounded review. Its local control runs, if needed, are charged once to milestone 3. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Freeze the competent control and the customer's success criterion; fund only unresolved comparisons.

## 2. Determine when self-checking is justified

Origin: The second initial comparison. Research/engineering reuse: Reuse R2/R3/R4/R5/R11. Evidence supports conditional policies, not a universal improvement.

1. **What exact claim are you testing?** An additional self-check can improve some outputs, but useful test feedback, mere reconsideration and fresh resampling are different interventions.
2. **Compared with what?** Ordinary agent versus the same agent explicitly self-checking; do not confuse ground-truth stopping, hidden-test feedback or extra task instructions with autonomous improvement.
3. **What result would make you stop?** Metric and advance/stop rule: Classify each relevant result by feedback source and retry/spend allowance. Adopt a candidate policy only with stated conditions. No local performance claim from literature alone; stop blanket self-check recommendations when evidence is mixed. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Record documented negative results and feedback errors. Reflexion's MBPP decline and intrinsic-correction failures remain in the evidence record.
5. **What did this really cost?** Proposed allowance: L; no separate paid self-check campaign. Any local self-check control is included in milestone 3, not charged again as a new experiment. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Retain a strong self-check or retry control; skip rediscovering that iterative refinement exists.

## 3. Test the exact V1 workflow's remaining local claim

Origin: V1. Research/engineering reuse: R1–R8 constrain design; none directly establishes this archived package's current performance. Small bridge only if needed.

1. **What exact claim are you testing?** The actual V1 reference–critic–revision package improves our chosen task outcomes enough to justify its total overhead.
2. **Compared with what?** Four preselected real tasks across the normal-agent, explicit-self-check and exact V1 arms, same starting source/model/tools/ceilings. Record generated prompts, host adaptations and all calls.
3. **What result would make you stop?** Metric and advance/stop rule: Use the common exploratory G gate against the strongest simple control. A match in all transfer dimensions can close by reuse instead. Stop at the reservation limit or on an expensive tie; four tasks cannot prove a population advantage. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Every task-level loss, critical regression, timeout, unused budget, critic false claim and mismatch between critic approval and independent acceptance.
5. **What did this really cost?** Proposed allowance: B: at most $46 reserved for new execution ($10 readiness + 4×3×$3), conditional on a credible quote. Up to 3 investigator hours; research/analysis cost reported separately. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Keep the earned incumbent, including the ordinary agent if it wins. Buy diagnosis of a specific remaining failure, not an automatic V2 upgrade.

## 4. Improve deficient development feedback

Origin: Evidence-quality mechanism; V1/V4. Research/engineering reuse: Reuse R3/R10 and our saved counterexamples. This is not a tool-deprived V1 comparison.

1. **What exact claim are you testing?** Where existing feedback misses real defects, a specific execution-backed check improves repair decisions without falsely condemning correct alternatives.
2. **Compared with what?** Incumbent's normal tools/checks versus the same workflow plus one targeted check. Independent acceptance remains protected and unchanged in both.
3. **What result would make you stop?** Metric and advance/stop rule: First catch all frozen known counterexamples while retaining valid controls. A paid screen, if justified, must meet G; measure confirmed-finding precision and correct-code rejection. Stop if the check encodes the candidate implementation or an ambiguous requirement. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Incorrect generated tests, missed defects, valid alternatives rejected, and regressions caused by trusting the check.
5. **What did this really cost?** Proposed allowance: L first; reuse existing artifacts/tests. S only for an unresolved effect on new work, not to re-prove that stronger tests can find bugs. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Adopt the validated check or discard it; decide whether another revision has reliable feedback to act on.

## 5. Decide whether another review/revision is worth doing

Origin: V1 stopping policy. Research/engineering reuse: R2/R4/R6/R7 warn against assuming every extra round helps.

1. **What exact claim are you testing?** A continuation rule based on unresolved evidence beats automatically spending another review round.
2. **Compared with what?** One completed correction versus a bounded additional review/correction from the same checkpoint, using only information available at that checkpoint.
3. **What result would make you stop?** Metric and advance/stop rule: Meet G; count incremental rescues minus spoils and incremental cost. Stop continuation when there is no reproducible unresolved finding or the declared marginal-value gate fails. Do not feed held-out grades back into the branch. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Correct work spoiled, repeated findings without progress, and bugs left unresolved by stopping too early.
5. **What did this really cost?** Proposed allowance: L on existing traces; S only if naturally eligible checkpoints exist. Shared prefix cost is charged consistently, not counted as new spend twice. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Freeze an economical stopping rule; fund coordination only when the work actually requires it.

## 6. Verify ownership and workspace isolation

Origin: V2/V3 engineering control. Research/engineering reuse: Reuse existing isolation tests and R9 failure categories. Basic isolation is mandatory from the start, including milestone 3.

1. **What exact claim are you testing?** The implemented ownership protocol prevents conflicting writes and accidental cross-branch state without excessive setup overhead.
2. **Compared with what?** Current safe ownership practice versus any proposed additional isolation machinery; use controlled scratch/replay conflicts, never unsafe production work.
3. **What result would make you stop?** Metric and advance/stop rule: Zero lost edits, state leaks or unresolved ownership conflicts in the frozen fault set; valid nonconflicting cases still complete. Stop the extra machinery if existing controls already satisfy the requirement. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Merge losses, false lockouts, cleanup failures and isolation setup time. Passing injected cases is not a measured real-world failure rate.
5. **What did this really cost?** Proposed allowance: L; $0 new solver calls using existing tests/replays. Quote any new integration implementation separately. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Establish readiness for multi-writer work; no performance premium is claimed merely because isolation checks pass.

## 7. Test task decomposition and specialized roles

Origin: V2. Research/engineering reuse: R6/R8/R9 support task-conditional analysis; role lists themselves are not proof.

1. **What exact claim are you testing?** A particular division of an observed coupled task improves final integrated correctness.
2. **Compared with what?** Same worker count, model mix, tools and budget: clear specialized responsibilities versus general workers on the same decomposition. If decomposition itself changes, test that separately.
3. **What result would make you stop?** Metric and advance/stop rule: Meet G on predeclared task types; score the integrated deliverable, not the number of completed subtasks. Defer if the workload lacks independently ownable pieces. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Interface mismatches, duplicated effort, missing responsibilities and errors introduced at integration.
5. **What did this really cost?** Proposed allowance: S only when relevant tasks exist; otherwise L and defer. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Retain only responsibilities that help; determine whether executing them concurrently adds value.

## 8. Measure parallel execution's real latency benefit

Origin: V2 scheduling. Research/engineering reuse: R8/R9 motivate accounting for coupling and integration; do not import their effect sizes.

1. **What exact claim are you testing?** Parallel execution reduces delivery time for genuinely independent pieces without sacrificing quality or creating disproportionate extra cost.
2. **Compared with what?** Same decomposition, workers, ownership, model mix and outputs, scheduled serially versus concurrently.
3. **What result would make you stop?** Metric and advance/stop rule: At least 20% lower paired median end-to-end time, no fewer accepted tasks, no critical regression and at most 10% higher metered cost. Include coordination/integration/wait time; freeze concurrency before running. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Resource contention, merge repair, race failures, expensive idle workers and tasks slowed down by coordination.
5. **What did this really cost?** Proposed allowance: S; ownership readiness is a prerequisite. Report small-sample latency uncertainty; no population throughput claim. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Enable parallelism only for the measured task class, or keep serial scheduling.

## 9. Test shared findings with provenance

Origin: V2 knowledge governance. Research/engineering reuse: Reuse R9's misalignment taxonomy; local benefit remains an engineering/performance question.

1. **What exact claim are you testing?** Citing the source, scope and status of shared findings prevents other workers from acting on incorrect or stale claims.
2. **Compared with what?** Same workflow and communication allowance with ordinary clear notes versus explicit evidence/status records.
3. **What result would make you stop?** Metric and advance/stop rule: Reject all frozen stale/unsupported records and preserve valid records in replay; meet G before claiming delivery improvement. Stop if bookkeeping consumes more effort than it prevents. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: False facts propagated, useful facts wrongly discarded, stale records reused and extra reading/writing cost.
5. **What did this really cost?** Proposed allowance: L on saved handoffs; S only after a recurring propagation problem is observed. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Adopt the smallest useful record, then test how disputed evidence should affect acceptance.

## 10. Evaluate dissent and HOLD resolution

Origin: V2. Research/engineering reuse: R9 supplies failure categories; it does not prove this HOLD implementation superior.

1. **What exact claim are you testing?** Evidence-backed dissent prevents bad final approvals while allowing correct work to proceed.
2. **Compared with what?** Same reviewers, evidence and allowance: existing issue resolution versus an explicit HOLD with an owner and resolution condition.
3. **What result would make you stop?** Metric and advance/stop rule: Zero approvals of the frozen blocking-failure cases and zero unresolved false HOLDs on valid controls; count time to resolution. A performance claim additionally needs G on real tasks. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Bad approvals prevented and missed, needless HOLDs, deadlocks, and legitimate dissent overruled without evidence.
5. **What did this really cost?** Proposed allowance: L first; S only if unresolved real disagreements justify it. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Keep a bounded resolution policy or remove redundant ceremony.

## 11. Allocate budgets across pieces and park stalls

Origin: V3. Research/engineering reuse: R5/R9 plus existing spend controls; no need to demonstrate that unbounded spending can run away.

1. **What exact claim are you testing?** A soft-limit/parking policy completes more valuable obligations within the same portfolio budget.
2. **Compared with what?** Same fixed queue, declared task values and overall ceiling with current allocation versus the proposed parking rule. Every arm retains an external hard ceiling.
3. **What result would make you stop?** Metric and advance/stop rule: At least 25% more accepted obligations per metered dollar, without leaving a declared critical obligation unfinished. If task values differ, freeze the weights before execution. Defer without observed stalls. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Repairable tasks abandoned early, cheap-task cherry-picking, starvation, and expenditure shifted into later retries.
5. **What did this really cost?** Proposed allowance: L replay first; S for an unresolved allocation question. This differs from milestone 5, which concerns one more round on one piece. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Adopt an allocation policy, or keep the incumbent and protect the remaining budget.

## 12. Bind acceptance to the actual artifact and evidence

Origin: V4. Research/engineering reuse: Reuse existing hash/integrity tests and corrected telemetry. This is a correctness control, not an unproven quality lift.

1. **What exact claim are you testing?** A passing verdict cannot be reused after its candidate, requirement, reference or test identity changes.
2. **Compared with what?** Current conscientious verification versus automated identity checking, exercised on controlled stale/current evidence pairs.
3. **What result would make you stop?** Metric and advance/stop rule: Zero stale-evidence acceptances and zero valid-evidence rejections on the frozen replay set; hash/cost reconstruction must reconcile. Stop paid investigation if current tests already establish the property. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: False accepts, needless revalidation, encoding/hash mistakes and evidence that cannot be reconstructed.
5. **What did this really cost?** Proposed allowance: L; no new benchmark calls. Existing implementation validation is reusable, not billed as a new discovery. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Make the validated binding an invariant for retained candidates, checkpoints and later acceptance.

## 13. Retain the best verified candidate

Origin: V4. Research/engineering reuse: Reuse saved rescues/spoils and engineering replay; no inspected paper directly proves this local retention policy's economic value.

1. **What exact claim are you testing?** Keeping a verified checkpoint prevents a later revision from replacing a better deliverable with a worse one.
2. **Compared with what?** Latest-candidate selection versus best-so-far selection using only development evidence available during the run; held-out grades remain unavailable for selection.
3. **What result would make you stop?** Metric and advance/stop rule: On frozen regressions, retain a valid candidate without losing verified improvements. A paid screen must meet G; report final Q and selection overhead on new work. Stop if selection merely overfits development tests. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Regressions retained, genuine improvements rejected, stale validation and storage/recheck overhead.
5. **What did this really cost?** Proposed allowance: L first; S only if further local selection uncertainty matters. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Keep the minimal selection rule and establish a dependable recovery point.

## 14. Recover from interruption

Origin: V4/V5 checkpoints. Research/engineering reuse: Reuse existing checkpoint contracts and deterministic recovery methods; no imported success rate.

1. **What exact claim are you testing?** Resuming a valid checkpoint reduces repeated work while preserving obligations and prior spending.
2. **Compared with what?** Resume versus restart at identical declared interruption points in scratch work, with the same final acceptance checks.
3. **What result would make you stop?** Metric and advance/stop rule: At least 50% lower post-interruption duplicate work/cost, no lost obligations and no duplicate external effect in the simulated fault set. Report original sunk cost separately; do not infer natural interruption frequency. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Lost state, stale context, duplicate actions, invalid resumes and overhead on runs that never interrupt.
5. **What did this really cost?** Proposed allowance: L replay first; S if actual context restoration requires model calls. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Adopt recovery if useful; distinguish measured recovery benefit from assumed everyday savings.

## 15. Choose light versus heavier effort

Origin: V5 initial routing. Research/engineering reuse: R8 motivates routing by task structure; its fitted selector is not a deployable free oracle for our tasks.

1. **What exact claim are you testing?** A simple route chosen from pre-run observable task properties reduces cost on a declared workload mix without lowering acceptance.
2. **Compared with what?** Best fixed route versus a frozen routing rule, same underlying models/tools/total ceilings. Count light-to-compact escalation as part of the policy.
3. **What result would make you stop?** Metric and advance/stop rule: At least 25% lower cost per accepted task with no lower Q in either predeclared easy or coupled stratum in the screen; confirm later. Stop if the rule uses hindsight or its own unvalidated difficulty score as ground truth. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Hard tasks underfunded, easy tasks overprocessed, misrouting, escalation cost and imbalance between task strata.
5. **What did this really cost?** Proposed allowance: S only after sufficient observed workload variety; otherwise L and defer. No learned router built from a handful of cases. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Use the routing rule only where evidence supports it; keep a fixed fallback.

## 16. Limit unsupported repeated judgments

Origin: V5 evidence ladder. Research/engineering reuse: R4/R6/R7 support skepticism about repeated opinions, not this exact ladder.

1. **What exact claim are you testing?** Making uncorroborated late-round judgments advisory reduces needless revision without hiding real defects.
2. **Compared with what?** Same naturally occurring third-review checkpoint, incumbent with the ladder disabled versus enabled; preserve concrete failing checks in both.
3. **What result would make you stop?** Metric and advance/stop rule: At least 25% lower remaining-stage cost with no lower final Q and no skipped confirmed failure. Defer if eligible checkpoints do not occur; never manufacture a long loop to justify the feature. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Valid concerns dismissed, unsupported edits avoided, defects missed and costs merely moved into another round.
5. **What did this really cost?** Proposed allowance: L on existing traces; S only when eligible cases exist. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Adopt or defer the ladder independently of initial routing and portfolio budget allocation.

## 17. Reuse verified lessons across tasks

Origin: V4/V5 optional memory. Research/engineering reuse: R3 offers limited precedent for reflection/memory; it does not prove cross-repository lesson transfer.

1. **What exact claim are you testing?** A small frozen collection of relevant verified lessons improves future work enough to pay for retrieval.
2. **Compared with what?** Incumbent with no retrieved lesson versus the same system with provenance-checked relevant lessons; use untouched future tasks and include retrieval cost.
3. **What result would make you stop?** Metric and advance/stop rule: Meet G, with zero uses of frozen invalid/stale lessons in a controlled probe. Defer without a relevant validated corpus; do not build a database merely to reach this milestone. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Negative transfer, irrelevant context, stale knowledge, contamination of confirmation tasks and retrieval overhead.
5. **What did this really cost?** Proposed allowance: L corpus audit; S only with a usable corpus and fresh tasks. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Enable selective memory or leave it off. A past success is not automatic authority.

## 18. Allocate model capability economically

Origin: Beyond fixed-model mechanism tests. Research/engineering reuse: R5/R8 motivate joint cost/quality analysis; current role-level crossover must be measured.

1. **What exact claim are you testing?** Using cheaper models in validated roles, with bounded escalation, lowers total cost without degrading delivery.
2. **Compared with what?** The earned configuration on one fixed strong model versus a frozen mixed-model assignment. Change model allocation here, not silently during earlier mechanism tests.
3. **What result would make you stop?** Metric and advance/stop rule: At least 25% lower cost per accepted task with no lower Q or critical regression; charge retries, escalation, tool and context costs. Stop on unknown model identity or an apparent saving that disappears after retries. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Weak builders creating expensive repair, unreliable judges, escalation loops and provider-specific failures.
5. **What did this really cost?** Proposed allowance: S only after current prices and limits are quoted; inadequate per-run capacity means re-scope before spending. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Keep the assignment only in validated roles; test the combined surviving system.

## 19. Confirm the integrated surviving configuration

Origin: Whole-system validation. Research/engineering reuse: R5's holdout/reproducibility principles; old screens cannot serve as independent confirmation.

1. **What exact claim are you testing?** The selected combination retains its advantage end to end on untouched tasks, rather than depending on isolated feature wins.
2. **Compared with what?** Complete surviving system versus the strongest simple incumbent, same environments and resources; include a second relevant repository/context and later a fixed second-model replication.
3. **What result would make you stop?** Metric and advance/stop rule: Choose one primary claim and sample-size/interval plan before seeing confirmation data. For a superiority claim require its prespecified confidence bound to clear the quality/cost hurdle; otherwise report inconclusive. A six-pair screen alone does not guarantee that bar. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Feature interactions, prompt growth, repository/model dependence, incomplete runs and gains that vanish on fresh tasks.
5. **What did this really cost?** Proposed allowance: The prior $36 confirmation reservation remains deferred, not saved. It buys at most six pairs at the planning cap; quote and fund additional required sample size separately. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Authorize a narrowly supported release/user pilot, request justified further evidence, or roll back the combination.

## 20. Demonstrate independent user value and reuse

Origin: Product evidence; includes V5.1 usability. Research/engineering reuse: Research cannot establish these users' demand, willingness to pay, or onboarding success.

1. **What exact claim are you testing?** People outside the development process can use the method and voluntarily return because it reduces effort on their own work.
2. **Compared with what?** Five prospective users' normal workflow versus the selected method on paired real tasks, with blind acceptance where practical; record onboarding separately.
3. **What result would make you stop?** Metric and advance/stop rule: Proposed early signal: at least 3/5 voluntarily reuse on a second task, at least 25% lower observed active human effort without lower acceptance, and an actual paid pilot if making a willingness-to-pay claim. This is not proof of product-market fit. Common rule: stop at the cap, on an invalid comparison, or on an unmet predeclared gate; retain contrary evidence.
4. **Where did your approach lose?** Local outcome: not yet measured unless existing evidence is explicitly identified. Report: Non-adoption, setup friction, support/maintenance burden, unpaid enthusiasm, negative task outcomes and failed independent replication.
5. **What did this really cost?** Proposed allowance: No blanket model or participant budget: quote the pilot and investigator/user time before recruitment. No outreach or paid trial is authorized by this roadmap. Actual attributable research/execution/evaluation/human costs must be appended; a ceiling is not a bill.
6. **What decision does the next expenditure enable?** Fund a narrow product, publish a bounded research result, simplify the offering, or stop commercial expansion.

## Immediate decision

Close the broad novelty questions in milestones 1–2 through research reuse. Do not rerun published demonstrations merely to tell the same story. Complete only the missing transfer/readiness checks for milestone 3; dispatch its bridge only when a concrete budget and task set are selected.

Reuse the existing isolation/accounting/identity checks immediately. Do not wait for their numbered audit slots. Most later milestones remain deferred until real failures or workload conditions justify them. The exact package can lose while a useful component survives, and the final useful product can be much smaller than the accumulated historical skill.

After every round, publish a compact investor record using the six exact questions, with the artifact/data links, actual cost categories, observed losses, decision, and proposed next allocation. “No further spending justified” is a valid and useful result.
