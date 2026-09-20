# Independent grader review, 2026-09-20

A reviewer separate from the fixture author inspected all six public contracts, hidden assertions and reference implementations without reading running candidates or model outputs. All 24 seeded good/bad suite expectations were reproduced. Each inspected hidden assertion follows its public requirements. Of 24 additional contract-derived probes against the references, 23 passed.

One coverage gap is known before interpreting this pilot: c002's reference fails to match two equal finite amount strings `1000000000000000000000000000000` with empty names. Decimal's default precision causes its quantization to raise; the implementation treats that as invalid data despite the contract having no magnitude ceiling. The frozen hidden suite does not cover this boundary.

This is an imperfection in the reference and coverage, not an incorrect existing expected assertion. The running pilot's fixtures are unchanged. Passing the frozen tests must not be described as proving the complete public contract. The reference is known to pass this finite suite, not known correct for every permitted input. A future fixture version should correct the reference and add the independently derived large-finite-value check before new runs; affected results must remain distinguishable by fixture hash.

Verdict: suitable for the declared limited apparatus calibration, with this recorded limitation. No general task-distribution claim is supported.
