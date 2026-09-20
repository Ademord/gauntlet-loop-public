# Calibration decision, 20 September 2026

Accept the measurement repairs and controlled comparison tooling. Stop this calibration at its six planned tasks. Keep production skill 5.1.0 unchanged. The experiment shows concrete benefits and risks of additional work, but does not establish that Gauntlet's orchestration improves representative development performance.

## Frozen primary result

All six tasks completed in all three branches, with all frozen behavioral tests passing and no scope violations. There were no rescues or spoils on those tests. The runner executed 24 successful calls, with no delegated agents inside a stage. See the [generated report](runs/2026-09-20-pilot-02/REPORT.md) and [derived analysis](runs/2026-09-20-pilot-02/analysis.json).

| Branch across six tasks | Frozen test passes | CLI usage cost | Summed stage time |
| --- | ---: | ---: | ---: |
| Initial build | 6/6 | $0.9802 | 8.46 min |
| Build + self-check | 6/6 | $2.8242 | 23.59 min |
| Build + fresh review + correction | 6/6 | $3.3463 | 27.15 min |

Costs are CLI-reported API-equivalent usage, not verified subscription charges. Each hypothetical branch includes its shared build, which physically ran once. Pilot 02 cost $5.1903356; the earlier stopped attempt and diagnostics cost $0.577671, for $5.7680066 total against the $15 ceiling. Time sums observed sequential calls, excludes setup/grading, and does not estimate parallel throughput. The extra-work branches had equal $0.85 ceilings per task, but did not spend equal amounts.

These are constructed small tasks, not a representative sample. Their frozen scores are at a ceiling. Six observations cannot establish equivalence, and passing these tests does not establish full contract correctness.

## Concrete findings outside the frozen score

Supplementary probes expose both useful repairs and missed grading coverage:

| Case | Initial build | Self-check | Fresh review + correction |
| --- | --- | --- | --- |
| c002: equal large finite amounts | fails | passes | passes |
| c004: 400-digit hour count | raises instead of returning `unknown` | passes | passes |
| c006: deep dependency chain/cycle | wrong exception | passes | passes |
| c004: nonbreaking whitespace between number and unit | passes | rejects a permitted input | passes |

The [c002 probe](runs/2026-09-20-pilot-02/supplementary-c002.json) was independently selected during grader review before that reviewer inspected candidates. The other [findings](runs/2026-09-20-pilot-02/supplementary-findings.json) were selected after reading final stage messages and patches, then applied equally to every branch and the reference. They are concrete error analysis, not unbiased estimates of relative performance. None changes the frozen primary scores.

The c004 critic identified the overflow; the c006 critic reported recursion depth as a robustness concern. The self-check independently fixed both. On c002, the critic reported no violation, and both continuation builders found the precision defect themselves. The c004 self-check also introduced `re.ASCII`, incorrectly extending the contract's ASCII-digit restriction to whitespace. The reference shares that whitespace limitation; c002 and c006 references also fail their supplementary boundaries. Reference/hidden-test coauthorship did not provide sufficient independent coverage.

Thus extra work demonstrably repaired some saved candidates, and one extra pass also introduced a regression. There is no basis for claiming that all extra work was wasted, that an independent critic caused every repair, or that this selected set proves a general advantage over self-checking. The [final messages](runs/2026-09-20-pilot-02/stage-summaries.jsonl) are model self-reports; the saved code and equal probes verify the behaviors above.

## What is now reliable, and what comes next

Historical token totals now use complete reconciled model usage: 217,433,726 across 76 counted arms, replacing the incomplete 150,771,035. Original observations are untouched. Changed prompts are rejected before paid dispatch, held-out failures prevent acceptance, and dispatch counts are no longer presented as verified review counts. The new controller fixes stage boundaries, isolates continuations and graders, records identities, and accounts for inherited session counters. The [measurement replay](../paired-study/measurement-replay.md) and [protocol](PROTOCOL.md) give the exact boundaries.

Both attempts retain frozen source snapshots. A Windows newline hash defect was found in final review: original transcript hashes identify normalized text. Derived evidence indexes verify them and record actual saved-byte hashes; the future controller hashes bytes directly. No observation or experimental artifact was rewritten to improve a score.

The next performance experiment should sample real development tasks independently of whether a critic is likely to find a bug. Freeze task IDs, eligibility rules, budgets and independently authored acceptance checks before solving; keep confirmation tasks untouched. Compare a capable build, additional self-checking, and fresh review with correction on accepted outcomes, cost, latency and regressions. Specify a meaningful effect and sample-size plan for that task population before making a performance claim. Do not search for harder synthetic cases until a preferred treatment wins, add orchestration rules from this pilot, or start another paid run automatically.

The immediate engineering deliverable is a trustworthy way to test the idea. The next research contribution must be evidence about when the additional coordination earns its cost.
