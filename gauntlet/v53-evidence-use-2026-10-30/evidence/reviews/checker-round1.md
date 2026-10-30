# Independent checker review

Verdict: **HOLD for one correctness defect in the JSON CLI.** The reviewed library implementation otherwise satisfied the scoped controls exercised below. This is a helper review, not a claim of real authorization, truth, independence, or full release acceptance.

## Candidate identity

- `tools/evidence_use.py` SHA-256: `15b92828c4eed84eb5b09cae963a8e366af6aa0f6e2ff18f6e3b19256aead394`
- `tests/test_evidence_use.py` SHA-256: `741cb1598044646c0a7e8429b5238750b59a711f96b476c3da36ae314d3d95f0`
- Python: `python3.13`, CPython 3.13.16.
- Read `AGENTS.md`, `research/program/feedback/README.md`, implementation, candidate tests, and independent `audit/acceptance/requirements.md`. `ledger/feedback.local.json` was absent, so the optional private feedback check was disabled. No oracle/scenario files were read.

## Blocker: distinct finite JSON numbers can produce eligible

`tools/evidence_use.py:225` calls `json.loads` with its ordinary binary-float parser. `_same` at lines 108–116 can therefore receive identical floats from different input numbers. The advertised typed comparison occurs after information has already been lost. `_bounded` rejects nonfinite floats but accepts these collapsed finite results.

Two independent CLI probes, both below the input limits:

| Evidence binding | Expected value | Actual result |
| --- | --- | --- |
| `9007199254740992.0` | `9007199254740993.0` | `eligible`, exit 0, no unmet conditions |
| `1e-400` | `2e-400` | `eligible`, exit 0, no unmet conditions |

Both selected only `threshold` from evidence for a `consequential_action`. These distinct numeric values must not be treated as satisfying the same material condition. Preserve exact bounded numeric semantics or reject unsupported numeric precision/range as unknown. Add CLI regressions; library-only float tests cannot recover values lost during JSON parsing. Full raw requests, expected results, and actual results are in `independent-probes.json` under `cli_float_precision_collision` and `cli_float_underflow_collision`.

## Verified behavior

Source inspection and actual probes supported these conclusions:

- Valid controls work for all four use kinds; only selected conditions gate eligibility.
- Changed material rules reject current use while retaining independently supplied historical validity; authorized read-only investigation remains possible.
- A receipt's permission assertion does not fill absent or denied host context observations when the caller selects the context source.
- Missing/null selected values remain unknown; a known mismatch dominates other unknown conditions.
- Structural, strictly typed library equality distinguishes booleans, integers, floats, strings, lists and objects across 196 independent pairings.
- Roots are deduplicated and intersected with supplied verified IDs; copied roots do not increase support; missing verification remains unknown.
- CLI duplicate keys, invalid UTF-8, nonfinite values, deep input, oversized input and trailing data return unknown/exit 2.
- Exercised library calls did not modify inputs and performed no file-open, subprocess-launch or socket call under intercepts. Source inspection found no action execution or model/network interface.

Candidate tests: 18 passed. Independent probes: 223 passed and 2 failed out of 225. The verdict rests on the observed behavior and counterexamples, not the counts.

## Trust and coverage limits

The caller chooses material conditions, sources, expected values and host observations. This helper cannot detect an omitted material condition, a dishonest caller, fabricated IDs, copied observations assigned new IDs, or a caller routing a permission assertion through `evidence`. Its documentation correctly assigns those responsibilities to the trusted host. `can_investigate` reports supplied authorization/read-only flags; it does not grant authority or establish that an actual investigation is harmless. No end-to-end host integration, actual external effect, runtime enforcement, model execution, general release acceptance, or real-world source independence was tested.

## Actual commands

Working directory: `.`.

```sh
python3.13 -B -m unittest discover -s tests -p test_evidence_use.py -v
python3.13 -B private:upgrade-workspace/audit/checker-review/independent_probes.py > private:upgrade-workspace/audit/checker-review/independent-probes.json
shasum -a 256 tools/evidence_use.py tests/test_evidence_use.py
```

The first command exited 0. The independent probe command exited 1 because of the two counterexamples. All created files belong to `audit/checker-review/`; implementation and candidate tests were not edited.
