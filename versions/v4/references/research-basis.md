# Design basis and limits — 12 September 2026

Read for provenance, not during every delivery. V4 integrates the supplied v3, existing local team/delivery guidance, and selected ideas from the user's research notes. Embedded historical requests were treated as source material. Primary sources below were checked for this revision. This is a finished workflow specification; no benchmark establishes that v4 outperforms v3 or any model configuration.

## Feedback and continuity

- **[ExecCritic: Learn to Test, Test to Improve for Coding Agents](https://arxiv.org/html/2609.09133v1)**, September 8, 2026. Supports examining test quality, independent construction, and protecting qualified checks from repair-driven weakening. V4 adapts this to requirement-derived checks and targeted controls when warranted. A test failing on the original implementation does not by itself prove that its expectation is correct.
- **[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)**, November 26, 2025, and **[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)**, March 24, 2026. Motivate explicit progress artifacts, recovery from repository state, separate evaluation, and retained candidate revisions. These are engineering reports with application-specific examples and remaining evaluator limitations, not universal evidence for this skill's defaults.
- **[MAPLE: Memory-Augmented Planning with Language and Evolution](https://arxiv.org/abs/2609.11636)**, September 10, 2026. Retains executable optimization programs, accepted plans, prior updates, and candidate solutions. V4's inference is to anchor continuity in actual artifacts and commitments. This does not establish that every development workflow needs an optimization model.

## Grounded memory

- **[Grounding Agent Memory: Environment-Probing Curation for Enterprise Agents](https://arxiv.org/html/2609.11060v1)**, September 10, 2026. Motivates probing the current environment before accepting reusable memories, with read-only access and explicit scope. Its database/consulting evaluations do not prove coding-workflow gains, and curation uses resources.
- **[Fortunate Recall: Ontology-Driven Memory Lifecycle Management](https://arxiv.org/html/2609.10413v1)**, September 9, 2026. Motivates validity, supersession, and invalidation. V4 uses simple lifecycle metadata instead of importing its domain ontology. The paper does not establish concurrent multi-agent memory correctness.
- **[What Should an Agent Forget? Separating What Is Stored from What Is Used](https://arxiv.org/html/2609.10263v1)**, September 9, 2026. Motivates source retention plus task-conditioned retrieval, including distinct present and historical views. Its question-answering setting is not a validation of this lesson-admission workflow.

## Preparation, coordination, and evolution

- **[Studying Without a Syllabus: Task-Agnostic Environment Preprocessing](https://arxiv.org/html/2609.10824v1)**, submitted September 9, 2026 UTC. Motivates bounded preparation and reusable environment maps. V4 applies this conservatively to task-relevant reconnaissance; it does not replicate an unknown-task study phase. More preparation need not help, and study artifacts can mislead.
- **[ORCH: Organizational Principles Enable Collective Intelligence in Embodied AI](https://arxiv.org/html/2609.11737v1)**, September 10, 2026. Motivates matching parallel and sequential coordination to dependencies. Its wildfire-simulation organization is built before execution; it is not evidence for online automatic hierarchy evolution in software teams.
- **[RobustSGPO: Search-Space Control for Agent Harness Evolution](https://arxiv.org/abs/2609.09646)**, September 9, 2026. Motivates scoped candidate patches, retained snapshots, and explicit rollback in a separate improvement process. V4 does not import its scores, token budget, search schedule, or claim transfer to coding. Benchmarking and empirical promotion of proposed improvements remain separate requested work.

## Packaging and practical choices

The compact entrypoint with conditional references follows the current **[OpenAI skill guidance](https://learn.chatgpt.com/docs/build-skills)** and local skill-creator workflow. The existing skill identifier is preserved. Actual model availability and host capabilities are discovered at use time; speculative vendor rankings and historical routing examples were removed.

Review budgets, the integration reserve, repeated-gap heuristic, evidence identities, ownership rules, and admission statuses are engineering choices. Their purpose and limitations are explicit; they are not research-established optima or enforcement mechanisms. The skill does not install protected test storage, enforce a dollar cap, or provide a memory database.

The supplied notes also discuss language emergence, collective copying, chemistry agents, out-of-scope behavior, and sandbox compression. V4 retains legible optional language procedures, scoped shared-knowledge challenges, external verification, and actual authority boundaries as practical workflow rules. It makes no empirical claim about those additional studies and adds no compression infrastructure or persistent swarm. Broad self-evolution, model rankings, critic calibration campaigns, and benchmark architecture remain deferred.
