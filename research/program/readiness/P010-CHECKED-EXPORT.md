# P010 — checked export in a real caller

The unchanged [P009 receipt guard](P009-EXPORT-CHECKS.md) now runs inside one trusted document-export caller in private package 1.4.0. It checks the actual child result, expected file, requested HTML and options before structural PDF readback and writing a new local destination. Failed attempts retain their raw process evidence. A machine-checked export remains pending visual review.

The integrated graph suite passed **93/93 methods**. [Independent offline qualification](P010-qualification.json) passed **21/21 top-level cases**: one optional-route success, eighteen rejections, one compatibility group and one legacy-route group. The compatibility group contains 17 comparisons, not 17 extra top-level cases. All child processes in that probe were mocked; these suite counts are not combined into a claim of independent trials.

One fresh export then produced a 54,296-byte, one-page PDF with matching receipt, complete source text and unchanged inputs. Root and [independent visual review](P010-visual-acceptance.json) accepted the page. Its 2.6533827-second caller time is one observation, not a speedup. Package hashes matched 39/39 entries, and 38/38 watched historical evidence files stayed unchanged. No implementation repair was requested.

| Investor question | This increment |
| --- | --- |
| Exact claim | The tested caller uses the qualified receipt guard, blocks the specified failures, preserves their evidence and supports one fresh accepted standalone export. |
| Compared with what? | The working P009 guard and existing caller behavior on supported overlap, including HTML/attachment compatibility and the mocked legacy route. No model or timing comparison. |
| Stop condition | Any required invalid case accepted, valid case rejected, old evidence changed, or native route unavailable after one diagnosed retry. At most one repair for an established defect. |
| Losses and limits | Legacy preflight still fails three dependency checks. Screenshots, append and external browser work are outside this route. One fixture does not qualify every layout, crash recovery or general sandboxing. |
| Real cost | No new native worker experiment. Controller, review, preparation, testing and human effort still have unknown total cost. This was not free research. |
| Next expenditure | Audit whole-task cost and acceptance coverage using existing records before funding another comparison. |

The route uses fixed trusted Node code and a fresh Edge context, with page offline, JavaScript disabled, requests blocked and Chromium sandbox enabled. Observed versions were Playwright 1.62.1 and Edge 153.0.4234.32. This is a narrow route qualification on one host, not an OS/network isolation certificate. Full legacy preflight still lacks `pdftotext`, `pdfunite` and Python Playwright. The new route rejects screenshots and append requests explicitly and has no automatic fallback. Its destination filesystem must support exclusive hard links; this does not establish complete crash recovery or concurrency safety.

The private package indexes the route and its trusted local profile in its export guide. Neither this export command nor a matching receipt supplies form-truth validation, upload permission, submission authority or an H6/H7 success record. Every future final PDF still needs content and page review. Earlier [P008 export failures](../architecture/VALIDATED-DRAFTING.md) and [P007 controller boundaries](../architecture/FORM-VALIDATION.md) remain historical evidence.

The next engineering step maps to **M-027, Complete attributable accounting**, and **M-024, Independent acceptance coverage**. Enumerate preparation, worker/controller/reviewer work, retries, tools and human corrections; bind each to existing evidence or an explicit unknown. Keep the total incomplete whenever a required cost is unknown. This does not promote either milestone or authorize another paid comparison.

The [checkpoint record](P010-checked-export.json) binds aggregate results to saved evidence. [Criteria](P010-probe-criteria.json) and [freeze identities](P010-probe-freeze.json) preceded candidate inspection. The portable [offline probe](../../../tools/probes/checked_export_probe.py) uses synthetic data and requires `pypdf`, the reviewed caller/helper files and the original baseline supplied separately. Those private implementations are not bundled here, so this public checkpoint is not a self-contained reproduction of the integration. The public P009 utility remains independently runnable.

Frozen staging names map as follows: `independent/criteria.json` is `P010-probe-criteria.json`; `independent/probe_checked_export.py` is the linked probe. The original contract stays private; its digest remains in the freeze and report. Raw process output, host profiles, inherited template contents and PDF/images are excluded. This checkpoint is recorded locally and has not been published; no performance gain or milestone promotion is established.
