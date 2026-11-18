"""Generate synthetic supplier-document records for the portfolio demo.

No real people, companies, emails, or employer data are used.
"""
from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "synthetic_documents.csv.gz"

COMPANIES = [
    "Northstar Systems", "Bluewave Logistics", "Evergreen Components", "Atlas Office Supply",
    "Summit Digital Services", "Cedarstone Manufacturing", "Brightpath Consulting",
    "Silverline Networks", "Oakridge Industrial", "Pioneer Business Solutions",
    "Cloudcrest Technologies", "Meadowbrook Packaging", "Vertex Equipment",
    "Harborlight Services", "Redwood Distribution", "Clearview Analytics",
    "Ironwood Facilities", "Goldenfield Trading", "Westbridge Solutions",
    "Mapleline Industries", "Nimbus Support Partners", "Stonegate Materials",
    "Riverbend Software", "Horizon Procurement", "Keystone Operations",
]
DOMAINS = ["example.com", "sample.org", "demo.net", "mockmail.io", "vendor.test"]
CATEGORIES = ["Invoice", "Supplier Profile", "Contract", "Compliance Form", "Purchase Order"]
REGIONS = ["North", "South", "East", "West", "Central"]
STATUSES = ["Active", "Inactive", "Pending"]


def money(value: float, style: int) -> str:
    if style == 0:
        return f"INR {value:,.2f}"
    if style == 1:
        return f"₹{value:,.0f}"
    if style == 2:
        return f"Rs. {value:,.2f}"
    return f"{value:,.2f}"


def make_document(i: int, rng: random.Random, np_rng: np.random.Generator, base_date: datetime) -> dict:
    supplier = rng.choice(COMPANIES)
    spend = float(np_rng.lognormal(mean=11.3, sigma=0.9))
    spend = round(min(max(spend, 500.0), 8_500_000.0), 2)
    status = rng.choices(STATUSES, weights=[0.72, 0.16, 0.12], k=1)[0]
    domain = rng.choice(DOMAINS)
    slug = "".join(ch.lower() for ch in supplier if ch.isalnum())[:18]
    email = f"{rng.choice(['accounts', 'operations', 'vendor', 'finance'])}@{slug}.{domain.split('.', 1)[-1]}"
    last_updated = (base_date - timedelta(days=rng.randint(0, 680))).date().isoformat()
    category = rng.choice(CATEGORIES)
    region = rng.choice(REGIONS)

    # Add realistic source-data quality issues. These are deliberately synthetic.
    spend_text = money(spend, rng.randrange(4))
    email_text = email
    status_text = status
    if rng.random() < 0.035:
        spend_text = ""
    if rng.random() < 0.045:
        email_text = ""
    elif rng.random() < 0.018:
        email_text = email.replace("@", " at ")
    if rng.random() < 0.025:
        status_text = {"Active": "Actve", "Inactive": "In-active", "Pending": "PENDING "}[status]

    supplier_label = rng.choice(["Supplier Name", "Vendor Name", "Supplier", "Vendor"])
    supplier_text = "" if rng.random() < 0.006 else supplier
    spend_label = rng.choice(["Annual Spend", "Spend", "Contract Value", "Amount"])
    status_label = rng.choice(["Supplier Status", "Status", "Vendor Status"])
    email_label = rng.choice(["Contact Email", "Email", "Supplier Email"])
    date_label = rng.choice(["Last Updated", "Updated On", "Modified Date"])

    lines = [
        f"{supplier_label}: {supplier_text}",
        f"{spend_label}: {spend_text}" if spend_text else f"{spend_label}:",
        f"{status_label}: {status_text}",
        f"{email_label}: {email_text}" if email_text else f"{email_label}:",
        f"{date_label}: {last_updated}",
        f"Document Type: {category}",
        f"Region: {region}",
        f"Reference: DOC-{i:06d}",
    ]
    raw_text = "\n".join(lines)

    return {
        "doc_id": f"DOC-{i:06d}",
        "record_date": (base_date - timedelta(days=rng.randint(0, 680))).date().isoformat(),
        "category": category,
        "region": region,
        "raw_text": raw_text,
    }


def generate(rows: int = 47_000, seed: int = 42, output: Path = OUTPUT) -> Path:
    if rows < 1:
        raise ValueError("rows must be a positive integer")
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    base_date = datetime(2026, 10, 31)
    records = [make_document(i + 1, rng, np_rng, base_date) for i in range(rows)]
    frame = pd.DataFrame.from_records(records)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False, compression="infer")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=47_000, help="Number of synthetic records (default: 47000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="Output CSV or CSV.GZ path")
    args = parser.parse_args()
    path = generate(args.rows, args.seed, args.output)
    print(f"Generated {args.rows:,} synthetic records: {path}")
