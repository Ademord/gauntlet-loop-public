# P007 — form validation and gate freshness

Following [P006](GRAPH-HARDENING.md), inspection reproduced concrete weaknesses in the application pipeline: malformed form records could pass or crash, attachment page counts and names were not verified, and a structurally valid gate could outlive its inputs. This checkpoint repairs those local checks. No application was submitted, no tracker was changed, and prior application evidence was preserved.

Private package **1.3.0 is integrated** and passed **74/74 synthetic regression methods**: 42 prior regressions, 15 new form-audit methods and 17 independent acceptance methods. The previous package failed 14 of those independent methods and passed 3 valid controls; 28 failing subcase assertions belong to those 14 methods. Earlier subset runs are included, not additional trials. Separate current form and delivery checks passed; an already-submitted start was refused with exit code 3. Package hashes and skill validation passed. [Indexed record and installed artifact identities](P007-form-validation.json).

| Boundary | Integrated behavior | Limit |
| --- | --- | --- |
| Form record | Reject malformed/duplicate/nonfinite JSON, invalid field pairs and unsupported attachment records | Field shape does not establish factual accuracy |
| Local attachments | Match filenames, absolute regular-file paths, hashes and actual PDF page counts; reject nested RAV files | No proof of remote upload or employer-specific completeness |
| Gate inputs (G04) | Bind configuration, verdict, manifest, latest H5 record, submitted-job set and gate script; compare before/after execution and at H6 entry points | Covers these specified inputs; no general stage-receipt graph or lock |
| Hard checks | Form failures and stale/missing gate bindings block the tested runner paths despite force | Direct browser calls can still bypass the runner |

Empty attachment lists and blank/scalar field values remain supported. Existing timestamps remain readable; legacy attachment pairs remain rendering-only. Previous valid-path test fixtures contained fake PDF bytes and an unsupported field shape, so those fixtures now use real synthetic PDFs and documented pairs. Gates without the new input binding require regeneration. A completed private form passed read-only verification without changing its bytes.

| Investor question | This checkpoint |
| --- | --- |
| **What exact claim are you testing?** | The tested interfaces reject invalid local form evidence and stale specified gate inputs while valid controls progress. Metric: 74 installed synthetic methods passed; 0 failed or skipped. |
| **Compared with what?** | Package 1.2.0 on the same independent cases. This is an engineering repair, not an agent comparison. |
| **What result would make you stop?** | Do not install if a reproduced invalid state passes, force overrides a hard check, or legitimate work can no longer advance. These are implementation acceptance conditions. |
| **Where did your approach lose?** | The previous checks accepted invalid records and stale decisions; earlier test fixtures masked contract gaps. Old unbound gates must be regenerated. Browser bypass remains open. |
| **What did this really cost?** | Unknown. No additional paid worker experiment ran; controller/reviewer usage, implementation, unsuccessful attempts, evaluation and human time are not fully measured. Earlier costs are not counted again. |
| **What decision does the next expenditure enable?** | Whether the next observed failure justifies an owned browser executor, qualified stage receipts or atomic submission reservation. None is established here. |

G04 is repaired for the listed input bindings. General stage freshness, direct browser authority, raw ledger bypass and atomic submission reservation remain open. Full runtime and managed-agent qualification remain incomplete. No performance gain, cost saving or milestone promotion is claimed. The private implementation and evidence are not reproducible from this public checkout alone; the P006 reports remain unchanged.
