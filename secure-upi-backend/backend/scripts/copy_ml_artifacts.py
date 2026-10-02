"""
Copies the three files the API needs from the ML project into
app/ml_runtime/artifacts/, after ml/src/train.py has produced them.

Run from the backend/ directory:
    python -m scripts.copy_ml_artifacts [path/to/ml/models]
"""
import shutil
import sys
from pathlib import Path

REQUIRED_FILES = ["pipeline.joblib", "feature_list.json", "metrics.json"]


def run(source_dir: str = "../ml/models"):
    source = Path(source_dir)
    destination = Path(__file__).resolve().parents[1] / "app" / "ml_runtime" / "artifacts"
    destination.mkdir(parents=True, exist_ok=True)

    missing = [f for f in REQUIRED_FILES if not (source / f).exists()]
    if missing:
        print(f"Missing from {source}: {', '.join(missing)}")
        print("Run the ML training pipeline first (ml/src/train.py), then retry.")
        sys.exit(1)

    for filename in REQUIRED_FILES:
        shutil.copy(source / filename, destination / filename)
        print(f"Copied {filename} -> {destination}")

    print("Done. Restart the API for it to pick up the new model.")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "../ml/models")
