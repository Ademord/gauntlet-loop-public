# Managed-agent readiness

Current scope: assess the execution boundary and investigate possible missing capabilities. There is no new worker launcher or autonomous experimentation in this increment. The existing observer and usage parser remain the recording layer.

The pieces in a managed setup have distinct jobs:

| Piece | Responsibility |
| --- | --- |
| Session | Ordinary task, starting files, current attempt and artifacts |
| Host adapter / harness | Start the chosen agent with explicit tools, model, limits and recording |
| Tools | Task resources and validation the worker can actually invoke |
| Sandbox | Enforce process, filesystem and network boundaries for commands and descendants |
| Orchestration | Choose assignments, feedback and stopping; preserve independent acceptance |

P001 had recording and restricted file tools, but no worker-accessible execution. Its failure does not establish which orchestration mechanism would help. The [readiness record](../research/program/readiness/P001-triage.json) maps its gaps to existing milestones before adding features.

## Check the boundary before supplying execution

Copy [the profile example](../tools/managed-profile.example.json) to a private `*.local.json` file and set the installed executable paths. Use a private output directory:

```text
python tools/managed_agents.py doctor --profile tools/managed-profile.local.json --output tmp/managed-qualification
```

The command runs no model. It creates disposable canaries and tests a native Windows profile for workspace read/write, reads/writes outside it, explicit controller-file denial, a loopback connection and direct external TCP. The external endpoint receives no application data; a working parent connection is required before a child denial counts. Missing files, timeouts and failed launches are not accepted as isolation. Reports include executable/tool/profile hashes and remain private because they contain machine paths.

The tool preserves failures, never retries unsandboxed and never edits global configuration. Exit 3 means the requested boundary did not pass. Even passing these finite probes does not authorize dispatch: descendant cancellation, worker validation, host/observer integration and resource limits still need qualification. The command is deliberately a diagnostic, not a general sandbox security certification.

The native CLI and its policy are reused rather than implementing a security kernel. [OpenAI documents native Windows sandboxing](https://learn.chatgpt.com/docs/windows/windows-sandbox) and [permission profiles](https://learn.chatgpt.com/docs/permissions). [Claude's Bash sandbox documentation](https://code.claude.com/docs/en/sandboxing) currently directs Windows users to WSL2; its file-tool permission controls are a separate boundary. Check actual installed behavior before choosing a backend.

## Current result and next action

[MAQ-001](../research/program/readiness/MAQ-001.json) is blocked. In the reusable tool's native run, the workspace remained usable, the explicit controller canary and outside writes were denied, and direct external TCP was denied. A sibling-file read and a loopback connection succeeded. Earlier exploratory probes also differed on the sibling read, so a favorable single canary would have overstated isolation.

Do not expose arbitrary candidate-code execution under this proposed policy yet. Investigate the observed read/loopback behavior or qualify another supported backend. WSL was absent on the inspected machine; no OS feature was installed. A narrower trusted static-validator tool is another possible engineering step, but it must be identified as such and must not be advertised as arbitrary test execution.

After the boundary is qualified, the smallest useful integration is one named validation capability with working dependencies, immutable controller configuration, bounded process cleanup and the existing observer. Browser/account tools and deployment remain separate capabilities. Another paid task can follow that readiness work; a performance comparison additionally requires a stable configuration and a competent equally equipped baseline.
