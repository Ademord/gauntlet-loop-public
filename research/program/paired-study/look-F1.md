# Paired study, flag F1: look at 14 pairs

Generated 2026-09-19 10:55 UTC by `tools/paired_study/report_pairs.py` from `results.jsonl`. Arm A is the light topology (one bounded build, one independent evidence-based review, no preference loop); arm B is compact (build, independent critic, revise). Everything else about the two arms is identical, including the model. Acceptance is an independent rerun of the suite after the protected tests are restored, with no file changed outside the allowed paths.

- Counted pairs: 14. Pilot rows excluded: 2. Harness-failure rows excluded: 2.

## Per task

| Task | A accepted | B accepted | held-out A/B | reviews A/B | turns A/B | tokens A/B | cost A/B | seconds A/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m001-intelligence-schema-L37 | yes | yes | not applicable/not applicable | 1/1 | 18/31 | 1,436,718/2,729,139 | $0.73/$0.98 | 219/272 |
| m002-intelligence-evaluate-L148 | yes | yes | not applicable/not applicable | 1/1 | 27/31 | 2,258,723/2,641,344 | $0.84/$1.28 | 168/234 |
| m003-intelligence-evaluate-L102 | yes | yes | not applicable/not applicable | 1/1 | 10/9 | 878,716/779,612 | $0.81/$0.61 | 221/151 |
| m004-intelligence-evaluate-L97 | yes | yes | not applicable/not applicable | 1/1 | 18/20 | 1,470,442/1,594,079 | $0.77/$0.61 | 147/189 |
| m005-intelligence-schema-L31 | yes | yes | not applicable/not applicable | 1/1 | 22/20 | 1,907,365/1,589,951 | $0.74/$0.59 | 182/186 |
| m006-intelligence-evaluate-L149 | yes | yes | not applicable/not applicable | 1/1 | 26/35 | 2,190,393/2,996,952 | $0.74/$0.98 | 193/237 |
| m007-intelligence-vlm-L59 | yes | yes | not applicable/not applicable | 1/1 | 21/33 | 1,855,531/3,029,591 | $0.70/$1.19 | 229/252 |
| m008-intelligence-evaluate-L45 | yes | yes | not applicable/not applicable | 1/1 | 29/33 | 2,326,531/2,848,363 | $1.06/$1.13 | 280/256 |
| m009-intelligence-schema-L26 | yes | yes | not applicable/not applicable | 1/1 | 25/19 | 2,022,492/1,609,863 | $0.67/$0.81 | 141/165 |
| m010-intelligence-evaluate-L44 | yes | yes | not applicable/not applicable | 1/1 | 7/19 | 698,396/1,644,099 | $1.07/$0.69 | 175/156 |
| m011-intelligence-vlm-L129 | yes | yes | not applicable/not applicable | 1/1 | 17/29 | 1,394,175/2,414,287 | $0.60/$0.86 | 122/171 |
| m012-intelligence-validation-L99 | no | yes | not applicable/not applicable | 1/1 | 20/39 | 1,593,457/3,241,389 | $0.54/$1.39 | 145/273 |
| t001-ip-sum-check-gates-confidence | yes | yes | True/True | 1/1 | 4/24 | 370,803/2,088,846 | $0.90/$0.91 | 142/164 |
| t002-tpm-demo-autoplay-on-entry | yes | yes | not applicable/not applicable | 1/1 | 11/35 | 1,383,415/3,603,770 | $1.49/$1.44 | 379/308 |

## Totals

| Measure | A, light | B, compact |
| --- | --- | --- |
| accepted | 13 of 14 | 14 of 14 |
| median reviews | 1 | 1 |
| median turns | 19 | 30 |
| median tokens | 1,531,950 | 2,527,816 |
| total cost | $11.67 | $13.48 |
| median seconds | 178 | 212 |

## Paired tests

From `analyze_pairs.py`, committed before the first pair ran. The per-look threshold is the alpha split across the planned looks: 0.0167. A difference is reported as detected only below that threshold.

```json
{
  "flag": "F1",
  "pairs": 14,
  "excluded_pairs": [],
  "alpha_per_look": 0.016666666666666666,
  "acceptance": {
    "accepted_A": 13,
    "accepted_B": 14,
    "discordant_A_only": 0,
    "discordant_B_only": 1,
    "p_value": 1.0,
    "significant_at_look": false
  },
  "reviews_used": {
    "pairs_with_values": 14,
    "A_minus_B": {
      "mean": 0.0,
      "ci95": [
        0.0,
        0.0
      ]
    },
    "sign_test": {
      "n_nonzero": 0,
      "positive": 0,
      "p_value": 1.0
    },
    "significant_at_look": false
  },
  "cost_usd": {
    "pairs_with_values": 14,
    "A_minus_B": {
      "mean": -0.1296393357142857,
      "ci95": [
        -0.3010048857142857,
        0.02674634999999995
      ]
    },
    "sign_test": {
      "n_nonzero": 14,
      "positive": 5,
      "p_value": 0.4239501953125
    },
    "significant_at_look": false
  },
  "total_tokens": {
    "pairs_with_values": 14,
    "A_minus_B": {
      "mean": -787437.7142857143,
      "ci95": [
        -1195729.7857142857,
        -384246.9285714286
      ]
    },
    "sign_test": {
      "n_nonzero": 14,
      "positive": 3,
      "p_value": 0.057373046875
    },
    "significant_at_look": false
  },
  "wall_clock_s": {
    "pairs_with_values": 14,
    "A_minus_B": {
      "mean": -19.357142857142858,
      "ci95": [
        -46.857142857142854,
        7.642857142857143
      ]
    },
    "sign_test": {
      "n_nonzero": 14,
      "positive": 4,
      "p_value": 0.1795654296875
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
