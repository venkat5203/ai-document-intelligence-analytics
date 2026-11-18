import unittest

import pandas as pd

from src.pipeline import extract_fields, process_records


class ExtractionTests(unittest.TestCase):
    def test_extracts_supplier_fields_and_normalizes_status(self):
        sample = """Vendor Name: Northstar Systems
Amount: INR 1,234,500.00
Vendor Status: Actve
Email: finance@northstar.example
Updated On: 2026-09-14
Document Type: Invoice
Region: South
Reference: DOC-000001"""
        result = extract_fields(sample)
        self.assertEqual(result["supplier_name"], "Northstar Systems")
        self.assertEqual(result["spend"], 1234500.0)
        self.assertEqual(result["status"], "Active")
        self.assertTrue(result["email_valid"])

    def test_empty_required_values_are_flagged(self):
        sample = "Supplier Name: Northstar Systems\nAnnual Spend:\nSupplier Status: Pending\nContact Email:\nLast Updated: 2026-01-02"
        result = process_records(pd.DataFrame({"doc_id": ["DOC-1"], "record_date": ["2026-01-02"], "category": ["Invoice"], "region": ["South"], "raw_text": [sample]}))
        self.assertFalse(bool(result.loc[0, "is_valid"]))
        self.assertGreater(int(result.loc[0, "issue_count"]), 0)


    def test_blank_field_does_not_consume_next_line(self):
        sample = """Supplier Name:
Annual Spend:
Supplier Status: Pending
Contact Email:
Last Updated: 2026-01-02"""
        result = extract_fields(sample)
        self.assertIsNone(result["supplier_name"])
        self.assertIsNone(result["spend"])
        self.assertEqual(result["status"], "Pending")
        self.assertIsNone(result["email"])
        self.assertEqual(result["last_updated"], "2026-01-02")

    def test_rejects_missing_raw_text_column(self):
        with self.assertRaises(ValueError):
            process_records(pd.DataFrame({"doc_id": ["DOC-1"]}))


if __name__ == "__main__":
    unittest.main()
