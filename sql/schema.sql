-- SQLite-compatible analytical schema for the processed synthetic dataset.
CREATE TABLE IF NOT EXISTS document_records (
    doc_id TEXT PRIMARY KEY,
    record_date TEXT,
    category TEXT,
    region TEXT,
    supplier_name TEXT,
    spend REAL,
    status TEXT,
    email TEXT,
    last_updated TEXT,
    quality_score REAL,
    issue_count INTEGER,
    is_valid INTEGER
);

CREATE INDEX IF NOT EXISTS idx_document_records_date ON document_records(record_date);
CREATE INDEX IF NOT EXISTS idx_document_records_category ON document_records(category);
CREATE INDEX IF NOT EXISTS idx_document_records_region ON document_records(region);
CREATE INDEX IF NOT EXISTS idx_document_records_valid ON document_records(is_valid);
