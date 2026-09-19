# Source 1: Continual Enterprise World Model Discovery in Dynamic Systems

| Field | Value |
| --- | --- |
| arXiv | [2609.19551](https://arxiv.org/abs/2609.19551) |
| Title | Continual Enterprise World Model Discovery in Dynamic Systems |
| Authors | Shambhavi Mishra, David Vazquez, Perouz Taslakian, Marco Pedersoli, Jose Dolz, Issam H. Laradji |
| Submitted | September 17, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> In an enterprise system, updating one field can set another, create a record, or start an approval. These effects are produced by business rules that are not built into the platform but written by each organization and revised over time. An agent working in such a system cannot predict the result of its own actions without knowing these rules. We study continual enterprise world model discovery, where an agent starts without knowledge of these business rules and discovers them by interacting with records and observing the outcomes. From those observations it builds a world model, which it revises as the rules change. To evaluate this, we introduce EnterpriseWorldShift, built on a live ServiceNow environment with nine tables, 25 hidden rules and 600 evaluation actions. It presents four versions of the same enterprise world, with the tables and records held fixed while a rule is modified, then added, then removed, so that discovery, revision, extension and retirement are each tested in turn. Our Continual Discovery Agent (CDA) builds such a model and carries it from one world to the next. It predicts the effects of the hidden rules more accurately than looking them up for each question, the approach taken by prior work, by up to 8.98 IoU points, and it answers from its own model without querying the running system.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| an agent learns the hidden rules of a live enterprise system and updates the model as rules change | "discovers them by interacting with records and observing the outcomes. From those observations it builds a world model, which it revises as the rules change" | matches |
| announced September 18, 2026 | arXiv submission date is September 17, 2026 | differs: the scan gives an announcement date, the paper's own date is a day earlier |
| live ServiceNow environment with 9 tables, 25 hidden business rules, 600 evaluation actions | "a live ServiceNow environment with nine tables, 25 hidden rules and 600 evaluation actions" | matches |
| four versions: a rule modified, added, removed | "four versions of the same enterprise world ... a rule is modified, then added, then removed" | matches; the four phases are discovery, revision, extension, retirement |
| up to +8.98 IoU points over a lookup-at-question-time approach | "more accurately than looking them up for each question, the approach taken by prior work, by up to 8.98 IoU points" | matches; "up to" is an upper bound, not a mean |
| the agent can answer from its own model without querying the live system | "it answers from its own model without querying the running system" | matches |

## What the abstract does not establish

- One platform, one benchmark, built by the authors. Nothing shows the result holds outside a ServiceNow-style rule engine where effects are discrete and observable.
- "Up to 8.98 IoU points" is a maximum over conditions. The abstract gives no mean, no spread, and no cost of the discovery interactions.
- IoU over predicted effects is a proxy for usefulness. It says nothing about whether an agent acting on the model does better work.
- Answering "without querying the running system" is a speed and load argument, not a correctness argument: a stale model answers confidently from memory, which is the failure mode the revision phases are meant to catch. The abstract does not report how quickly the model detects a changed rule.
- ASSUMPTION: the model is an explicit rule structure rather than weights, which is how the scan reads it and how the title suggests; only the abstract was read.

## Where the skill already stands

The learning reference prefers executable state over prose memory: "Prefer executable state such as repository files, validated configuration, schema, or constraint models when these are the thing being operated on." Lessons carry `applies_when`, `procedure`, `verification`, an `environment_probe` with an environment identity and a timestamp, `recheck_when`, and statuses including `superseded` and `invalidated`, so a lesson that stops holding can be retired. Retrieval is narrow: at most three lessons per piece, applicability before similarity.

## The gap

Lessons are independent statements about what to do. Nothing in v5 records what the environment does: which action produces which side effect, which precondition gates it, and when that last held. So a run cannot predict the effect of its own action, and two lessons about the same mechanism sit side by side with no way to notice they contradict. The environment probe checks a lesson at admission; there is no object that the probe revises.

## Proposed change (adapted, not copied)

1. An optional `environment_model` under a project's learning records: entries of `action -> precondition -> observed effect`, each with the environment identity where it was observed, the observation that produced it, and a last-confirmed date.
2. Entries are written only when a run is surprised twice by the same mechanism, which keeps the model small and tied to real friction.
3. A contradicted entry is revised or retired in place, with the old text and the contradicting observation kept, exactly as lesson supersession already works.
4. No discovery campaign: entries come from work that was happening anyway. Nothing probes an environment to fill the model.

## Judgment on adoption

Defer, with a small first step. The mechanism is right for long-lived projects, and the paper's own evidence is one platform with a benchmark the authors built. The cheap version is the `environment_model` record above, gated on repeated surprise. Falsifier: entries that are never consulted by a later run, or never revised when the environment changes, mean the model is decoration; the utility ledger already provides the retrieval-outcome record that would show it. Backlog row: B-021.
