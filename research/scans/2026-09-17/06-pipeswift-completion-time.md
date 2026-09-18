# Source 6: PipeSwift, completion-oriented agent serving

| Field | Value |
| --- | --- |
| arXiv | [2609.16491](https://arxiv.org/abs/2609.16491) |
| Title | PipeSwift: Revisiting Pipeline Parallelism for Large-Scale Completion-Oriented Agentic LLM Serving |
| Authors | Shiju Wang, Fei Ren, Fangcheng Fu, Zhanhong Tan, Kairui Li, Jingwei Cai, Kaisheng Ma |
| Submitted | September 15, 2026 (v1); September 16, 2026 (v2) |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

The arXiv abstract page renders the system's name as the unexpanded LaTeX macro `\name{}` in two places; both are expanded to "PipeSwift" below. Everything else is character-identical to the page.

> LLM agents execute long-horizon workflows where each model response determines the progress of subsequent tool interactions and environment transitions. Unlike chatbot serving, where TTFT and TPOT SLO constraints are critical, agentic workloads are increasingly governed by completion time. This shift challenges existing LLM serving designs, which are optimized around token-level SLOs. We revisit scheduling and parallelism under this completion-oriented objective. Through systematic exploration, we show that job completion time (JCT) is governed by the balance between prefill and decode efficiency. Prefill-prioritized scheduling, while achieving the best TTFT and decode throughput, renders suboptimal JCT; across the scheduling-policy space, completion time varies by up to 1.40×, with the optimum at neither extreme. We further show that pipeline parallelism (PP), previously overlooked due to its limited decode latency advantage, benefits JCT by providing a favorable balance of prefill–decode trade-off. Based on these insights, we build PipeSwift, an optimized open-source pipeline-parallel runtime that co-designs scheduling and parallelism through a JCT-aware scheduling layer and pipeline-integrated multi-token prediction. Evaluated on deterministic replays of real coding and web-search agent trajectories with two 360B+ MoE models on 64 H800 GPUs, PipeSwift reduces overall JCT by up to 1.45× over SGLang wide-EP, 2.33× over vLLM PP2, and 1.54× over today's state-of-the-art open-source PD-disaggregated deployment.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| scheduling optimized for first-token latency can worsen end-to-end completion | "Prefill-prioritized scheduling, while achieving the best TTFT and decode throughput, renders suboptimal JCT" | matches |
| completion varied by as much as 1.40x across policies | "completion time varies by up to 1.40×" | matches |
| two 360B+ MoE models, 64 H800 GPUs | same | matches |
| 1.45x vs SGLang wide-EP, 2.33x vs vLLM PP2, 1.54x vs PD-disaggregated | same figures | matches |

## What the abstract does not establish

- This is a serving-systems result. Nothing a prompt-level workflow controls (scheduling policy, parallelism, multi-token prediction) is involved. The transferable content is the objective: the unit of work is the completed job, and optimizing per-response metrics can make it worse.
- Only the abstract was read.

## Where v4 already stands

v4: "Parallelize independent branches of work and serialize dependencies"; budgets are in reviews and observable requests; no time accounting; "Integration is its own dependency, not the sum of piece approvals."

## The gap

v4 accounts in reviews and requests, never in completion. It gives no guidance on what to do while a critic or a slow environment check is running, and its milestone record has no wall-clock. A run can be locally efficient (every agent responds fast) and globally slow (everything waits on one review).

## Proposed v5 change (adapted, not copied)

1. Dispatch around the critical path: when a piece is waiting on a slow check or review, start the next independent build or review instead of idling the run; never block the whole run on one review when independent work exists.
2. Record run start/stop and per-piece completion time in state and the milestone summary, or `unknown`.
3. State the objective: the unit optimized is the accepted piece and the delivered run, not any agent's response time. Do not shorten reviews or builds to make individual steps look fast.

## Judgment on adoption

Adopt as a small guidance and recording change only. Anything larger (a scheduler, an orchestration graph) is what v4 explicitly refuses to build without a demonstrated need, and this source does not demonstrate one at the workflow level.
