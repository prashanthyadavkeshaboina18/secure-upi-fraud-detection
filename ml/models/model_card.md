# Model card — UPI fraud detector

**Model:** xgboost  ·  **Trained:** 2026-09-24T18:01:33+00:00  ·  **Threshold:** 0.919

## Data
Synthetic UPI-like transactions (1,500 simulated users, 60 days, target fraud rate
2.0%). Four fraud archetypes are injected — account takeover, social
engineering / collect scams, mule bursts, high-value drains — with deliberate overlap
with genuine behaviour. Real UPI fraud data is not public; the public ULB credit-card set is
used only as an optional benchmark.

## Test performance (held-out 24,051 rows, fraud rate 2.00%)
| Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| 0.725 | 0.582 | 0.646 | 0.960 | 0.685 |

Confusion matrix: TN=23,464  FP=106  FN=201  TP=280.
The winner was chosen by recall/precision floors then PR-AUC — never accuracy.

## How it scores
Input = the 9 transaction fields in `feature_list.json`. Features (`src/feature_engineering.py`)
combine the transaction with the sender's *past* transactions (new payee/device/city, amount vs
personal norm, 1h/24h velocity). The backend must reproduce them exactly.

## Limitations
* Results reflect the simulator's assumptions, not real-world fraud; expect lower performance on real data.
* Cold start: a sender's first transactions have no history, so history features are neutral.
* Not evaluated for fairness across user groups; city/txn-type are the only categorical inputs.
* Threshold was tuned for F1 on validation data; business costs of FP vs FN may justify another.
* Fraud patterns drift — retrain and monitor PR-AUC over time.
