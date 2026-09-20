# Independent grader review, 2026-09-20

A reviewer separate from the fixture author inspected all six public contracts, hidden assertions and reference implementations without reading running candidates or model outputs. All 24 seeded good/bad suite expectations were reproduced. Each inspected hidden assertion follows its public requirements. Of 24 additional contract-derived probes against the references, 23 passed.

One coverage gap is known before interpreting this pilot: c002's reference fails to match two equal finite amount strings `1000000000000000000000000000000` with empty names. Decimal's default precision causes its quantization to raise; the implementation treats that as invalid data despite the contract having no magnitude ceiling. The frozen hidden suite does not cover this boundary.

This is an imperfection in the reference and coverage, not an incorrect existing expected assertion. The running pilot's fixtures are unchanged. Passing the frozen tests must not be described as proving the complete public contract. The reference is known to pass this finite suite, not known correct for every permitted input. A future fixture version should correct the reference and add the independently derived large-finite-value check before new runs; affected results must remain distinguishable by fixture hash.

Verdict: suitable for the declared limited apparatus calibration, with this recorded limitation. No general task-distribution claim is supported.

## Post-run error analysis

After all six comparisons completed, equal supplementary probes confirmed additional uncovered boundaries: the c004 reference rejects nonbreaking whitespace although only digits are restricted to ASCII, and the c006 reference raises `RecursionError` on deep dependency chains/cycles. The c004 baseline also overflowed on a 400-digit hour count. Both extra-work branches fixed the overflow and recursion issues; the c004 self-check introduced the whitespace regression. These cases were selected from final messages and patch inspection after the run, unlike the earlier independent c002 probe. They do not alter frozen scores. See the [decision](DECISION.md) and its linked reproducible evidence. The existing frozen assertions remain valid examples, but the references must not be called fully correct implementations.
