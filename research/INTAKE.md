# Research intake: how a new paper becomes (or does not become) a skill change

Papers arrive faster than versions should. This is the fixed path from "interesting abstract" to "adopted rule", so that a session months from now can process a batch of papers the same way the v5 run did, with the same evidence standard and without touching the installed skill.

## 1. Where things go

| Stage | Location | Who may write it |
| --- | --- | --- |
| Raw scan text as supplied (a feed summary, a pasted digest) | `research/source-notes-<date>.txt` | anyone; never published; never treated as findings |
| One note per paper | `research/scans/<date>/NN-<slug>.md` from `research/scans/TEMPLATE.md` | the lead of an intake session |
| Proposal | a `candidate` row in `research/program/backlog.md` | the lead |
| Adopted rule | `skill/` on a `codex/` branch through an upgrade run | only an upgrade run with frozen checks and independent critics |
| Source assessment that ships with the skill | `skill/references/research-basis.md`, one bullet per source with its limits | the upgrade run |

## 2. The note, and the three rules that keep it honest

Fetch the arXiv abstract page (or the publisher page) and record the abstract verbatim in a quote block. The v5 fidelity critic re-fetched every abstract and compared character by character; write the note so that check passes. Three rules:

1. Verbatim means verbatim. Expand a broken macro only with an annotation line above the block. Every number the note attributes to the paper must appear in the abstract as written, unrounded.
2. Check the supplied scan against the abstract line by line in a table (claim, abstract wording, status). Feeds paraphrase; some paraphrases are wrong in ways that matter (the v5 scan's "ICML" was the method's acronym, not the conference).
3. Label every inference beyond the abstract as ASSUMPTION. "Only the abstract was read" is a limit stated in every note until someone reads the full text (backlog B-011 is the standing item for that).

Then the judgment, in this order: what the abstract does not establish; where the current skill already stands (quote the current version's sentences); the gap; the proposed change as a bounded rule with a gate; the observation that would falsify the design choice; the verdict `adopt | adapt | reject | defer` with the reason. Adapt is the usual verdict: the papers are about their domains, the skill is a workflow, and the transfer is the skill's inference, never the paper's claim.

## 3. From note to rule

- A note produces at most one backlog row: kind `skill change (N.M candidate)`, source = the note, gate = what must be true before it is worth a run. Batch rows into a version; one paper per version is churn.
- An upgrade run adopts rows the same way v5 was made: new `codex/` branch, snapshot `skill/` under `versions/vN/`, freeze the checks first (reuse `gauntlet/v5-upgrade-2026-09-17/contract.yaml` and `probes.md` as templates: one scenario probe per adopted paper, the incumbent as the bar, size limits, fidelity, consistency, compatibility, prompt-mode forward check), build, dispatch independent critics with distinct lenses, apply the evidence ladder to the run itself, rejudge affected checks after every revision, build the release, write provenance and the `UPGRADES.md` entry. The v5 run used six reviews in three rounds; budget the same.
- What never enters `skill/`: a number from a paper stated as a fact about this workflow; a vendor or model ranking; a mechanism without a gate that references verifiability; a rule without a stated falsifier in the research basis; any text that fails `tools/validate_package.py` (size limits, forbidden personal patterns).
- What never happens in an intake session: editing the installed copy, editing `skill/` on `main`, or running a benchmark because a paper suggests one. Benchmarks are the program's phase 2 and have their own protocol.

## 4. Cadence and budget

Read abstracts in batches; read full papers only for rows that reach `drafted`. A batch of six abstracts, notes, and judgments cost the v5 run about an hour of lead time and one fidelity review; an upgrade run on top cost two more hours and five reviews. The entrypoint has 11 bytes of headroom under its 16,000-byte limit, so every adopted rule now displaces words; that pressure is intended.

## 5. Signals worth a note, and signals to skip

Worth a note: a paper that isolates one mechanism the skill uses (a supervisor, a topology choice, memory, checkpoints, dispatch order) and measures what it costs or when it pays. Skip: architecture surveys, framework comparisons that vary everything at once, serving and infrastructure results with no workflow-level lever (PipeSwift earned one sentence, not a rule), and anything whose only transferable content is "more of X helps" without a condition.
