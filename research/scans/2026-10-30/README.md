# Research scan, 30 October 2026

Seven version-pinned primary papers were read in full by the release review team, including references and appendices. The notes paraphrase the findings and distinguish the team's workflow inferences from the papers' results. No paper implementation or experiment was reproduced. No improvement to Gauntlet is established by this reading.

The baseline comparison is **Gauntlet 5.2.0**, commit `17161321b3cd1603ae7b5d710e3e85a837331cb8`. The notes assess that incumbent, even if a later release adopts a candidate. A verdict of **adapt** means a bounded candidate with a gate, not an installed rule. Overlapping candidates should be combined rather than counted as separate reasons to add machinery.

| Paper and version | Complete textual coverage | Visual inspection | Disposition |
|---|---|---|---|
| [Humanize](01-humanize.md), 2610.08900v2 | 14 pages; appendices A–B; six figures, two tables read | PDF pages 2–8 and 14 | Already covered: retain bounded independent review; defer a new mechanism |
| [RiseHarness](02-riseharness.md), 2610.27435v1 | 38 pages; appendices A–E; seven figures, seven tables read | PDF pages 3–4, 9–11, 33–37 | Candidate: optional paired harness-diagnosis packet |
| [TRACE](03-trace.md), 2609.33517v1 | 41 pages; appendices A–I; five figures, 17 tables read | All figures; key tables on pages 4, 6–9, 29 and 39 | Candidate: action-scoped resume evidence coverage; existing recovery rules retained |
| [CALM](04-calm.md), 2610.38573v1 | 25 pages; appendices A–B; four figures, 14 tables read | All figures; selected tables on pages 1, 4, 7–8 and 20 | Candidate test of existing history/current-context rules; defer new machinery |
| [OffQuery](05-offquery.md), 2610.01244v1 | 44 pages; appendices A–E; eight figures, 11 tables read | All figures; selected tables on pages 2, 5, 7, 9, 18, 22, 39–41 and 43 | Candidate: retained-state postconditions beside output checks |
| [SciValidityBench](06-scivaliditybench.md), 2610.34767v1 | 25 pages; appendices A–I | PDF pages 7–9; selected figures/tables | Candidate: claim-bound evidence eligibility, shared with resume coverage |
| [More Memory](07-more-memory.md), 2610.27406v1 | 31 pages; appendices A–H | PDF pages 6–7, 10, 27, 29 and 31; selected figures/tables | Candidate: distinguish independent support from a lesson's descendants |

Textual coverage includes figure/table contents; it does not mean every PDF page was visually inspected. [The reading manifest](reading-manifest.json) records public source URLs, versions, source hashes and precise coverage without embedding paper text or private research locations.

The common recommendation is small: preserve existing authority, budget and independent-acceptance rules; sharpen the evidence needed for a particular action or claim; check what state survives a successful output. No mandatory graph, learned gate, permanent curator team, vendor assignment, larger review loop or automatic learning follows from these sources. Any candidate still needs the release's independent checks and stated falsifier. Comparative performance claims require separately authorized evidence, with selection effects, failures and full costs retained.
