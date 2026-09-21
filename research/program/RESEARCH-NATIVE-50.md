# Current native capability and research register

Checked 20 September 2026. This is a targeted primary-source review, not an exhaustive product inventory or an effectiveness replication. The [50-milestone matrix](MILESTONES-50.md) uses the source IDs below. Official pages were opened/read; Codex pages were live-fetched. Claude pages were inspected by the delegated documentation audit. Documentation can change after this date.

## What is being compared

The unit is the configured agent host: model + effort + app/CLI version + tools + permissions + memory + delegation/workflow settings. The fair comparison is a competent native host versus the same host with an explicitly identified Gauntlet addition. A model name alone does not specify that system.

Official sources currently identify **GPT-6 Astra** (`gpt-6-astra`) and **Claude Fable 5.1** (`claude-fable-5-1`). Ultra and ultracode involve orchestration settings, not just a strictly single-agent reasoning budget. A native-only baseline can legitimately use multiple agents. A deliberately single-agent ablation must be labeled as such.

The local executable reports `codex-cli 0.154.0-alpha.6.2`. This verifies the executable's identity, not every setting or capability. Claude's installed local version/configuration was not inspected. The saved calibration controller used Claude CLI; its tests/evidence do not establish native Codex behavior. Neither product documentation nor model availability proves which model or workflow actually ran in a future experiment. Record actual dispatch events and IDs.

If ordinary native work and an explicit self-check arm perform the same intervention, collapse them. Do not pay twice for prompt labels. The earlier three-arm $46 bridge is a ceiling for up to three distinct configurations, conditional on quotes, not an obligation to run duplicate arms. Native checker/reviewer workflows must not be silently removed to make V1 look better.

## Reading checkmarks

- **Research P: established principle.** Reuse a supported evaluation/design practice; no transferred effect size.
- **Research C: conditional/mixed.** Useful in some settings, harmful or uncertain in others.
- **Research E: engineering reuse.** Reuse tools, contracts or deterministic tests; this is not a paper proving business value.
- **Research U: local benefit unproven.** No inspected source closes the exact performance/product claim.
- **Native ✅: documented availability.** It does not mean always enabled, always invoked, correctly implemented in every release, or effective on our task.
- **Native ⚙️: explicit setup/selection required.** A native facility exists but configuration supplies important behavior.
- **Native ◐: partial overlap.** Primitives exist; the exact policy/guarantee is not established.
- **Native ?: not established by this review.** This is not a claim that no such capability exists anywhere.
- **Decision ✅ Reuse: mechanism/adoption decision closed.** A performance claim may remain open.
- **Decision ✅ Verified scope: named local engineering evidence exists.** The scope is stated in the row; it is not broad performance proof.
- **Decision 🟨 Partial / 🧪 Open / ⏸ Defer** retain missing implementation, evidence or a prerequisite.

A capability can be checked as native while its Gauntlet benefit remains unproven. Passing an injected fault set does not imply a population error rate of zero. A fresh reviewer or a schema does not establish truth.

## Codex primary sources

| ID | Source | Supported scope and limit |
| --- | --- | --- |
| C1 | [Models](https://learn.chatgpt.com/docs/models) | Astra is listed. Ultra supports proactive delegation. Availability depends on account/client. Astra's experimental within-task context management is opt-in and initially restricted; it is separate from general memory. |
| C2 | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Current Codex releases enable subagent tools; built-in/custom roles, model/effort assignment, parallel activity, steering and concurrency controls are documented. Triggering depends on requests, instructions and mode. More agents consume additional resources. |
| C3 | [Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) | Explicit managed Git worktrees, handoff, setup scripts and restoration facilities exist. Each spawned subagent is not thereby guaranteed a separate filesystem. Ignored files and shared Git metadata need attention. |
| C4 | [Hooks](https://learn.chatgpt.com/docs/hooks) | Configured/trusted lifecycle handlers can inspect or control supported operations. Event coverage and failure semantics differ; missing MCP connections and some hook errors do not block operations. Post-action hooks cannot undo side effects. |
| C5 | [Best practices](https://learn.chatgpt.com/guides/best-practices) | Testing, review, planning, instructions, skills, resume/fork and automatic compaction are supported workflows. Documentation asks users to supply meaningful checks; adequate verification is not guaranteed by merely invoking the agent. |
| C6 | [Memories](https://learn.chatgpt.com/docs/customization/memories) | Local memory generation/retrieval exists and is off by default. Notes are a recall layer; required policy belongs in durable instructions. This is not validated cross-task lesson transfer. |
| C7 | [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) | Native repository exploration, editing, tools, steering, resume, permissions, review and delegation surfaces exist. This overview does not establish every backend/platform guarantee. |
| C8 | [Code review](https://learn.chatgpt.com/docs/code-review) | Dedicated review reports findings without changing the working tree. App/IDE reviews can remain in the same chat or be detached. A read-only review is not an independent correctness oracle. |
| C9 | [Local Codex CLI probe](#local-codex-cli-probe) | Read-only version/help inspection confirms advertised JSONL events, final-response JSON Schema, resume/fork/review and worktree options. No model call was executed; schema enforcement and detailed usage payloads were not exercised. |

### Local Codex CLI probe

Commands inspected: `codex --version` and `codex exec --help`, 20 September 2026. Version: `codex-cli 0.154.0-alpha.6.2`. Help advertises `--json` for JSONL events and `--output-schema <FILE>` for the model's final response shape. This establishes the declared interface, not a successful execution, factual truth or complete billing ledger. The launcher also printed a home-directory/PATH-alias warning; this was a help/version probe only.

## Claude Code primary sources

| ID | Source | Supported scope and limit |
| --- | --- | --- |
| A1 | [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) | Native context gathering, action, verification and revision loop; tool choice and verification adequacy remain task-dependent. |
| A2 | [Subagents](https://code.claude.com/docs/en/sub-agents) | Built-in/custom agents, tool/model/effort/memory choices and explicit worktree isolation. Fresh-context and history-inheriting forks differ; interactive and print/SDK defaults can differ. |
| A3 | [Dynamic workflows](https://code.claude.com/docs/en/workflows) | Script-controlled orchestration, adversarial review, checker/fix/no-progress loops, saved scripts and replay are native facilities. Opt-in ultracode combines extra-high reasoning with automatic workflows. Pro requires workflow enablement. A word in ordinary print-mode input does not prove activation. |
| A4 | [Agent teams](https://code.claude.com/docs/en/agent-teams) | Experimental peer coordination and messages, disabled by default. Team resumption, shutdown and coordination have documented limits. |
| A5 | [CLI reference](https://code.claude.com/docs/en/cli-reference) | Worktree, resume/fork and print-mode turn/dollar controls. Dollar limits include subagent spend on sufficiently recent versions, but are reactive controls rather than exact prepaid reservations. |
| A6 | [Memory](https://code.claude.com/docs/en/memory) | Automatic memory is default-on; durable instructions and notes are available. Repository memory can be shared across worktrees. Behavioral guidance is not hard enforcement. |
| A7 | [Hooks](https://code.claude.com/docs/en/hooks) | Configurable deterministic/agent checks and completion gates. Repeated Stop blocking eventually yields after eight blocks; handlers have authority/coverage limits. These are facilities, not preinstalled Gauntlet acceptance requirements. |
| A8 | [Checkpointing](https://code.claude.com/docs/en/checkpointing) | Automatic checkpoints/rewind cover tracked file-tool edits, not a complete repository transaction: Bash edits and most subagent edits are outside the capture guarantee. |
| A9 | [Model configuration](https://code.claude.com/docs/en/model-config) | Fable 5.1 alias/effort selection, model overrides, per-role allocation and fallback options. Actual IDs and overrides matter; availability does not establish cost-optimal routing. |
| A10 | [Costs](https://code.claude.com/docs/en/costs) | Local usage/cost estimates and resource-management advice. Provider billing is authoritative; prompt caching differs from validated output/evidence caching. |
| A11 | [Monitoring](https://code.claude.com/docs/en/monitoring-usage) | Optional telemetry and beta detailed tracing. These support an audit but do not automatically supply the study denominator, human time or productivity measure. |
| A12 | [Permissions](https://code.claude.com/docs/en/permissions) | Native tool approval boundaries; separate from filesystem/network sandboxing. Integration-specific approved-artifact binding still needs verification. |
| A13 | [Sandboxing](https://code.claude.com/docs/en/sandboxing) | Native shell sandbox facilities with platform limits. Native Windows is unsupported for this sandbox; WSL2 is supported. Worktree isolation is a different property. |
| A14 | [Claude Fable](https://www.anthropic.com/claude/fable) | Official Fable 5.1 identification; product availability is not a record of this project's actual execution. |

## Research

R1–R11 retain their methods, counterevidence and transfer limits in the [earlier research register](RESEARCH-REUSE-20.md). They are not reinterpreted as proving modern native-host superiority or Gauntlet advantage.

| ID | Primary source | What is reused; what is not |
| --- | --- | --- |
| R12 | [AgentDojo](https://arxiv.org/html/2406.13352v3) | Inspected threat model and defense results: measure authorized-task utility separately from attacker success. Native or added filtering can reject legitimate work or permit abuse through allowed tools. No imported attack rate, universal defense, or proof of action idempotency/approval binding. |
| R13 | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) | Inspected order/verbosity bias and mitigation experiments. Use independent labels and order reversal when relevant; consistency does not establish accuracy. Human-preference agreement is not code correctness. |

## Local engineering evidence

| ID | Source | Exact reusable scope |
| --- | --- | --- |
| E1 | [Calibration decision](calibration/DECISION.md) | Six constructed tasks, three continuation branches; frozen scores at ceiling plus supplementary repairs and a spoil. Not the exact archived V1 run and not a modern native-host comparison. |
| E2 | [Calibration controller](../../tools/paired_study/run_calibration.py) | Frozen stage inputs, branch/protected-grader handling, reservations and event capture. The controller refuses interrupted re-execution rather than implementing complete recovery. |
| E3 | [Controller tests](../../tests/test_calibration.py) and [telemetry tests](../../tests/test_telemetry.py) | Tested branch, identity, accounting and partial-report properties. These do not cover every live concurrent/native-host behavior. |
| E4 | [Grader review](calibration/GRADER-REVIEW.md) | Valid existing assertions alongside independent coverage/reference gaps. |
| E5 | [Measurement replay](paired-study/measurement-replay.md) | Reconciled metered usage and incomplete-report handling. Actual subscription charges and research/human cost remain distinct. |
| E6 | [Version record](../../versions/README.md), [release verifier](../../tools/verify_release.py), [public audit](../../tools/public_audit.py) | Preserved versions, package/link verification and scanning infrastructure. V3's four absent references remain disclosed; package review is not performance evaluation. |

## Economic consequence

Do not translate 50 rows into 50 experiments. One evidence packet can close several readiness checks. Reuse native loops, review/delegation, worktrees, memory and recovery primitives; qualify only the guarantee or benefit being claimed.

No new solver benchmark was dispatched for this expansion. Documentation retrieval, delegated analysis and artifact preparation consumed resources; a complete attributed dollar/human-time ledger is not available, so research cost is **not measured**, not zero. There is no new realized-savings claim.

The previous $46 initial bridge remains a conditional ceiling, not a quote or commitment. Current models may not fit the provisional per-run capacity; scope and prices must be checked before any dispatch. The earlier $18 reduction in proposed screening and $36 deferred confirmation remain reductions/deferral of allocations, not measured net savings.
