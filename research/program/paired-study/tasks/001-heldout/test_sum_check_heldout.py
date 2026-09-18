"""Held-out checks for task t001 (paired study). Not shown to the builder; copied into the clone after acceptance.

The intended fix promotes the out-of-band SUM_CHECK to ERROR. An over-broad fix that flags every total, or one
that only special-cases the two pinned examples, fails one of these.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from schema import ExtractedRecord, LineItem  # noqa: E402
from validation import ERROR, validate  # noqa: E402


def _target(**overrides):
    rec = ExtractedRecord(
        source_id="h.pdf", processable=True, is_target_type=True,
        source_name="Helios Consulting AG", reference="HC-9",
        issued_on="2026-02-20", currency="CHF", amount_total=100.0,
        line_items=[LineItem("Advisory", 10.0, 10.0, 100.0)])
    for k, v in overrides.items():
        setattr(rec, k, v)
    return rec


def test_heldout_just_below_band_routes_to_review():
    # ratio 0.99 is outside (0.999, 1.25): must be an ERROR-level SUM_CHECK and LOW confidence
    r = validate(_target(amount_total=99.0))
    assert [f.code for f in r.flags] == ["SUM_CHECK"]
    assert r.flags[0].severity == ERROR
    assert r.confidence == "LOW" and r.needs_review is True


def test_heldout_in_band_gross_total_stays_high():
    # ratio 1.2 is inside the band (tax headroom): no flag, HIGH, no review
    r = validate(_target(amount_total=120.0))
    assert r.flags == []
    assert r.confidence == "HIGH" and r.needs_review is False
