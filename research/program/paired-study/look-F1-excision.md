# Paired study, flag F1-excision: look at 8 pairs

Generated 2026-09-19 14:02 UTC by `tools/paired_study/report_pairs.py` from `results.jsonl`. Arm A is the light topology (one bounded build, one independent evidence-based review, no preference loop); arm B is compact (build, independent critic, revise). Everything else about the two arms is identical, including the model. Acceptance is an independent rerun of the suite after the protected tests are restored, with no file changed outside the allowed paths.

- Counted pairs: 8. Pilot rows excluded: 0. Harness-failure rows excluded: 0.

## Per task

| Task | A accepted | B accepted | held-out A/B | reviews A/B | turns A/B | tokens A/B | cost A/B | seconds A/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x001-intelligence-pipeline-process_source | yes | yes | not applicable/not applicable | 1/1 | 20/38 | 1,807,163/3,668,597 | $0.93/$1.29 | 233/247 |
| x002-intelligence-vlm-__init__ | yes | yes | not applicable/not applicable | 1/1 | 41/34 | 3,110,652/3,182,151 | $1.13/$1.09 | 197/175 |
| x003-intelligence-evaluate-values_match | yes | yes | not applicable/not applicable | 1/1 | 18/29 | 1,560,885/2,606,022 | $0.65/$0.90 | 136/212 |
| x004-intelligence-validation-_check_line_items | yes | yes | not applicable/not applicable | 0/1 | 22/46 | 1,904,416/4,469,014 | $0.61/$1.51 | 158/250 |
| x005-intelligence-validation-_check_formats | yes | yes | not applicable/not applicable | 1/1 | 24/40 | 2,161,198/3,823,864 | $0.78/$1.24 | 138/298 |
| x006-intelligence-schema-parse_number | yes | yes | not applicable/not applicable | 1/1 | 29/25 | 2,530,295/2,133,168 | $0.92/$0.72 | 206/136 |
| x007-intelligence-evaluate-match_line_items | yes | yes | not applicable/not applicable | 1/1 | 10/19 | 979,206/1,700,694 | $1.85/$0.79 | 356/238 |
| x008-intelligence-vlm-call_json | yes | yes | not applicable/not applicable | 1/2 | 31/35 | 2,988,839/3,652,255 | $1.15/$1.68 | 231/384 |

## Totals

| Measure | A, light | B, compact |
| --- | --- | --- |
| solved, suite passes | 8 of 8 | 8 of 8 |
| accepted | 8 of 8 | 8 of 8 |
| median reviews | 1 | 1 |
| median turns | 23 | 34 |
| median tokens | 2,032,807 | 3,417,203 |
| total cost | $8.02 | $9.21 |
| median seconds | 202 | 242 |

Contrast-fired rate, the pre-registered secondary from the third amendment: 1 of 8 pairs had an arm B that used two or more reviews (x008-intelligence-vlm-call_json). Where it is zero, arm B never revised and the flag did not manipulate the revision loop.

## Paired tests

From `analyze_pairs.py`, committed before the first pair ran. The per-look threshold is the alpha split across the planned looks: 0.0167. A difference is reported as detected only below that threshold.

```json
{
  "flag": "F1-excision",
  "pairs": 8,
  "excluded_pairs": [],
  "alpha_per_look": 0.016666666666666666,
  "acceptance": {
    "accepted_A": 8,
    "accepted_B": 8,
    "discordant_A_only": 0,
    "discordant_B_only": 0,
    "p_value": 1.0,
    "significant_at_look": false
  },
  "reviews_used": {
    "pairs_with_values": 8,
    "A_minus_B": {
      "mean": -0.25,
      "ci95": [
        -0.625,
        0.0
      ]
    },
    "sign_test": {
      "n_nonzero": 2,
      "positive": 0,
      "p_value": 0.5
    },
    "significant_at_look": false
  },
  "cost_usd": {
    "pairs_with_values": 8,
    "A_minus_B": {
      "mean": -0.1490937000000001,
      "ci95": [
        -0.4995561000000003,
        0.2587291999999999
      ]
    },
    "sign_test": {
      "n_nonzero": 8,
      "positive": 3,
      "p_value": 0.7265625
    },
    "significant_at_look": false
  },
  "total_tokens": {
    "pairs_with_values": 8,
    "A_minus_B": {
      "mean": -1024138.875,
      "ci95": [
        -1658552.5,
        -411568.5
      ]
    },
    "sign_test": {
      "n_nonzero": 8,
      "positive": 1,
      "p_value": 0.0703125
    },
    "significant_at_look": false
  },
  "wall_clock_s": {
    "pairs_with_values": 8,
    "A_minus_B": {
      "mean": -35.625,
      "ci95": [
        -100.25,
        30.75
      ]
    },
    "sign_test": {
      "n_nonzero": 8,
      "positive": 3,
      "p_value": 0.7265625
    },
    "significant_at_look": false
  },
  "reading": "no difference detected"
}
```

## What this does and does not show

- Tasks are one-token defects and small repairs in one public Python repository, run on one model. Nothing here generalizes to harder work, other languages, or other models.
- Acceptance is binary and every task has a deterministic oracle, so the comparison is about cost and effort far more than about quality.
- The planned first look is thirty pairs; a smaller look is reported for what it is.
- Cost figures are the transcript's own `total_cost_usd`, which is API-equivalent pricing, not what a subscription is billed.
