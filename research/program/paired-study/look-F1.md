# Paired study, flag F1: look at 30 pairs

Generated 2026-09-19 12:50 UTC by `tools/paired_study/report_pairs.py` from `results.jsonl`. Arm A is the light topology (one bounded build, one independent evidence-based review, no preference loop); arm B is compact (build, independent critic, revise). Everything else about the two arms is identical, including the model. Acceptance is an independent rerun of the suite after the protected tests are restored, with no file changed outside the allowed paths.

- Counted pairs: 30. Pilot rows excluded: 2. Harness-failure rows excluded: 2.

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
| m013-intelligence-pipeline-L35 | yes | yes | not applicable/not applicable | 1/1 | 43/6 | 3,894,667/553,895 | $1.34/$0.64 | 284/156 |
| m014-intelligence-schema-L93 | yes | yes | not applicable/not applicable | 1/1 | 6/18 | 529,633/1,433,081 | $0.81/$0.69 | 222/178 |
| m015-intelligence-vlm-L67 | yes | yes | not applicable/not applicable | 1/1 | 14/8 | 1,080,641/740,023 | $0.55/$0.82 | 102/193 |
| m016-intelligence-evaluate-L68 | yes | yes | not applicable/not applicable | 1/1 | 19/8 | 1,516,744/707,082 | $0.70/$0.77 | 169/132 |
| m017-intelligence-evaluate-L46 | yes | yes | not applicable/not applicable | 1/1 | 25/9 | 2,064,167/880,892 | $0.87/$0.98 | 154/283 |
| m018-intelligence-evaluate-L189 | yes | yes | not applicable/not applicable | 1/1 | 29/26 | 2,477,764/2,177,553 | $0.85/$0.91 | 211/277 |
| m019-intelligence-evaluate-L49 | yes | yes | not applicable/not applicable | 1/1 | 5/27 | 483,729/2,320,881 | $0.94/$1.02 | 209/204 |
| m020-intelligence-vlm-L68 | yes | yes | not applicable/not applicable | 1/1 | 32/27 | 2,666,548/2,236,431 | $1.05/$0.87 | 173/181 |
| m021-intelligence-evaluate-L51 | yes | yes | not applicable/not applicable | 1/1 | 33/32 | 2,877,312/2,792,201 | $1.05/$1.31 | 176/352 |
| m022-intelligence-evaluate-L120 | yes | yes | not applicable/not applicable | 1/1 | 8/24 | 781,921/2,075,629 | $1.08/$0.95 | 230/183 |
| m023-intelligence-vlm-L135 | yes | yes | not applicable/not applicable | 1/1 | 21/10 | 1,764,527/919,536 | $0.66/$0.89 | 176/166 |
| m024-intelligence-schema-L29 | yes | yes | not applicable/not applicable | 1/1 | 8/39 | 717,317/3,243,414 | $0.85/$1.13 | 169/310 |
| m025-intelligence-evaluate-L47 | yes | yes | not applicable/not applicable | 1/1 | 6/20 | 562,567/1,681,327 | $0.81/$0.77 | 146/133 |
| m026-intelligence-evaluate-L200 | yes | yes | not applicable/not applicable | 1/1 | 6/24 | 606,843/2,147,280 | $1.17/$0.81 | 239/159 |
| m027-intelligence-evaluate-L58 | yes | yes | not applicable/not applicable | 1/1 | 25/30 | 2,123,361/2,612,369 | $0.79/$1.10 | 169/216 |
| m028-intelligence-pipeline-L57 | no | yes | not applicable/not applicable | 1/1 | 15/24 | 1,163,136/2,061,703 | $0.44/$0.87 | 88/181 |
| t001-ip-sum-check-gates-confidence | yes | yes | True/True | 1/1 | 4/24 | 370,803/2,088,846 | $0.90/$0.91 | 142/164 |
| t002-tpm-demo-autoplay-on-entry | yes | yes | not applicable/not applicable | 1/1 | 11/35 | 1,383,415/3,603,770 | $1.49/$1.44 | 379/308 |

## Totals

| Measure | A, light | B, compact |
| --- | --- | --- |
| solved, suite passes | 30 of 30 | 30 of 30 |
| accepted | 28 of 30 | 30 of 30 |
| median reviews | 1 | 1 |
| median turns | 18 | 24 |
| median tokens | 1,493,593 | 2,118,063 |
| total cost | $25.63 | $28.03 |
| median seconds | 176 | 188 |

Contrast-fired rate, the pre-registered secondary from the third amendment: 0 of 30 pairs had an arm B that used two or more reviews. Where it is zero, arm B never revised and the flag did not manipulate the revision loop.

## Paired tests

From `analyze_pairs.py`, committed before the first pair ran. The per-look threshold is the alpha split across the planned looks: 0.0167. A difference is reported as detected only below that threshold.

```json
{
  "flag": "F1",
  "pairs": 30,
  "excluded_pairs": [],
  "alpha_per_look": 0.016666666666666666,
  "acceptance": {
    "accepted_A": 28,
    "accepted_B": 30,
    "discordant_A_only": 0,
    "discordant_B_only": 2,
    "p_value": 0.5,
    "significant_at_look": false
  },
  "reviews_used": {
    "pairs_with_values": 30,
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
    "pairs_with_values": 30,
    "A_minus_B": {
      "mean": -0.08006362333333336,
      "ci95": [
        -0.18415004333333337,
        0.026141416666666622
      ]
    },
    "sign_test": {
      "n_nonzero": 30,
      "positive": 11,
      "p_value": 0.20048842206597328
    },
    "significant_at_look": false
  },
  "total_tokens": {
    "pairs_with_values": 30,
    "A_minus_B": {
      "mean": -476551.6,
      "ci95": [
        -881458.4333333333,
        -44210.9
      ]
    },
    "sign_test": {
      "n_nonzero": 30,
      "positive": 11,
      "p_value": 0.20048842206597328
    },
    "significant_at_look": false
  },
  "wall_clock_s": {
    "pairs_with_values": 30,
    "A_minus_B": {
      "mean": -21.933333333333334,
      "ci95": [
        -46.833333333333336,
        2.8666666666666667
      ]
    },
    "sign_test": {
      "n_nonzero": 30,
      "positive": 12,
      "p_value": 0.361594608053565
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
