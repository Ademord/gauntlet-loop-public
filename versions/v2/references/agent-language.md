# Auditable agent-language experiment

Use for a requested language pilot or a recurring coordination problem worth testing. This is an optional experiment within an authorized task, not a prerequisite to normal work or a claim of better performance. It does not authorize a persistent swarm, extra background runs, new communication channels or global self-modification. A request to update the skill adds the procedure; it does not itself run a research campaign.

Agents may invent new tokens, a grammar and composition rules instead of only abbreviating English. The objective is accurate, efficient coordination. Human incomprehensibility is not a success criterion. Keep agent messages readable and retain a plain-language expansion inline; user updates, approvals, dissent, acceptance verdicts and final answers stay in ordinary language. Preserve spaces and labels so the messaging UI remains legible.

## Start from a real coordination need

Choose a bounded repeated exchange, such as a file handoff or a scoped evidence report. Record the task success condition and the present failure or overhead. Start with a concise plain-language baseline; include a simple structured-English format as a comparator when it may solve the problem more cheaply. Do not invent a communication ceiling or make production work artificially harder. If the experiment needs a test budget, propose it as an experimental parameter, distinct from the user's actual budget; reuse explicit constraints.

Use fictional or non-sensitive task data. Keep research observations separate from production acceptance and from the user's private conversation content.

## Negotiate and freeze a protocol

Use project-local records, preferably a section of the existing methodology plus a protocol file when the glossary grows. A version should state:

- Purpose, authors, reviewer, status and scope.
- Token meanings, argument types/order, separators, negation and uncertainty rules.
- How to quote literals, escape reserved markers and distinguish data from actions.
- Worked messages with exact plain-language meanings, invalid examples and recovery.
- Version compatibility, superseded versions, and the evidence for adoption.

Use explicit version labels in messages. A receiver acknowledges the supported version before relying on it. Freeze meanings for the task slice; negotiate changes after it, not halfway through an action. New meanings require a new version, a visible change record and renewed receiver agreement. Keep earlier definitions so saved messages remain interpretable.

An illustrative *human-designed* seed, not evidence of an evolved language:

```text
Protocol GLP/1
ri <slice> <artifact> = candidate ready for independent inspection, not accepted
ho <slice> <finding> = acceptance on HOLD for the named finding
ev <claim> <evidence> = evidence pointer for a claim, not a claim that it passed

GLP/1 ri gallery candidate-c7 ; ev C12 evidence/run-4.json
Meaning: Gallery candidate c7 is ready for independent inspection. Claim C12
has evidence at evidence/run-4.json. No acceptance verdict is asserted.
```

References resolve only to authorized project records, not executable commands. Never compress away recipient/target identity, ownership, negative conditions, uncertainty, side-effect boundaries or the distinction between proposed and verified. A terse token cannot create permission. Unknown tokens, mismatched versions, ambiguity or contradictory expansions cause clarification in plain language before dependent action.

## Evaluate before adoption

Let the pair propose candidate conventions and briefly review communication failures after a bounded task slice. Save the proposals, decisions and examples as ordinary task records, not internal reasoning transcripts. Then freeze a candidate and compare it with plain language on matched held-out tasks of comparable difficulty using the same tools and task-success criteria. Avoid training and judging on the same examples.

An independent decoder receives only the frozen protocol and examples, then explains unseen messages, including new compositions, negation, ambiguous or unknown tokens and version changes. A fresh agent should reconstruct the intended task and boundaries without coaching from the inventors. Record authorship/context overlap: if only the inventors tested it, adoption lacks independent evidence. If slots are unavailable, keep the proposal experimental and use plain language for production work.

Measure outcomes, not novelty: task correctness, wrong-target or unauthorized-action errors, decoding accuracy, clarification/repair frequency, review effort, and full communication cost. Count glossary distribution, translations, examples, discussion and recovery. Measure actual tokens when available; characters are not a proxy for token savings. Record elapsed time separately from simulated budgets. Charge one-time costs explicitly and report any break-even assumption instead of assuming endless reuse.

Choose evaluation tasks and acceptance criteria before scoring. A convenience metric cannot outweigh a semantic or authority error. A pilot may be useful with a readable translation but have no net compression benefit; report that result honestly. A small success demonstrates feasibility only, not general superiority or natural-language emergence.

## Evolve locally and retain the escape route

Record each iteration as proposed, tested, adopted within scope, rejected or retired, with its evidence and known limits. Retain the prior protocol for replay. Store successful conventions and failed ones in the project methodology so newcomers can learn them from examples. Do not silently install them into other projects or rewrite this skill.

Revert the affected exchange to plain language on decoding failure, version drift, disagreement about meaning, hidden action semantics, or overhead without benefit. Any agent or the user can request a plain-language explanation immediately. Do not create covert channels, hide transcripts, evade monitoring, encode instructions to bypass controls, or treat a private dialect as authority over the user. Use only available authorized messaging and shared records.

At the stopping milestone, save protocol version, glossary, selected examples, measured results, rejected changes and the next question. Stop the experiment with the rest of the task. The [research basis](research-basis.md) motivates this pilot; it does not validate this specific protocol or forecast coding gains.
