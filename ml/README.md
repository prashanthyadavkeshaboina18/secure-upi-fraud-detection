# ML — UPI fraud detection

Everything needed to generate data, train, compare and export the fraud model that the
backend serves. Run every command from this `ml/` folder.

```bash
pip install -r requirements.txt

python -m src.data_generation.build_dataset   # → data/raw/upi_synthetic.csv
python -m src.preprocessing                   # → data/interim/upi_synthetic_clean.csv
python -m src.split                           # → data/processed/*.csv (features + stratified & time splits)
python -m src.train                           # → models/candidates/*.joblib (+ thresholds.json)
python -m src.compare_models                  # → reports/evaluation/*, models/candidates/winner.json
python -m src.export_pipeline                 # → models/pipeline.joblib, feature_list.json, metrics.json, model_card.md
python -m pytest                              # run the tests
```

Optional: `python -m src.train --smote` (SMOTE inside the pipeline, train fold only) and, after
placing the ULB file at `data/raw/creditcard.csv`, `python -m src.train --dataset creditcard`.
Set `ML_N_USERS` / `ML_N_DAYS` / `ML_FRAUD_RATE` env vars for a bigger, smaller or different dataset.

Score one transaction by hand: `python -m src.predict --txn '{...}' --history data/interim/upi_synthetic_clean.csv`

## Rules of the road
* **`data/raw` is never edited.** Cleaning writes to `interim`, features/splits to `processed`.
* **One feature implementation.** `src/feature_engineering.py::build_features` is used for
  training *and* (via `compute_single`) for scoring. `backend/app/services/feature_service.py`
  must be a copy of it (or import it) and read `FEATURE_COLUMNS` from `src/config.py` /
  `models/feature_list.json`. `tests/test_feature_engineering.py` checks batch == single-txn results and that
  no future data leaks into a row — re-run it whenever either side changes.
* **No leakage:** `fraud_type` and ids are never features; SMOTE only runs inside the training pipeline;
  the decision threshold is tuned on a validation slice of train, never on test.
* **Models are picked by criteria, not accuracy:** recall ≥ `MIN_RECALL`, precision ≥ `MIN_PRECISION`,
  then highest PR-AUC (tie-break F1). See `src/compare_models.py`.
* **Notebooks are scratch space.** Anything authoritative lives in `src/`.

## What the backend consumes (copied by `scripts/copy_ml_artifacts.py`)
| File | Use |
|---|---|
| `models/pipeline.joblib` | preprocessor + model; input is a DataFrame with `feature_list.json["features"]` in that order |
| `models/feature_list.json` | column order, input columns, `decision_threshold` |
| `models/metrics.json` | served verbatim by `/api/model/performance` |
| `models/model_card.md` | data, assumptions, limitations |
