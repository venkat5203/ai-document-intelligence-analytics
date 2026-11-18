"""Load processed demo records into a local SQLite database for SQL practice."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed_documents.csv.gz"
DATABASE = ROOT / "data" / "document_analytics.db"
SCHEMA = ROOT / "sql" / "schema.sql"


def main() -> None:
    if not PROCESSED.exists():
        raise FileNotFoundError("Processed dataset missing. Run: python -m src.run_pipeline")
    frame = pd.read_csv(PROCESSED, compression="infer")
    columns = ["doc_id", "record_date", "category", "region", "supplier_name", "spend", "status", "email", "last_updated", "quality_score", "issue_count", "is_valid"]
    frame = frame[columns].copy()
    frame["is_valid"] = frame["is_valid"].astype(int)

    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DROP TABLE IF EXISTS document_records")
        connection.executescript(SCHEMA.read_text(encoding="utf-8"))
        frame.to_sql("document_records", connection, if_exists="append", index=False)
        count = connection.execute("SELECT COUNT(*) FROM document_records").fetchone()[0]
    print(f"Loaded {count:,} synthetic records into {DATABASE}")


if __name__ == "__main__":
    main()
