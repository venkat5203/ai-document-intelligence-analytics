from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.generate_synthetic_data import generate
from src.pipeline import issue_summary, process_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate, extract, and validate the synthetic document dataset.")
    parser.add_argument("--rows", type=int, default=47_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source = ROOT / "data" / "synthetic_documents.csv.gz"
    if not source.exists():
        generate(args.rows, args.seed, source)
    raw = pd.read_csv(source, compression="infer")
    processed = process_records(raw)
    processed_path = ROOT / "data" / "processed_documents.csv.gz"
    processed.to_csv(processed_path, index=False, compression="infer")
    issue_summary(processed).rename_axis("issue").reset_index(name="failed_records").to_csv(ROOT / "data" / "quality_summary.csv", index=False)
    metrics = {
        "records": int(len(processed)),
        "valid_records": int(processed["is_valid"].sum()),
        "records_needing_review": int((~processed["is_valid"]).sum()),
        "validation_pass_rate_pct": round(float(processed["is_valid"].mean() * 100), 2),
        "average_quality_score_pct": round(float(processed["quality_score"].mean()), 2),
        "dataset_type": "synthetic",
    }
    (ROOT / "data" / "run_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Processed output: {processed_path}")


if __name__ == "__main__":
    main()
