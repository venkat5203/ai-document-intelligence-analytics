"""Deterministic extraction and quality checks for synthetic document text."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

FIELD_PATTERNS = {
    "supplier_name": r"(?:Supplier Name|Vendor Name|Supplier|Vendor)[ \t]*:[ \t]*([^\n]+)",
    "spend_raw": r"(?:Annual Spend|Spend|Contract Value|Amount)[ \t]*:[ \t]*(?:INR|USD|Rs\.?|₹)?[ \t]*([\d,]+(?:\.\d{1,2})?)?",
    "status_raw": r"(?:Supplier Status|Vendor Status|Status)[ \t]*:[ \t]*([^\n]*)",
    "email": r"(?:Contact Email|Supplier Email|Email)[ \t]*:[ \t]*([^\n]*)",
    "last_updated": r"(?:Last Updated|Updated On|Modified Date)[ \t]*:[ \t]*([^\n]*)",
    "document_type": r"Document Type[ \t]*:[ \t]*([^\n]+)",
    "region": r"Region[ \t]*:[ \t]*([^\n]+)",
    "reference": r"Reference[ \t]*:[ \t]*([^\n]+)",
}

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")


def _search(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text or "", flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    value = (match.group(1) or "").strip()
    return value or None


def extract_fields(raw_text: str) -> dict[str, Any]:
    """Extract fields from a semi-structured supplier document text sample."""
    text = str(raw_text or "")
    result: dict[str, Any] = {}
    for field, pattern in FIELD_PATTERNS.items():
        result[field] = _search(pattern, text)

    spend = result.pop("spend_raw")
    try:
        result["spend"] = float(spend.replace(",", "")) if spend else None
    except (TypeError, ValueError):
        result["spend"] = None

    status = (result.get("status_raw") or "").strip().lower().replace(" ", "")
    status_map = {
        "active": "Active", "actve": "Active", "inactive": "Inactive",
        "in-active": "Inactive", "pending": "Pending",
    }
    result["status"] = status_map.get(status)
    result.pop("status_raw", None)

    result["supplier_name"] = result.get("supplier_name")
    result["email"] = result.get("email")
    result["email_valid"] = bool(result["email"] and EMAIL_RE.match(result["email"]))
    result["last_updated"] = result.get("last_updated")
    return result


def _date_valid(value: Any) -> bool:
    if not value:
        return False
    try:
        pd.to_datetime(value, errors="raise")
        return True
    except (TypeError, ValueError):
        return False


def process_records(source: pd.DataFrame) -> pd.DataFrame:
    """Extract fields, normalize types, and calculate transparent QA flags."""
    if "raw_text" not in source.columns:
        raise ValueError("Input data must contain a 'raw_text' column")

    extracted = pd.DataFrame([extract_fields(text) for text in source["raw_text"]], index=source.index)
    result = pd.concat([source.copy(), extracted], axis=1)

    result["supplier_present"] = result["supplier_name"].fillna("").str.strip().ne("")
    result["spend_present"] = pd.to_numeric(result["spend"], errors="coerce").notna()
    result["spend_positive"] = pd.to_numeric(result["spend"], errors="coerce").gt(0)
    result["status_valid"] = result["status"].isin(["Active", "Inactive", "Pending"])
    result["email_valid"] = result["email"].fillna("").map(lambda item: bool(EMAIL_RE.match(str(item))))
    result["date_valid"] = result["last_updated"].map(_date_valid)

    flag_columns = ["supplier_present", "spend_present", "spend_positive", "status_valid", "email_valid", "date_valid"]
    result["quality_checks_passed"] = result[flag_columns].sum(axis=1)
    result["quality_score"] = (result["quality_checks_passed"] / len(flag_columns) * 100).round(1)
    result["is_valid"] = result[flag_columns].all(axis=1)
    result["issue_count"] = len(flag_columns) - result["quality_checks_passed"]

    result["record_date"] = pd.to_datetime(result["record_date"], errors="coerce")
    result["last_updated_date"] = pd.to_datetime(result["last_updated"], errors="coerce")
    result["spend"] = pd.to_numeric(result["spend"], errors="coerce")
    return result


def issue_summary(processed: pd.DataFrame) -> pd.Series:
    """Count failing checks; counts may overlap because one record can fail multiple checks."""
    checks = {
        "Missing supplier name": "supplier_present",
        "Missing spend": "spend_present",
        "Non-positive spend": "spend_positive",
        "Invalid status": "status_valid",
        "Missing / invalid email": "email_valid",
        "Invalid last-updated date": "date_valid",
    }
    return pd.Series({label: int((~processed[col]).sum()) for label, col in checks.items()}).sort_values(ascending=False)
