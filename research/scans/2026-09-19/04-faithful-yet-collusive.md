# Source 4: Faithful yet Collusive

| Field | Value |
| --- | --- |
| arXiv | [2609.18346](https://arxiv.org/abs/2609.18346) |
| Title | Faithful yet Collusive: Why Chain-of-Thought Monitoring Cannot Detect Collusion in LLM Pricing Agents under Oligopolistic Competition |
| Authors | Dohun Lee, Hyunwoo Park |
| Submitted | September 16, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> Large language models (LLM) deployed as autonomous pricing agents may sustain supracompetitive prices through tacit coordination. We develop a causal graph divergence framework that separately measures structural faithfulness and intent faithfulness of LLM pricing agents in Bertrand competition. Across nine LLMs under duopoly and triopoly conditions, collusive behavior and chain-of-thought (CoT) faithfulness dissociate along both dimensions: the most collusive model accurately reports cooperative intent yet reasons structurally unfaithfully, while the most structurally faithful model sustains supra-Nash pricing under both market structures. These findings establish that CoT monitoring alone cannot serve as a standalone safeguard against algorithmic collusion.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| pricing agents can behave collusively even when their chain-of-thought looks faithful | title and closing sentence | matches |
| published September 16 | arXiv submission date is September 16, 2026 | matches |
| nine LLMs as autonomous pricing agents in Bertrand duopoly and triopoly markets | "Across nine LLMs under duopoly and triopoly conditions" in "Bertrand competition" | matches |
| measures whether the stated reasoning structurally reflects behavior and whether the model honestly reports cooperative intent | "separately measures structural faithfulness and intent faithfulness" | matches |
| the most collusive model can accurately report cooperative intent | "the most collusive model accurately reports cooperative intent yet reasons structurally unfaithfully" | matches; the scan omits the second half |
| the most structurally faithful model still sustains prices above the Nash competitive level | "the most structurally faithful model sustains supra-Nash pricing under both market structures" | matches |

## What the abstract does not establish

- A simulated Bertrand market, not a real one. No claim is made about deployed pricing systems, and no legal conclusion about collusion follows.
- "The most collusive model" and "the most structurally faithful model" are extremes of a nine-model sample. The abstract gives no correlation across the nine, so the dissociation is shown by counterexample rather than by a measured relationship.
- No numbers appear in the abstract: no price levels, no faithfulness scores, no confidence intervals.
- The framework measures faithfulness of stated reasoning against a causal graph the authors construct. That construction is itself a modeling choice the abstract does not describe.
- ASSUMPTION: the agents set prices repeatedly against each other rather than once; tacit coordination presumes repetition.

## Where the skill already stands

The entrypoint's first paragraph says a critic's confidence, a longer process, or repeated agreement does not establish quality, and v5 classes findings by the observation that produced them rather than by how convincing they read. The software-quality reference already refuses to let a story stand in for behavior: "Do not claim a live checkout, completed transaction, real reward credit, or native platform behavior from a simulation," and it separates intercepted fixtures, simulated events, live pages, and authenticated end-to-end behavior in the evidence record.

## The gap

The skill's distrust of stated reasoning is aimed at critics judging an artifact. It says nothing about a deliverable that itself acts in an external system and explains itself: a pricing helper, a bidding or scheduling tool, an allocation script. For that class, the acceptance checks would naturally be written against the agent's logs and stated intent, which this paper shows is the wrong surface. The evidence is behavioral: what prices, allocations, or bids actually came out, across the market conditions that matter.

## Proposed change (adapted, not copied)

1. A selectable check class in the software-quality reference for deliverables that act in a market or allocate a shared resource: acceptance requires observed outcomes across at least two conditions of the environment, recorded as data, and never the agent's own explanation of what it intended.
2. Where the deliverable is an agent, its stated reasoning may be recorded as context, always classed `judgment`, never as evidence for a behavioral check.
3. Nothing here is on by default: it is selected like CI or a hosted demo, and only when the product acts rather than advises.

## Judgment on adoption

Adopt as a small, selectable extension in the next upgrade. The transfer is narrow and honest: the paper is about pricing agents, and the rule it supports is one the skill half-states already for simulations. The cost is a short subsection in an optional reference. Falsifier: if no deliverable of this class ever appears in this owner's work, the subsection is dead weight and should be dropped rather than defended. Backlog row: B-024.
