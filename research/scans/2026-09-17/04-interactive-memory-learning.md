# Source 4: Interactive Memory Learning (ICML), delayed reward for memory decisions

| Field | Value |
| --- | --- |
| arXiv | [2609.17088](https://arxiv.org/abs/2609.17088) |
| Title | Interactive Memory Learning for Long-Term Conversations |
| Authors | Cai Ke, Jiangyue Yan, Han Zhang, Xin Liu, Zike Yuan, Yue Yu, Hui Wang, Ruifeng Xu |
| Submitted | September 15, 2026 |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> Recent advancements in large language models have significantly enhanced the capabilities of agents in modeling long-term conversations. Despite these successes, existing approaches typically adopt a static heuristic paradigm, where information is passively archived without adaptive memory valuation. Consequently, these methods fail to self-evolve or align their memory management with evolving user needs. To address this, we propose ICML (InteraCtive Memory Learning), a multi-agent framework that transforms the memory mechanism from a passive archive into a learnable, interactive memory policy. Specifically, we first employ a session synthesis pipeline to generate expert data, facilitating rapid test-time adaptation in unseen scenarios. Building on this, ICML utilizes an online reinforcement learning mechanism where a Planner agent selectively encodes high-value information and a Trigger agent dynamically retrieves it to optimize response quality, whereby the two agents co-evolve through continuous interaction feedback. Crucially, both agents are synchronized through a delayed reward mechanism that propagates future feedback back to earlier storage decisions, ensuring memory policies are precisely aligned with user expectations. Experimental results demonstrate that ICML significantly outperforms strong baselines, exhibiting the unique capability to continuously improve response quality as interactions accumulate.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| one agent decides what to store, another decides when to use it | "a Planner agent selectively encodes high-value information and a Trigger agent dynamically retrieves it" | matches |
| the writer does not get its definitive reward immediately; later interactions reveal usefulness and propagate back | "a delayed reward mechanism that propagates future feedback back to earlier storage decisions" | matches |
| agents keep updating during interaction rather than fixed heuristics | "online reinforcement learning ... co-evolve through continuous interaction feedback" | matches |
| "ICML has ..." | ICML here is the method's acronym, not the conference | wording in the scan is ambiguous; corrected here |

## What the abstract does not establish

- The domain is long-term *conversation* and the reward is response quality. Gauntlet lessons are engineering procedures whose value is whether a later run avoided a defect or saved rounds. The delayed-reward idea transfers; the RL machinery and the synthesized expert data do not.
- No numeric result is given in the abstract. "Significantly outperforms strong baselines" is unquantified here.
- Only the abstract was read. ASSUMPTION: the paper's reward is an LLM-judged or human-rated response score.

## Where v4 already stands

v4 lesson lifecycle: `candidate | experimental | active | disputed | superseded | invalidated | rejected | retired`; admission requires an environment probe and an independent reviewer; "Claims that a procedure improves future performance remain hypotheses until supported by separate relevant use"; contrary evidence is preserved.

## The gap

v4 admits lessons on how sound they look at write time (probe passes, reviewer agrees). Nothing in v4 records what happened when the lesson was later retrieved, nothing demotes a lesson that is repeatedly retrieved and never helps, and the sentence about "separate relevant use" has no record to point at. Value is assigned at storage time, which is exactly the "static heuristic paradigm" the paper criticizes.

## Proposed v5 change (adapted, not copied)

1. Lesson record gains `utility_ledger`: a list of `{run, piece, retrieved_at, applied, outcome, evidence}` with `outcome` in `prevented_defect | reduced_rounds | neutral | irrelevant | harmful | unknown`.
2. Promotion `experimental -> active` requires at least one `prevented_defect` or `reduced_rounds` entry from a run other than the lesson's source run, with evidence, in addition to v4's probe and review.
3. Two consecutive `irrelevant` retrievals lower the lesson's retrieval priority (status unchanged). One evidenced `harmful` entry moves the lesson to `disputed` and quarantines it from retrieval until reviewed.
4. Disclosure: ledger outcomes are the lead's recorded attribution and are confounded by everything else in the run. The ledger prioritizes retrieval; it does not prove causal value.

## Judgment on adoption

Adopt as a manual ledger, not as learning. This is the smallest change that makes "separate relevant use" a checkable thing. The cost is a few lines per retrieval. The main risk is attribution noise, which is disclosed in the record itself.
