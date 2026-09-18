# Source 3: LIMBO, memory as an inference-time budget

| Field | Value |
| --- | --- |
| arXiv | [2609.14138](https://arxiv.org/abs/2609.14138) |
| Title | LIMBO: Lifelong Inference-Time Memory and Budget Optimization for LLM Agents |
| Authors | Siddharth Sharma, Nilesh Prasad Pandey, Onat Gungor, Tajana Rosing |
| Submitted | September 12, 2026 |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> As LLM agents become integrated into increasingly complex workflows, they must continually acquire new capabilities while retaining competence on previously learned tasks. Lifelong agents address this through experience replay, injecting past interactions into the prompt to leverage prior experience during inference. However, replay is not free: every replayed trajectory competes with retrieval, reasoning, tool use, and verification for the same limited prompt and compute budget, making effective resource allocation essential. Existing approaches allocate these resources using fixed replay policies, regardless of whether replay is beneficial for the current task. We identify this as inference-time memory allocation, a distinct problem class for lifelong agents, and introduce LIMBO: the first online framework to our knowledge that treats memory as a controllable inference-time resource and jointly optimizes memory strategy and inference budget for each incoming task. Unlike prior approaches that fix the replay policy or require model weights, teacher supervision, or offline retraining, LIMBO learns this allocation online in a single pass, explicitly balancing task performance and inference cost without modifying the underlying agent. Across three LLM backbones on LifelongAgentBench, LIMBO achieves better cost-accuracy tradeoffs than state-of-the-art memory-augmented baselines and nearly matches all strongest such baselines at up to ~83% lower inference cost (~53% on average). LIMBO adapts its policy across models and environments without retraining, demonstrating that effective allocation can be learned online rather than manually specified.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| replay competes with reasoning, verification, retrieval, tool-use tokens | "every replayed trajectory competes with retrieval, reasoning, tool use, and verification for the same limited prompt and compute budget" | matches |
| learns online, task by task, no retraining, no teacher | "learns this allocation online in a single pass ... without modifying the underlying agent" | matches |
| three backbones, LifelongAgentBench | same | matches |
| nearly matched strongest memory-heavy systems at up to ~83% less cost, ~53% average | "nearly matches ... at up to ~83% lower inference cost (~53% on average)" | matches; the headline is a cost result, accuracy is "nearly matches" |

## What the abstract does not establish

- The memories are replayed trajectories from a benchmark of related tasks; Gauntlet's lessons are short curated procedures with triggers. The token competition argument transfers; the learned policy does not, because Gauntlet has no per-task reward to learn from online.
- "Nearly matches" means some accuracy is traded for cost. The abstract does not give the accuracy delta.
- Only the abstract was read. ASSUMPTION: the online policy uses a bandit-style signal from task outcomes.

## Where v4 already stands

v4 learning is off by default and, when on, "retrieve only relevant valid entries", "Read only the relevant subset; record selected IDs/versions in the run contract", and "Stored history is not automatically active guidance." Retrieval is filtered by applicability before similarity. This is already a narrow policy.

## The gap

v4 has no allowance on how many lessons enter a piece's context, does not charge retrieval against the piece's budget or say that retrieval competes with test runs and reference comparisons, and does not record whether a retrieval was worth its cost. A run with a large active lesson set will silently spend context on memory.

## Proposed v5 change (adapted, not copied)

1. Retrieval allowance: at most three active lessons per piece enter working context by default, ranked by applicability, then validity, then evidence freshness. More requires a recorded reason. The number is an editable engineering default, like the review budgets.
2. Retrieval is an event: lesson ID/version, why it was selected, and its cost (observable tokens or `unknown`) are recorded and count against the piece's observable request allowance where telemetry exists.
3. Skip retrieval for a `light` topology piece unless a lesson's `applies_when` trigger is matched by an observed condition, not by semantic similarity alone.
4. Each retrieval outcome is written to the lesson's utility ledger (source 4), so that the allowance can later be tuned from evidence rather than set once.

## Judgment on adoption

Adopt the allowance and the recording; reject the learned allocation policy. The allowance is the manual, disclosed version of what LIMBO learns. It is cheap, it makes memory cost visible, and it produces the record a learned policy would need. Setting the default to three is a choice, not a measurement.
