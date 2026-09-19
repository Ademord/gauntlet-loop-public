# 5.1 upgrade, progress

Run `v51-upgrade-2026-09-19`. Contract and probes frozen before building: [contract.yaml](contract.yaml),
[probes.md](probes.md). Governing skill version: 5.0.0. Topology: compact with parallel critics.

## Resume validation record, 19 September 2026

Written before any dispatch, as the execution contract requires.

| Item | State |
| --- | --- |
| Decision | `resume` |
| Contract | frozen this morning, unchanged since; criteria version 1 |
| Base | `skill/` at 5.0.0, SKILL.md 15,989 bytes, 7 references, validator passes with `--version 5.0.0` |
| Snapshot | `versions/v5/` now holds the outgoing package, byte-identical to `skill/` |
| Spent budget | 0 of 24 soft / 30 hard run reviews; nothing dispatched yet |
| Skill or harness change since the contract froze | none to `skill/`. The paired-study harness changed, which this run does not touch |
| Obligations carried in | none |

## The binding constraint

C2 caps `skill/SKILL.md` at 16,000 bytes and it is at 15,989. Every queued row that needs a word in the entrypoint
has to pay for it by tightening existing prose without dropping a rule. Each trim is listed below so a critic can
check it against the 5.0.0 snapshot in `versions/v5/`, and C3 treats an unlisted change as out of scope.

## Rows in scope

| Row | Where it lands |
| --- | --- |
| B-020 restore the bar table, two worked examples, the what-breaks-a-loop list | new `references/bars-and-examples.md`, linked from the bar step and from prompt drafting |
| B-002 task class and features enabled, closed vocabularies | milestone line in the entrypoint, vocabularies in the execution contract, includes in prompt drafting |
| B-009 route precedence and honest repair verdicts | route section of the entrypoint; the repair-verdict half lands only in the execution contract, and the entrypoint verdict step is untouched |
| B-012 prompt template length target against its eleven slots | prompt drafting only |
| B-013 per-piece limits when a small user cap makes soft and hard coincide | execution contract only |

## Log

- **2026-09-19, build round 1 started.** v5 snapshotted to `versions/v5/`. Byte budget measured: 11 free.
- **2026-09-19, build round 1 complete.** Candidate 5.1.0 built. SKILL.md 15,989 to 15,977 bytes.
- **2026-09-19, review round 1 dispatched.** Four critics in parallel, fresh context each: scope and consistency
  (C3, C5), the eight frozen probes (C4), record compatibility (C6), prompt-mode forward check (C7). 4 of 24 soft
  run reviews spent.

## What round 1 changed

| Row | Change | File |
| --- | --- | --- |
| B-020 | New `references/bars-and-examples.md`, 10,110 bytes: the three tests a bar must pass, bars by goal type, two filled prompts, the what-breaks-a-loop list. Restored from v3 and rewritten into v5 vocabulary | new file |
| B-020 | The bar step links it on the words "named, accessible, and comparable" | SKILL.md |
| B-020 | Prompt drafting links it | prompt-drafting.md |
| B-002 | Milestone line now carries task class and features enabled | SKILL.md |
| B-002 | Both closed vocabularies stated, with what to do about a value outside them | execution-contract.md |
| B-002 | Contract fields and the drafting includes both carry the two fields | execution-contract.md, prompt-drafting.md |
| B-009 | "When a message matches two routes, the outer request governs: a prompt about doing work is a draft." | SKILL.md |
| B-009 | How the verdict vocabulary reads in a repair, so `bar` never means the failing original is acceptable | execution-contract.md |
| B-012 | Target decided against measurement: 300 to 500 words filled, the template is 370 words empty, and a rule for what to do when an include will not fit | prompt-drafting.md |
| B-013 | What a coinciding soft and hard limit means: the review in hand is the last for that piece | execution-contract.md |

## Declared beyond restoration

One bullet in the new file is not in the v3 material it restores: *"A loop whose mechanism never fires. If every
first review accepts, the revision loop was never exercised..."*. It is declared here rather than smuggled, and the
scope critic is told to judge it. Its evidence is this repository's own study: across 76 recorded arms of two task
classes, no first critic review has returned a negative verdict. If the critic rejects it as out of scope, it comes
out; the finding stays in the research record either way.

**Ruled and resolved:** the scope critic ruled it out of scope in review round 1, because B-020 says restore what v4
dropped and adding to a restored list is an addition. It was removed in round 2. The list is fourteen items, as v3
had it.

## Trims taken to pay for the additions, each to be checked against `versions/v5/`

SKILL.md had 11 bytes of headroom under the 16,000-byte cap, and the additions cost about 170. Ten trims paid for
them in round 1; an eleventh followed in round 2. **Current state after round 3: trims 2 and 10 were reverted
because the scope critic judged that they damaged their rules, trim 11a was reverted in round 3 for the same
reason, and nine remain, counting trim 11.** Each is listed so a critic can verify that no rule, obligation or caveat was lost:

1. Resume route: dropped "Record a resume validation decision before dispatch", which the recovery section states
   more fully, naming all four decisions.
2. **Reverted in round 2.** "They are deferred in this version; using v5 never requires a benchmark campaign" became "using this skill
   never requires one", folded into the preceding clause.
3. "only when it will save repeated discovery" to "only when it saves repeated discovery".
4. "do not add a permanent roster" to "add no permanent roster".
5. "the task's quality and total retry budget" to "the task's quality and retry budget".
6. "are implied by v5" to "are implied".
7. "only for provenance and limits, not to load a literature review into each run" to "for provenance and limits,
   not as a literature review".
8. "24/30 critic reviews" to "24/30 reviews", the unit being given earlier in the same sentence.
9. "use appropriate source, factual, editorial..." to "use source, factual, editorial...".
10. "An unavailable explicitly assigned model blocks that lane until an authorized fallback is available" to "An
    unavailable assigned model blocks that lane until an authorized fallback exists". **Reverted in round 2.**
11. Round 2, two further trims in the budget sentence, to pay for those reverts: "6/9 critic reviews" to "6/9
    reviews", which made the sentence internally consistent and stands; and (11a) "whichever observable ceiling
    arrives first" to "whichever arrives first", which broadened the tie-break past the observable ceilings and was
    **reverted in round 3**. Round 3 paid for that revert by cutting one word from this run's own new route
    sentence, "a prompt about doing work" to "a prompt about work".

## Deterministic checks, round 1

| Check | Result |
| --- | --- |
| C1 structure | passed: frontmatter valid, name unchanged, version 5.1.0, 14 local links resolve, 3 YAML blocks parse |
| C2 size | passed: SKILL.md 15,977 of 16,000; single-file export 102,171 of the amended 110,000 |
| C8 release | passed: build_release, verify_release (9 package files, zip, portable, 25 version files, links), validate_package, public_audit with zero hard hits |
| C9 records | outstanding: README chronology, versions/README rows, backlog closure, release review |

Amendment A1 raised the export limit to 110,000 with its reason recorded in the contract. It also records that the
5.0.0 export was already 90,333 bytes, above the 90,000 the contract names, because the validator had never been
invoked with `--export`. It is now invoked with it.

## Review round 1: four verdicts, nine blocking findings

| Critic | Verdict | Checks |
| --- | --- | --- |
| scope and consistency | `none` | C3 failed, C5 failed |
| record compatibility | `bar` | C6 failed |
| scenario probes | `ours`, acceptance withheld | C4 failed on P2 and P8; six probes pass, 5.0.0 wins none |
| prompt-mode forward check | `ours` | drafted a compliant 500-word prompt with no placeholder, with three deterministic blockers |

The round found one defect that mattered more than the rest. B-002's obligation was asserted in three places and
carried in none: the include list gained the two fields, and the template and both worked examples did not, while
the new file claimed in writing that the examples "carry every include it lists". A fresh agent drafting from the
package would have emitted exactly the uncomparable prompt B-002 exists to prevent, and the package told it the
opposite. The prompt-mode critic found this from the inside, by drafting; the other two found it by grep.

The second was worse in kind. The two closed vocabularies were invented without checking `ledger/SCHEMA.md`, which
already defines both and says of itself that "backlog B-002 adds this to the skill's own record". The repository's
one real milestone line uses `task_class: "skill"` and `features_enabled: ["evidence_ladder", "parallel_critics"]`,
and the candidate's vocabulary rejected all three values. That is a blend of two contradicting patterns, which this
project's rules forbid; the fix is to pick the one with data written to it.

## Round 2 build

| Finding | Disposition |
| --- | --- |
| B-002 include has no vehicle; false coverage claim | template gained a slot; both examples carry task class, features, model inheritance and the request ceilings; the claim is now true and the counts are re-measured |
| vocabularies collide with the ledger's | adopted the ledger's lists verbatim, underscores included; both documents now say a change belongs in both, in one commit |
| no default for a record without the fields | `unknown` rather than absent, on the package's own convention, stated for records before 5.1.0 |
| the `other` escape was inapplicable to `features_enabled` | escape is now `unknown` for both fields |
| `features_enabled` duplicates topology facts | four values restate the topology; the topology field governs and a contradicting record is invalid |
| trim 2 dropped the deferral | reverted as "still deferred", restoring agreement with research-basis.md |
| trim 10 broadened a blocking rule | reverted verbatim to 5.0.0 |
| the unlisted bullet | removed from the skill; the finding stays in the research record |
| "binary job" against a ternary vocabulary | rewritten to name `none` |
| example 2 dropped the HOLD conjunct and a check status | both restored |
| the failure list was gated out of a stall | the gate now sends a stalled loop to it, and the stall-diagnosis rule links it |
| unsourced "most common failure by far" | replaced with a claim that does not assert a frequency |
| the model-comparison bar row sat on the default path | now says it is only for a comparison the user asked for |
| "Fetchable" against the entrypoint's "accessible" | the heading names both |
| tools/README documented an invocation that now fails | updated to 9 files and the 110,000 export limit |

Paid for in the entrypoint by making the budget sentence's unit consistent rather than asymmetric, which both
critics had flagged, and by cutting one word the same sentence already carried. SKILL.md 15,977 to 15,984 bytes,
16 free. The template now has thirteen fields, not the eleven the frozen contract names; the contract described the
state at freeze time and the row asked for the target to be decided against the slots, which it was, twice.

Deterministic checks after round 2: validator passes at 9 files, 15,984 bytes, export 103,542 of 110,000, 15 local
links, 3 YAML blocks.

## Review round 2: four verdicts

| Critic | Round 1 | Round 2 | State |
| --- | --- | --- | --- |
| record compatibility | `bar`, C6 failed | `ours`, **C6 passed** | closed |
| scope and consistency | `none`, C3 and C5 failed | `none`, C3 passed, **C5 failed on one finding** | open |
| scenario probes | `ours`, C4 failed on P2 and P8 | `ours`, P2 now passes, **P8 still fails** | open |
| prompt-mode forward check | `ours`, three blockers | `ours`, blockers cleared in the template and example 1 | open |

Round 2 fixed the vocabulary collision, and round 2's own fix produced the next finding. Adopting the run ledger's
list verbatim left the skill unable to record two mechanisms it governs, `blinding` and `agent_language`, which
**both worked examples actually use**. Worse, the examples filled the new field wrongly: example 1 declared
`parallel_critics` while its prose ran a single critic, and both omitted `evidence_ladder` while instructing the
ladder. That is review round 1's defect one level down, in the text a fresh agent copies.

## Round 3 build

| Finding | Source | Disposition |
| --- | --- | --- |
| the vocabulary cannot record `blinding` or `agent_language` | prompt-mode | both added, in the skill, `ledger/SCHEMA.md` and `tools/ledger/features.py`, in one commit |
| examples declare features their own prose contradicts | scope, probes | example 1 is `evidence_ladder, delegates, isolation, blinding`; example 2 is `evidence_ladder, delegates, blinding`; both name the topology `compact+delegates` and example 2 gains its topology reason |
| no rule for whether an always-on mechanism is listed | probes | list every mechanism in effect, because the consumer reads omission as off and would compare a run against itself |
| "Four of these values restate the topology" | probes, prompt-mode | the three are named; the count is gone |
| the default-for-absence sentence read as overwriting real values | compatibility | now "where these fields are absent ... read them as `unknown`" |
| one unlisted feature forced the whole list to `unknown` | compatibility | keep the values that fit, leave the unnamed one out, note it |
| a repository-specific maintenance rule shipped in the portable export | probes | rewritten so it addresses whatever store reads the records, not this repository |
| example 2 lacked integrated verification | probes, prompt-mode | added |
| `features_not_enabled` named but produced by nothing | probes | given its own schema row, stating plainly that the ingester does not yet copy it |
| round 2's own new trim broadened a tie-break | probes | reverted |
| the frequency claim survived eleven lines above the one that was fixed | scope | rewritten |
| `none` described as "neither is established", narrower than the rule | scope | now names ties and inadequate evidence |
| two tool files had their line endings flipped | scope, probes | restored to their committed form; the three tool diffs are now 2, 3 and 8 lines instead of whole-file rewrites |
| the export byte limit did not count bytes | probes | the validator reads bytes instead of decoding first, which had undercounted by a byte a line |
| prose in three documents is not a control | compatibility, and its own recommendation | `validate_package.py` now compares all three copies of both vocabularies and fails on drift; tested by removing a value and watching it fail |

## A finding rejected, with reasons

The prompt-mode critic reported as blocking that "two incompatible vocabularies both claim to be 5.1.0" and asked
for a version bump. Rejected. It was comparing the round-1 candidate it had read earlier against the round-2
candidate: 5.1.0 has never been released or installed, and revising a candidate between review rounds is what a
review round is. No record anywhere was written against the round-1 list, which existed for about twenty minutes
inside this run. The underlying rule it invoked is sound and now has a deterministic check behind it.

Two findings are deferred rather than fixed, both recorded in the backlog: a repair whose repository path or test
command the user never supplied has no rule (B-036), and nothing validates the vocabularies at ingest time
(B-037). The prompt-mode critic was asked directly whether the first deferral was honest and said it was, on the
ground that it is a new rule rather than a correction, and that it drafted a compliant prompt twice without it.

One more is deferred with the disagreement recorded: the Resume route no longer repeats "record a resume validation
decision before dispatch", which survives two sentences later in the recovery section and in the drafting
reference. The scope critic called it de-duplication and closed it; the probe critic calls it a deleted rule. At
15,997 of 16,000 bytes there is no room to restore it without dropping something else, so it stays as it is and
the disagreement is on the record.

Deterministic checks after round 3: validator passes with the new vocabulary check, 9 files, SKILL.md 15,997 bytes,
export 105,167 of 110,000, 15 links, 3 YAML blocks; verify_release passes; the audit reports zero hard hits on tree
and history.

## Review round 3: four verdicts, and the two that remained

| Critic | Round 2 | Round 3 |
| --- | --- | --- |
| record compatibility | `ours`, C6 passed | `ours`, **C6 passed**, no blocking findings |
| scope and consistency | `none`, C5 failed | `ours`, **C3 and C5 passed**, no blocking findings |
| scenario probes | `ours`, P2 and P8 failed | `ours`, **P1 to P7 pass**, P8 fails on two record findings |
| prompt-mode forward check | `ours`, three blockers | `ours`, **no blocking findings**, third compliant draft |

Two critics verified the new vocabulary control by perturbation rather than by reading it, each in its own scratch
copy: between them they broke all three copies in both directions, tried the exact hyphen spelling that caused the
round 1 defect, and confirmed it returns to passing when restored. One found a hole I had not seen, that changing a
bullet marker silently disabled the check, and one found the `unknown` sentinel is outside its comparison.

Both critics also corrected their own earlier work unprompted. The compatibility critic disclosed that its round 1
search had used the candidate's hyphenated spellings and therefore could not have matched the underscore list it
was looking for, in a check whose whole subject is spelling, so the divergence was three-way and it had reported
two. The scope critic disclosed that a grep filter had swallowed every Markdown bullet from its round 2 diffs. The
prompt-mode critic withdrew its version-bump finding in full and named its own error: the text difference was
deterministic, the claim built on it was an inference it never checked.

## Round 4 build

| Finding | Disposition |
| --- | --- |
| the deleted resume sentence is a scope change recorded nowhere | amendment A2 names the trade, with the arithmetic: 53 bytes against 3 free, and queues B-038 |
| the ledger vocabulary was extended beyond what B-002 authorized | amendment A2 authorizes it, with the reason and the measurable cost stated |
| `features_enabled` was "a possibly empty list" and also required an always-on value | the contradiction is gone, `evidence_ladder` is named as the always-on one, and `unknown` is writable when a run cannot say |
| example 2 lacked builder-local testing | added, the last of the eight includes to land |
| `none`'s trigger list omitted unresolved conflicting judgments | added |
| the failure list said "assigned model" where the rule says "explicitly assigned" | corrected |
| the trim list said eight remain | nine, counting trim 11 |
| a bullet marker could silently disable the vocabulary check | the parser accepts any bullet marker, and a package declaring 5.1 or later with no parseable row now fails loudly |
| three rounds of an inaccurate coverage claim | replaced with a check: every include has a marker, verified in both examples on every validation |

Both new checks were verified by mutation in a scratch copy, never in the repository: deleting a vocabulary row
fails loudly, changing its bullet marker now parses rather than skipping, and removing one include marker from one
example names that include and that example.

Deterministic checks after round 4: validator passes with both new checks, 9 files, SKILL.md 15,997 bytes, export
105,167 of 110,000, 15 links, 3 YAML blocks; verify_release passes; the audit reports zero hard hits.
