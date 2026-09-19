# Source 2: Closed-World Resolution Against Tool Hallucination in LLM Agents

| Field | Value |
| --- | --- |
| arXiv | [2609.19425](https://arxiv.org/abs/2609.19425) |
| Title | Closed-World Resolution Against Tool Hallucination in LLM Agents |
| Authors | Laxmipriya Ganesh Iyer |
| Submitted | September 16, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs ; full text (v1 HTML) read the same day |

## Abstract, verbatim

> Tool-augmented large language model (LLM) agents fail in a way no tool-selection or tool-security method addresses: they call tools that do not exist and pass arguments no schema declares. Existing defenses either pick the right tool (selection) or constrain what an agent may do with real tools (gating), both of which presuppose the emitted call refers to a real tool at all. We show this is a structural blind spot: a hallucinated call is by construction not a decision any gate made, so no gate can reject it. This paper is primarily a measurement and benchmark study. We give a five-class taxonomy of tool hallucination (H1-H5) and, as a reference point, the Resolution Rung: a training-free, closed-world resolver (registry membership plus a signature check) whose interest is where it must sit, not what it computes. We prove hallucination defense must precede any causal gate, and characterize the one irreducible residue (borrowed arguments schema-indistinguishable from a valid call). Across ten hosted models under two invocation surfaces we measure 322 genuine hallucinations; fabricated-tool calls concentrate on the unconstrained raw-JSON surface (34 vs. 3), and model scale does not help (a 675B model matches a 7-8B one). We then extend to the Model Context Protocol, where merging several servers into one namespace creates hallucination surfaces a single registry cannot express (a second taxonomy, M1-M5); on the live MCP surface we measure 154 hallucinations, including from frontier models that were clean on the single-registry surface, because collisions and shadowing are structural to the merge. We release the versioned Hallucinated-Tools Benchmark (HTB) so any resolver is comparable across submissions.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| tool-using agents hallucinate tools in a way normal permission systems cannot catch | "a hallucinated call is by construction not a decision any gate made, so no gate can reject it" | matches |
| announced September 18 | arXiv submission date is September 16, 2026 | differs by two days; the scan is giving an announcement date |
| 322 genuine tool hallucinations across ten hosted models, plus 154 more on a live MCP surface | same figures | matches |
| fabricated-tool calls much more common through unconstrained raw JSON than constrained invocation (34 vs. 3) | same figures | matches |
| scaling did not solve it: a 675B model performed similarly to 7-8B models | "model scale does not help (a 675B model matches a 7-8B one)" | matches |
| merging several servers creates namespace collisions and shadowing a single-registry safety system cannot represent | "merging several servers into one namespace creates hallucination surfaces a single registry cannot express ... collisions and shadowing are structural to the merge" | matches |
| the authors separate "is this action allowed?" from "does this tool and schema even exist?", and the resolver must sit before the policy gate | "We prove hallucination defense must precede any causal gate" | matches |

## What the abstract does not establish

- The counts are measurements on the authors' own benchmark under two invocation surfaces. Nothing says what rate a given production agent would show, and 322 is a count, not a rate; the abstract gives no denominator.
- "We prove" refers to an argument about where a resolver must sit, not an empirical result. Whether a resolver reduces downstream harm is not measured here.
- The comparison 34 versus 3 is fabricated-tool calls by surface, not total hallucinations by surface.
- Nothing addresses tools that exist but whose behavior differs from their schema, which is the neighbouring failure.
- ASSUMPTION: "two invocation surfaces" means structured tool-calling against raw JSON emission; the abstract implies it without defining both.

## Full text, read 19 September 2026 (B-026)

Read from the v1 HTML on arxiv.org. Short verbatim quotations; everything else is paraphrase.

### The argument, which is an ordering argument

The paper's real content is not the checker. The authors say so: the mechanism is "intentionally trivial, registry
membership plus a signature type-check", and they "do not claim the check is novel". What they claim is placement.
A gate decides admissibility for tools it exposed, so a call naming a tool that does not exist "is by definition
not something a gate chose to expose"; a contract verifier compares a presented contract against a trusted root,
and a fabricated tool has no contract to compare. Every existing defense reasons about the supply of tools and is
silent about the demand, the calls the model actually emits. Therefore resolution must sit **before** the gate, and
that placement is the contribution.

The taxonomy is five classes: H1 a tool that does not exist, H2 an argument no schema declares or a required one
omitted, H3 a value violating its declared type, H4 a real well-formed call to a tool the gate did not expose this
step, H5 a real tool called with another tool's argument shape. H1 to H3 are adjudicable against the registry
alone. H4 is the gate's job. The residue is the part of H5 that satisfies the target's schema anyway, which is
semantic confusion between two compatible tools and reduces to the tool-selection problem.

Measured: 322 hallucinations across ten hosted models on two invocation surfaces, with fabricated calls
concentrated on the unconstrained raw-JSON surface, 34 against 3. Scale did not help: a 675B model matched a 7 to
8B one. On the Model Context Protocol surface, where several servers merge into one namespace, 154 more, including
from models that were clean on the single-registry surface, because collisions and shadowing are structural to the
merge.

### Why this matters to a gauntlet run more than it looks

The finding transfers as a rule about ordering, not about tools. A gauntlet's critics judge a candidate against a
contract's required checks. Every one of those judgments assumes that what the candidate and the critic refer to
exists: the file path is real, the check id is in the contract, the quoted line is in the cited source, the
"external evidence" was actually retrieved. Nothing in v5 resolves those references before the judging starts, so
a fabricated citation is not something the review rejects; it is something the review never evaluates. That is the
same blind spot, one level up.

The local version of the Resolution Rung is therefore: **before a review round is scored, every reference in the
candidate and in the critic's findings must resolve against a closed registry** (the repository tree, the
contract's check ids, the cited file's actual bytes). An unresolved reference is a deterministic rejection, not a
judgment call, and it costs no model tokens. Backlog row B-031. It is also the deterministic answer to a failure
this owner has already hit in practice: research agents that invent a quotation, or that report "not found" as
"does not exist".

### What does not transfer

- The measurement is about function-calling surfaces, not about prose citations; no number here is evidence about
  how often a critic fabricates a reference.
- The soundness statement holds for a closed registry of typed tools. A repository tree is a closed registry; a
  claim about the outside world is not, and no resolver can adjudicate it.
- The irreducible residue has a local analogue and it is the dangerous one: a citation that resolves to a real
  file and a real line, but does not support the claim made about it. Resolution cannot catch that.

## Where the skill already stands

The execution contract already refuses to let a missing capability be dressed up as an inapplicable one: "A selected check with no evidence is `blocked` with the missing verification stated. Lack of tools is not `not applicable`." Evidence must identify actual inspection, and "The critic independently inspects or reproduces the relevant checks on the reviewed artifact; it does not copy builder status labels." The contract records the harness and the actual model per role when observable.

## The gap

Nothing records which tools a run actually had. A verdict can cite a command, a file, or a URL that never existed, and the record looks the same as one citing a real observation; the reader learns the difference only by re-running. On hosts that merge several tool servers, the same tool name can resolve differently between the builder's session and the critic's, and neither the contract nor the verdict record would show it. The paired-study harness has the same hole: it pins the model but not the tool surface.

## Proposed change (adapted, not copied)

1. Contract: record the tool surface as part of the harness, not just the model. The list of available tool names, and where they came from, at the time the run started.
2. Verdict: an evidence pointer that names a command, path, or URL must resolve when the critic records it. A pointer that does not resolve makes the check `blocked`, never `passed`, and the critic says which pointer failed.
3. Paired study: the arm command already restricts tools to an allowlist and disables plugins and MCP servers. Record the resolved tool list per arm alongside the model, and count refused or unknown-tool attempts in the results row next to permission denials.

## Judgment on adoption

Adopt items 2 and 3 in the next upgrade; item 1 costs one line in the contract and is worth it on hosts with merged tool namespaces. This is a recording and verification change, not a resolver: the skill cannot sit between a model and its runtime, and claiming otherwise would be the same category error the paper describes. Falsifier for item 2: if no unresolvable evidence pointer is ever found across a month of runs, the check is ceremony and can be dropped. Backlog row: B-022.
