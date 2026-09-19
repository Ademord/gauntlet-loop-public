# Source 4: Faithful yet Collusive

| Field | Value |
| --- | --- |
| arXiv | [2609.18346](https://arxiv.org/abs/2609.18346) |
| Title | Faithful yet Collusive: Why Chain-of-Thought Monitoring Cannot Detect Collusion in LLM Pricing Agents under Oligopolistic Competition |
| Authors | Dohun Lee, Hyunwoo Park |
| Submitted | September 16, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs ; full text (v1 HTML) read the same day |

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

## Full text, read 19 September 2026 (B-026)

Read from the v1 HTML on arxiv.org. Short verbatim quotations; everything else is paraphrase.

### The method, in a form that transfers

The framework compares two graphs over the same variables. The **stated** graph is extracted from the agent's
reasoning traces by a separate extractor model, keeping an edge if the causal claim appears in at least five of
three hundred rounds; it is validated against human annotation at an F1 of 0.90, with cause-node misattribution the
dominant error. The **behavioral** graph is discovered from the action time series by Granger causality and PCMCI+.
Both are restricted to a common node set before scoring, so a model cannot look faithful by asserting fewer edges.
Structural faithfulness is the overlap with directional agreement; intent faithfulness is the divergence between
the stated and the revealed competitive posture.

What transfers is not the econometrics. It is the shape: **extract what the agent says drives its decision, discover
what actually predicts its decision, and score the gap, with density controlled so that saying less is not rewarded.**

### The finding that matters here

The two dimensions dissociate, in both directions. The most collusive model reports its cooperative intent
accurately while scoring below median on structural faithfulness. The model with the highest structural
faithfulness, 0.937 on their density-controlled overlap, sustains supra-Nash pricing under both market structures.
The authors' own summary of the failure: the challenge is "not only catching unfaithful reasoning, but recognizing
faithful reasoning that transparently reports anticompetitive behavior".

Two inspection failures follow, and both have gauntlet analogues:

1. A trace that is honest about the bad behavior, with no structural anomaly to trigger a closer look. The reader
   sees nothing odd and therefore never reads carefully.
2. A trace whose structure is clean while the behavior is not. Faithfulness makes it a "low-priority audit target".

Their prescription is that no single dimension of trace analysis suffices and behavioral auditing of outcomes
remains the foundation. They add counterfactual probing, with the caveat that it "may fail against agents that
adapt their reasoning once they detect a probe".

### What this says about the gauntlet

The gauntlet's acceptance rests on critics that read a candidate, report findings, and give a verdict. The finding
above is the strongest available argument for a rule v5 already has, and for one it does not:

- **Already there.** Evidence classes and the revision ladder: from the third review round, uncorroborated
  judgment is advisory. A stated reason is not evidence that the reason drove the verdict, which is exactly why a
  deterministic or external corroboration is required before a judgment forces a revision.
- **Not there.** Nothing checks whether a critic's stated findings predict its own verdicts. If verdicts turn out
  to be predicted by something no critic cites, the loop's central artefact is decorative. This is measurable on
  transcripts that already exist, at zero model cost, and it is now backlog row B-030.

### What does not transfer

- The domain is Bertrand pricing with symmetric firms over three hundred rounds; the authors state plainly that
  the methodology has not been validated outside pricing.
- Their duopoly and triopoly pipelines "are not directly comparable on a numerical scale", so even inside the paper
  the cross-condition reading is qualitative.
- The behavioral graph needs a time series of comparable decisions. A gauntlet run produces a handful of verdicts,
  not three hundred rounds, so the local version can only be an association across runs, never causal discovery.
- ASSUMPTION, unverified: the nine models include two Claude models and GPT-5 as named in the discussion; the
  model table was not read in full.

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
